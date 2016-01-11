from __future__ import absolute_import

from huey.backends.redis_backend import RedisQueue, RedisBlockingQueue

from . import ClientProc


class HueyRedisProc(ClientProc):
    """
    A proc class for the redis backend of the
    `Huey <http://huey.readthedocs.org/>`_ library.

    :param name: the name of the proc (required)
    :param queues: list of queue names to check (required)
    :param blocking: whether to use the blocking or non-blocking client
                     (optional)
    :param connection_params: the connection parameter to use by default
                              (optional)
    :type name: str
    :type queues: str or list
    :type blocking: bool
    :type connection_params: dict

    Example::

        from hirefire.procs.huey import HueyRedisProc
        from mysite.config import queue

        class WorkerHueyRedisProc(HueyRedisProc):
            name = 'worker'
            queues = [queue]
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

    #: Whether to use the blocking or non-blocking Redis Huey client
    #: (optional).
    blocking = True

    #: The connection parameter to use by default (optional).
    connection_params = {}

    def __init__(self, connection_params=None,
                 blocking=None, *args, **kwargs):
        super(HueyRedisProc, self).__init__(*args, **kwargs)
        if connection_params is not None:
            self.connection_params = connection_params
        if blocking is not None:
            self.blocking = blocking
        if self.blocking:
            self.client_cls = RedisBlockingQueue
        else:
            self.client_cls = RedisQueue

    def client(self, queue):
        """
        Given one of the configured queues returns a
        :class:`~huey.backends.redis_backend.RedisBlockingQueue` or
        :class:`~huey.backends.redis_backend.RedisQueue` instance
        (depending on the :attr:`~hirefire.procs.huey.HueyRedisProc.blocking`
        attribute) with the
        :attr:`~hirefire.procs.huey.HueyRedisProc.connection_params`.
        """
        if isinstance(queue, RedisQueue):
            return queue
        return self.client_cls(queue, **self.connection_params)

    def quantity(self, **kwargs):
        """
        Returns the aggregated number of tasks of the proc queues.
        """
        return sum([len(client) for client in self.clients])
