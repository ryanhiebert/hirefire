from __future__ import absolute_import

from hotqueue import HotQueue

from . import ClientProc


class HotQueueProc(ClientProc):
    """
    A proc class for the `HotQueue
    <http://richardhenry.github.com/hotqueue/>`_ library.

    :param name: the name of the proc (required)
    :param queues: list of queue names to check (required)
    :param connection_params: the connection parameter to use by default
                              (optional)
    :type name: str
    :type queues: str or list
    :type connection_params: dict

    Example::

        from hirefire.procs.hotqueue import HotQueueProc

        class WorkerHotQueueProc(HotQueueProc):
            name = 'worker'
            queues = ['myqueue']
            connection_params = {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
            }

    """
    #: The name of the proc (required).
    name = None

    #: The list of queues to check (required).
    queues = []

    #: The connection parameter to use by default (optional).
    connection_params = {}

    def __init__(self, connection_params=None, *args, **kwargs):
        super(HotQueueProc, self).__init__(*args, **kwargs)
        if connection_params is not None:
            self.connection_params = connection_params

    def client(self, queue):
        """
        Given one of the configured queues returns a
        :class:`hotqueue.HotQueue` instance with the
        :attr:`~hirefire.procs.hotqueue.HotQueueProc.connection_params`.
        """
        if isinstance(queue, HotQueue):
            return queue
        return HotQueue(queue, **self.connection_params)

    def quantity(self. **kwargs):
        """
        Returns the aggregated number of tasks of the proc queues.
        """
        return sum([len(client) for client in self.clients])
