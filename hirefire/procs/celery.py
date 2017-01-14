from __future__ import absolute_import
from collections import Counter
from itertools import chain
from logging import getLogger

from celery.app import app_or_default

from ..utils import KeyDefaultDict
from . import Proc


logger = getLogger('hirefire')


class CeleryInspector(KeyDefaultDict):
    """
    A defaultdict that manages the celery inspector cache.
    """

    def __init__(self, app, simple_queues=False):
        super(CeleryInspector, self).__init__(self.get_status_task_counts)
        self.app = app
        self.simple_queues = simple_queues
        self.route_queues = None

    @classmethod
    def simple_queues(cls, *args, **kwargs):
        return cls(*args, simple_queues=True, **kwargs)

    def get_route_queues(self):
        """Find the queue to each active routing pair.

        Cache to avoid additional calls to inspect().

        Returns a mapping from (exchange, routing_key) to queue_name.
        """
        if self.route_queues is not None:
            return self.route_queues

        worker_queues = self.inspect['active_queues']
        active_queues = chain.from_iterable(worker_queues.values())

        self.route_queues = {
            (queue['exchange']['name'], queue['routing_key']): queue['name']
            for queue in active_queues
        }
        return self.route_queues

    @property
    def inspect(self):
        """Proxy the inspector.

        Make it easy to get the return value from an inspect method.
        Use it like a dictionary, with the desired method as the key.
        """
        allowed_methods = ['active_queues', 'active', 'reserved', 'scheduled']
        inspect = self.app.control.inspect()

        def get_inspect_value(method):
            if method not in allowed_methods:
                raise KeyError('Method not allowed: {}'.format(method))
            return getattr(inspect, method)() or {}

        return KeyDefaultDict(get_inspect_value)

    def get_queue_fn(self, status):
        """Get a queue identifier function for the given status.

        scheduled tasks have a different layout from reserved and
        active tasks, so we need to look up the queue differently.
        Additionally, if the ``simple_queues`` flag is True, then
        we can shortcut the lookup process and avoid getting
        the route queues.
        """
        if not self.simple_queues:
            route_queues = self.get_route_queues()

        def identify_queue(delivery_info):
            exchange = delivery_info['exchange']
            routing_key = delivery_info['routing_key']
            if self.simple_queues:
                # If the exchange is '', use the routing_key instead
                return exchange or routing_key
            try:
                return route_queues[exchange, routing_key]
            except KeyError:
                msg = 'exchange, routing_key pair not found: {}'.format(
                    (exchange, routing_key))
                logger.warning(msg)
                return None  # Special queue name, not expected to be used

        def get_queue(task):
            if status == 'scheduled':
                return identify_queue(task['request']['delivery_info'])
            return identify_queue(task['delivery_info'])
        return get_queue

    def get_status_task_counts(self, status):
        """Get the tasks on all queues for the given status.

        This is called lazily to avoid running long methods when not needed.
        """
        if status not in ['active', 'reserved', 'scheduled']:
            raise KeyError('Invalid task status: {}'.format(status))

        tasks = chain.from_iterable(self.inspect[status].values())
        queues = map(self.get_queue_fn(status), tasks)

        if status == 'scheduled':
            queues = set(queues)  # Only count each queue once

        return Counter(queues)


