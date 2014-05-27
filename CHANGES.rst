0.2.1
-----

- Fix the RQ_ Proc implementation to take the number of task into account
  that are currently being processed by the workers to prevent accidental
  shutdown mid-processing. Thanks to Jason Lantz for the report and
  initial patch.

0.2
---

- Got rid of d2to1 dependency.
- Added django-pq backend.
- Ported to Python 3.
- Added Tornado contrib handlers.

0.1
---

- Initial release with backends:

  * Celery_
  * HotQueue_
  * Huey_
  * Queues_
  * RQ_

.. _Heroku: http://www.heroku.com/
.. _Celery: http://celeryproject.com/
.. _HotQueue: http://richardhenry.github.com/hotqueue/
.. _Huey: http://huey.readthedocs.org/
.. _Queues: http://queues.googlecode.com/
.. _RQ: http://python-rq.org/
