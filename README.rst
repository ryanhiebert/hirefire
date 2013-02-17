HireFire
========

This is a Python package for HireFire_ -- The Heroku_ Process Manager:

.. epigraph::

  HireFire has the ability to automatically scale your web and worker
  dynos up and down when necessary. When new jobs are queued in to your
  application's worker queue [..], HireFire will spin up new worker
  dynos to process these jobs. When the queue is empty, HireFire will
  shut down the worker dynos again so you're not paying for idle
  workers.

  HireFire also has the ability to scale your web dynos. When your web
  application experiences heavy traffic during certain times of the day,
  or if you've been featured somewhere, chances are your application's
  backlog might grow to a point that your web application will run
  dramatically slow, or even worse, it might result in a timeout. In
  order to prevent this, HireFire will automatically scale your web
  dynos up when traffic increases to ensure that your application runs
  fast at all times. When traffic decreases, HireFire will spin down
  your web dynos again.

  -- from the HireFire_ frontpage

It supports the following Python queuing systems as backends:

* Celery_
* HotQueue_
* Huey_
* Queues_
* RQ_

Feel free to `contribute other backends`_ if you're using a different
queuing system.

.. _HireFire: http://hirefire.io/
.. _Heroku: http://www.heroku.com/
.. _Celery: http://celeryproject.com/
.. _HotQueue: http://richardhenry.github.com/hotqueue/
.. _Huey: http://huey.readthedocs.org/
.. _Queues: http://queues.googlecode.com/
.. _RQ: http://python-rq.org/
.. _`contribute other backends`: https://github.com/jezdez/hirefire/

.. note::

  This package is currently (02/16/2013) targetting the HireFire
  **beta** version ("`manager.hirefire.io`_") **NOT** the old product
  ("`monitor.hirefireapp.com`_").

  See the `beta support forum`_ to `get started`_ with this improved
  version.

  .. _`beta support forum`: http://hirefireapp.tenderapp.com/kb/beta/credit-card-support
  .. _`get started`: http://support.hirefire.io/kb/beta/getting-started-migrating-adding-applications
  .. _`manager.hirefire.io`: http://manager.hirefire.io/
  .. _`monitor.hirefireapp.com`: https://monitor.hirefireapp.com/

Installation
------------

Install the HireFire package with your favorite installer, e.g.:

.. code-block:: bash

  pip install HireFire

Sign up for the `HireFire (beta)`_ and set the ``HIREFIRE_TOKEN``
environment variable with the `Heroku CLI`_ as provided on the
specific HireFire `application page`_, e.g.:

.. code-block:: bash

  heroku config:set HIREFIRE_TOKEN=f69f0c0ddebe041248daf187caa6abb3e5d943ca

Now follow the quickstart guide below and don't forget to tweak the
options in the `HireFire management system`_.

.. _`Heroku CLI`: https://devcenter.heroku.com/articles/heroku-command
.. _`HireFire (beta)`: https://manager.hirefire.io/
.. _`HireFire management system`: https://manager.hirefire.io/

Configuration
-------------

The ``hirefire`` Python package currently supports only one framework:
Django. Implementations for other frameworks are planned but haven't been
worked on: Flask_, Pyramid_ (PasteDeploy), WSGI_ middleware, ..

Feel free to `contribute one`_ if you can't wait.

.. _`contribute one`: https://github.com/jezdez/hirefire/
.. _flask: http://flask.pocoo.org/
.. _Pyramid: http://www.pylonsproject.org/
.. _WSGI: http://www.python.org/dev/peps/pep-3333/

Django
^^^^^^

Setting up HireFire support for Django is easy:

#. Add ``'hirefire.contrib.django.middleware.HireFireMiddleware' to your
   ``MIDDLEWARE_CLASSES`` setting::

     MIDDLEWARE_CLASSES = [
         'hirefire.contrib.django.middleware.HireFireMiddleware',
         # ...
     ]

   Make sure it's the first item in the list/tuple.

#. Define as many ``hirefire.Proc`` subclasses as you want HireFire to
   monitor. Have a look at your ``Procfile`` file to do it.

   For example here is a ``Procfile`` with the following content
   which uses RQ_ for the worker proccess::

     web: python manage.py runserver
     worker: DJANGO_SETTINGS_MODULE=mysite.settings rqworker high default low

   Define a ``RQProc`` subclass somewhere in your Django project,
   e.g. ``mysite/procs.py``, with the appropriate attributes (``name``
   and ``queues``)::

     from hirefire.procs.rq import RQProc
 
     class WorkerProc(RQProc):
         name = 'worker'
         queues = ['high', 'default', 'low']

   See the procs API documentation if you're using another backend.

#. Set the ``HIREFIRE_PROCS`` setting to a list of dotted paths to your
   procs. For the above example proc::

     HIREFIRE_PROCS = ['mysite.procs.WorkerProc']

#. Set the ``HIREFIRE_TOKEN`` setting to the token that HireFire
   show on the specific `application page`_ (optional)::

     HIREFIRE_TOKEN = 'f69f0c0ddebe041248daf187caa6abb3e5d943ca'

   This is only needed if you haven't set the ``HIREFIRE_TOKEN``
   environment variable already (see above).

   .. _`application page`: https://manager.hirefire.io/applications

#. Check that the middleware has been correctly setup by opening the
   following URL in a browser::
   
     http://localhost:8000/hirefire/test

   You should see an empty page with 'HireFire Middleware Found!'.

   You can also have a look at the page that HireFire_ checks to get the
   number of current tasks::

     http://localhost:8000/hirefire/<HIREFIRE_TOKEN>/info

   where ``<HIREFIRE_TOKEN>`` needs to be replaced with your token or
   -- in case you haven't set the token in your settings or environment
   -- just use ``development``.