class CeleryProc(Proc):
    """
    A proc class for the `Celery <http://celeryproject.org>`_ library.

    :param name: the name of the proc (required)
    :param queues: list of queue names to check (required)
    :param app: the Celery app to check for the queues (optional)
    :type name: str
    :type queues: str or list
    :type app: :class:`~celery.Celery`

    Declarative example::

        from celery import Celery
        from hirefire.procs.celery import CeleryProc

        celery = Celery('myproject', broker='amqp://guest@localhost//')

        class WorkerProc(CeleryProc):
            name = 'worker'
            queues = ['celery']
            app = celery

    Or a simpler variant::

        worker_proc = CeleryProc('worker', queues=['celery'], app=celery)

    In case you use one of the non-standard Celery clients (e.g.
    django-celery) you can leave the ``app`` attribute empty because
    Celery will automatically find the correct Celery app::

        from hirefire.procs.celery import CeleryProc

        class WorkerProc(CeleryProc):
            name = 'worker'
            queues = ['celery']

    Querying the tasks that are on the workers is a more expensive
    process, and if you're sure that you don't need them, then you
    can improve the response time by not looking for some statuses.
    The default statuses that are looked for are ``active``,
    ``reserved``, and ``scheduled``. You can configure to *not*
    look for those by overriding the ``inspect_statuses`` property.
    For example, this proc would not look at any tasks held by
    the workers.

    ::

        class WorkerProc(CeleryProc):
            name = 'worker'
            queues = ['celery']
            inspect_statuses = []

    ``scheduled`` tasks are tasks that have been triggered with an
    ``eta``, the most common example of which is using ``retry``
    on tasks. If you're sure you aren't using these tasks, you can
    skip querying for these tasks.

    ``reserved`` tasks are tasks that have been taken from the queue
    by the main process (coordinator) on the worker dyno, but have
    not yet been given to a worker run. If you've configured Celery
    to only fetch the tasks that it is currently running, then you
    may be able to skip querying for these tasks. See
    http://docs.celeryproject.org/en/latest/userguide/optimizing.html#prefetch-limits
    form more information.

    ``active`` tasks are currently running tasks. If your tasks are
    short-lived enough, then you may not need to look for these tasks.
    If you choose to not look at active tasks, look out for
    ``WorkerLostError`` exceptions.
    See https://github.com/celery/celery/issues/2839 for more information.

    If you have a particular simple case, you can use a shortcut to
    eliminate one inspect call when inspecting statuses. The
    ``active_queues`` inspect call is needed to map ``exchange`` and
    ``routing_key`` back to the celery ``queue`` that it is for. If all
    of your ``queue``, ``exchange``, and ``routing_key`` are the same
    (which is the default in Celery), then you can use the
    ``simple_queues = True`` flag to note that all the queues in the
    proc use the same name for their ``exchange`` and ``routing_key``.
    This defaults to ``False`` for backward compatibility, but if
    your queues are using this simple setup, you're encouraged to use
    it like so:

    ::

        class WorkerProc(CeleryProc):
            name = 'worker'
            queues = ['celery']
            simple_queues = True

    Because of how this is implemented, you will almost certainly
    wish to use this feature on all of your procs, or on none of
    them. This is because both variants have separate caches that
    make separate calls to the inspect methods, so having both
    kinds present will mean that the inspect calls will be run twice.

    """
    #: The name of the proc (required).
    name = None

    #: The list of queues to check (required).
    queues = ['celery']

    #: The Celery app to check for the queues (optional).
    app = None

    #: The Celery task status to check for on workers (optional).
    #: Valid options are 'active', 'reserved', and 'scheduled'.
    inspect_statuses = ['active', 'reserved', 'scheduled']

    #: Whether or not the exchange and routing_key are the same
    #: as the queue name for the queues in this proc.
    #: Default: False.
    simple_queues = False

    def __init__(self, app=None, *args, **kwargs):
        super(CeleryProc, self).__init__(*args, **kwargs)
        if app is not None:
            self.app = app
        self.app = app_or_default(self.app)
        self.connection = self.app.connection()
        self.channel = self.connection.channel()

    def quantity(self, cache=None, **kwargs):
        """
        Returns the aggregated number of tasks of the proc queues.
        """
        if hasattr(self.channel, '_size'):
            # Redis
            return sum(self.channel._size(queue) for queue in self.queues)
        # AMQP
        try:
            from librabbitmq import ChannelError
        except ImportError:
            from amqp.exceptions import ChannelError
        count = 0
        for queue in self.queues:
            try:
                queue = self.channel.queue_declare(queue, passive=True)
            except ChannelError:
                # The requested queue has not been created yet
                pass
            else:
                count += queue.message_count

        if cache is not None and self.inspect_statuses:
            count += self.inspect_count(cache)

        return count

    def inspect_count(self, cache):
        """Use Celery's inspect() methods to see tasks on workers."""
        cache.setdefault('celery_inspect', {
            True: KeyDefaultDict(CeleryInspector.simple_queues),
            False: KeyDefaultDict(CeleryInspector),
        })
        celery_inspect = cache['celery_inspect'][self.simple_queues][self.app]
        return sum(
            celery_inspect[status][queue]
            for status in self.inspect_statuses
            for queue in self.queues
        )
