from __future__ import absolute_import

import os
import re
from logging import getLogger

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

try:
    # Django >= 1.10
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # Not required for Django <= 1.9, see:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    MiddlewareMixin = object

from hirefire.procs import (
    load_procs, serialize_procs, ProcSerializer, HIREFIRE_FOUND
)


def setting(name, default=None):
    return os.environ.get(name, getattr(settings, name, None)) or default


logger = getLogger('hirefire')

TOKEN = setting('HIREFIRE_TOKEN', 'development')
PROCS = setting('HIREFIRE_PROCS', [])
USE_CONCURRENCY = setting('HIREFIRE_USE_CONCURRENCY', False)

if not PROCS:
    raise ImproperlyConfigured('The HireFire Django middleware '
                               'requires at least one proc defined '
                               'in the HIREFIRE_PROCS setting.')


class DjangoProcSerializer(ProcSerializer):
    """
    Like :class:`ProcSerializer` but ensures close database connections.

    New threads in Django will open a new connection automatically once
    ``django.db`` is imported but they do not close the connection if a
    thread is terminated.
    """

    def __call__(self, args):
        try:
            return super(DjangoProcSerializer, self).__call__(args)
        finally:
            from django.db import close_old_connections
            close_old_connections()


class HireFireMiddleware(MiddlewareMixin):
    """
    The Django middleware that is hardwired to the URL paths
    HireFire requires. Implements the test response and the
    json response that contains the procs data.
    """
    test_path = re.compile(r'^/hirefire/test/?$')
    info_path = re.compile(r'^/hirefire/%s/info/?$' % re.escape(TOKEN))
    loaded_procs = load_procs(*PROCS)

    def test(self, request):
        """
        Doesn't do much except telling the HireFire bot it's installed.
        """
        return HttpResponse(HIREFIRE_FOUND)

    def info(self, request):
        """
        Return JSON response serializing all proc names and quantities.
        """
        data = serialize_procs(
            self.loaded_procs,
            use_concurrency=USE_CONCURRENCY,
            serializer_class=DjangoProcSerializer,
        )
        return JsonResponse(data=data, safe=False)

    def process_request(self, request):
        path = request.path

        if self.test_path.match(path):
            return self.test(request)

        elif self.info_path.match(path):
            return self.info(request)


class QueueTimeMiddleware(MiddlewareMixin):
    """
    The Django middleware that outputs Heroku request queue times to stdout

    The behavior and format for request queue time scaling are described in
    HireFire's docs: https://help.hirefire.io/article/49-logplex-queue-time
    """
    def process_request(self, request):
        """
        Outputs the Heroku request queue time to stdout
        """
        request_start_header_value = request.META.get("HTTP_X_REQUEST_START")
        if request_start_header_value is not None:
            try:
                request_start_timestamp_ms = int(request_start_header_value)
            except ValueError:
                logger.warning(
                    'Received an invalid "X-Request-Start" header value from '
                    'Heroku: "%s"',
                    request_start_header_value,
                )
            else:
                # The timestamp generated by timestamp() is the number of
                # seconds since the Unix epoch, so it needs to be multiplied
                # and truncated as an integer to convert it to milliseconds
                now_timestamp_ms = int(timezone.now().timestamp() * 1000)

                # There may be some clock drift between the Heroku router and
                # the dyno that is running this middleware; if the calculated
                # queue time is negative, treat it as zero instead
                queue_time_ms = (
                    now_timestamp_ms - request_start_timestamp_ms
                    if now_timestamp_ms >= request_start_timestamp_ms
                    else 0
                )

                print("[hirefire:router] queue={}ms".format(queue_time_ms))
