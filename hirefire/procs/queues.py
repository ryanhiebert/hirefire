from __future__ import absolute_import

from . import ClientProc


class QueuesProc(ClientProc):
    """
    A proc class for the `queues <http://queues.googlecode.com/>`_
    library.

    :param name: the name of the proc (required)
    :param queues: list of queue names to check (required)
    :type name: str
    :type queues: str or list of str or :class:`queues.queues.Queue`

    Example::

        from hirefire.procs.queues import QueuesProc

        class WorkerQueuesProc(QueuesProc):
            name = 'worker'
            queues = ['default', 'thumbnails']

    """
    #: The name of the proc (required).
    name = None

    #: The list of queues to check (required).
    queues = []

    def client(self, queue):
        """
        Given one of the configured queues returns a
        :class:`queues.queues.Queue` instance.
        """
        try:
            from queues import queues as _queues
        except ImportError:
            raise ValueError("Couldn't import the queues library.")
        if isinstance(queue, _queues.Queue):
            return queue
        return _queues.Queue(queue)

    def quantity(self, **kwargs):
        """
        Returns the aggregated number of tasks of the proc queues.
        """
        return sum([len(client) for client in self.clients])
