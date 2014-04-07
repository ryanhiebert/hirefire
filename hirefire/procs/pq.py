from __future__ import absolute_import

from django.db.models.query import QuerySet
from pq.models import Job

from . import ClientProc


class PQProc(ClientProc):
    """
    A proc class for the `django-pq <https://github.com/bretth/django-pq>`_
    app.

    :param name: the name of the proc (required)
    :param queues: list of queue names to check (required)
    :param connection: the connection to use for the queues (optional)
    :type name: str
    :type queues: str or list

    Example::

        from hirefire.procs.pq import PQProc

        class WorkerPQProc(PQProc):
            name = 'worker'
            queues = ['high', 'default', 'low']

    """
    #: The name of the proc (required).
    name = None

    #: The list of queues to check (required).
    queues = ['default']

    def client(self, queue):
        """
        Given one of the configured queues returns a
        :class:`pq.Queue` instance using the
        :attr:`~hirefire.procs.pq.PQProc.connection`.
        """
        if isinstance(queue, QuerySet):
            return queue
        return Job.objects.filter(status=Job.QUEUED, queue__name=queue)

    def quantity(self):
        """
        Returns the aggregated number of job of the proc queues.
        """
        return sum([client.count() for client in self.clients])
