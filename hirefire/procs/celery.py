from __future__ import absolute_import

from celery.app import app_or_default

from . import Proc


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

    """
    #: The name of the proc (required).
    name = None

    #: The list of queues to check (required).
    queues = ['celery']

    #: The Celery app to check for the queues (optional).
    app = None

    def __init__(self, app=None, *args, **kwargs):
        super(CeleryProc, self).__init__(*args, **kwargs)
        if app is not None:
            self.app = app
        self.app = app_or_default(self.app)
        self.connection = self.app.connection()
        self.channel = self.connection.channel()

    def quantity(self):
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
        return count
