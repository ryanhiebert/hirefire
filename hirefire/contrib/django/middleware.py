from __future__ import absolute_import
import os
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse

from hirefire.procs import load_procs, dump_procs, HIREFIRE_FOUND


def setting(name, default=None):
    return os.environ.get(name, getattr(settings, name, None)) or default


TOKEN = setting('HIREFIRE_TOKEN', 'development')
PROCS = setting('HIREFIRE_PROCS', [])

if not PROCS:
    raise ImproperlyConfigured('The HireFire Django middleware '
                               'requires at least one proc defined '
                               'in the HIREFIRE_PROCS setting.')


class HireFireMiddleware(object):
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
        The heart of the app, returning a JSON ecoded list
        of proc results.
        """
        payload = dump_procs(self.loaded_procs)
        return HttpResponse(payload, content_type='application/json')

    def process_request(self, request):
        path = request.path

        if self.test_path.match(path):
            return self.test(request)

        elif self.info_path.match(path):
            return self.info(request)
