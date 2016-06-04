Procs
=====

This is a auto-generated list of supported ``Proc`` classes.

Celery
------

.. autoclass:: hirefire.procs.celery.CeleryProc(name=None, queues=['celery'], app=None)
   :members:
   :inherited-members:
   :undoc-members:

HotQueue
--------

.. autoclass:: hirefire.procs.hotqueue.HotQueueProc(name=None, queues=[], connection_params={})
   :members:
   :inherited-members:
   :undoc-members:

Huey
----

.. autoclass:: hirefire.procs.huey.HueyRedisProc(name=None, queues=[], connection_params={}, blocking=True)
   :members:
   :inherited-members:
   :undoc-members:

Queues
------

.. autoclass:: hirefire.procs.queues.QueuesProc(name=None, queues=[])
   :members:
   :inherited-members:
   :undoc-members:

RQ
--

.. autoclass:: hirefire.procs.rq.RQProc(name=None, queues=['default'], connection=None)
   :members:
   :inherited-members:
   :undoc-members:
