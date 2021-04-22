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
.. _Huey: https://huey.readthedocs.io/
.. _Queues: http://queues.googlecode.com/
.. _RQ: http://python-rq.org/
.. _`contribute other backends`: https://github.com/jezdez/hirefire/

Installation
------------

Install the HireFire package with your favorite installer, e.g.:

.. code-block:: bash

  pip install HireFire

Sign up for `HireFire`_ and set the ``HIREFIRE_TOKEN`` environment variable
with the `Heroku CLI`_ as provided on the specific HireFire `application page`_,
e.g.:

.. code-block:: bash

  heroku config:set HIREFIRE_TOKEN=f69f0c0ddebe041248daf187caa6abb3e5d943ca

Now follow the quickstart guide below and don't forget to tweak the
options in the `HireFire management system`_.

For more help see the Hirefire `documentation`_.

.. _`Heroku CLI`: https://devcenter.heroku.com/articles/heroku-command
.. _`HireFire`: http://hirefire.io/
.. _`HireFire management system`: https://manager.hirefire.io/
.. _documentation: http://hirefire.io/documentation/guides/getting-started

Configuration
-------------

The ``hirefire`` Python package currently supports three frameworks:
Django, Tornado, and Flask_. Implementations for other frameworks are planned
but haven't been worked on: Pyramid_ (PasteDeploy), WSGI_ middleware, ..

Feel free to `contribute one`_ if you can't wait.

The following guides imply you have defined at least one
``hirefire.procs.Proc`` subclass defined matching one of the processes in your
Procfile. For each process you want to monitor you have to have one subclass.

For example here is a ``Procfile`` which uses RQ_ for the "worker" proccess::

  web: python manage.py runserver
  worker: DJANGO_SETTINGS_MODULE=mysite.settings rqworker high default low

Define a ``RQProc`` subclass somewhere in your project, e.g.
``mysite/procs.py``, with the appropriate attributes (``name`` and
``queues``)

.. code-block:: python

    from hirefire.procs.rq import RQProc

    class WorkerProc(RQProc):
        name = 'worker'
        queues = ['high', 'default', 'low']

See the procs API documentation if you're using another backend. Now follow
the framework specific guidelines below.

.. _`contribute one`: https://github.com/ryanhiebert/hirefire/
.. _flask: http://flask.pocoo.org/
.. _Pyramid: http://www.pylonsproject.org/
.. _WSGI: http://www.python.org/dev/peps/pep-3333/

Django
^^^^^^

Setting up HireFire support for Django is easy:

#. Add ``'hirefire.contrib.django.middleware.HireFireMiddleware'`` to your
   ``MIDDLEWARE`` setting

   .. code-block:: python

     # Use ``MIDDLEWARE_CLASSES`` prior to Django 1.10
     MIDDLEWARE = [
         'hirefire.contrib.django.middleware.HireFireMiddleware',
         # ...
     ]

   Make sure it's the first item in the list/tuple.

#. Set the ``HIREFIRE_PROCS`` setting to a list of dotted paths to your
   procs. For the above example proc

   .. code-block:: python

     HIREFIRE_PROCS = ['mysite.procs.WorkerProc']

#. Set the ``HIREFIRE_TOKEN`` setting to the token that HireFire
   shows on the specific `application page`_ (optional)

   .. code-block:: python

     HIREFIRE_TOKEN = 'f69f0c0ddebe041248daf187caa6abb3e5d943ca'

   This is only needed if you haven't set the ``HIREFIRE_TOKEN``
   environment variable already (see the installation section how to
   do that on Heroku).

   .. _`application page`: https://manager.hirefire.io/applications

#. Add ``'hirefire.contrib.django.middleware.QueueTimeMiddleware'`` to your
   ``MIDDLEWARE`` setting to enable HireFire's `support`_ for scaling
   according to Heroku request queue times (optional).

   .. code-block:: python

     # Use ``MIDDLEWARE_CLASSES`` prior to Django 1.10
     MIDDLEWARE = [
         'hirefire.contrib.django.middleware.HireFireMiddleware',
         # ...
     ]

   Make sure to place it before any other item in the list/tuple so that
   request queue time is calculated as accurately as possible.

   .. _`support`: https://help.hirefire.io/article/49-logplex-queue-time

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

Tornado
^^^^^^^

Setting up HireFire support for Tornado is also easy:

#. Use ``hirefire.contrib.tornado.handlers.hirefire_handlers`` when defining
   your ``tornado.web.Application`` instance

   .. code-block:: python

     import os
     from hirefire.contrib.tornado.handlers import hirefire_handlers

     application = tornado.web.Application([
         # .. some patterns and handlers
     ] + hirefire_handlers(os.environ['HIREFIRE_TOKEN'],
                           ['mysite.procs.WorkerProc']))

   Make sure to pass a list of dotted paths to the ``hirefire_handlers``
   function.

#. Set the ``HIREFIRE_TOKEN`` environment variable to the token that HireFire
   shows on the specific `application page`_ (optional)

   .. code-block:: bash

     export HIREFIRE_TOKEN='f69f0c0ddebe041248daf187caa6abb3e5d943ca'

   See the installation section above for how to do that on Heroku.

   .. _`application page`: https://manager.hirefire.io/applications

#. Check that the handlers have been correctly setup by opening the
   following URL in a browser::

     http://localhost:8888/hirefire/test

   You should see an empty page with 'HireFire Middleware Found!'.

   You can also have a look at the page that HireFire_ checks to get the
   number of current tasks::

     http://localhost:8888/hirefire/<HIREFIRE_TOKEN>/info

   where ``<HIREFIRE_TOKEN>`` needs to be replaced with your token or
   -- in case you haven't set the token as an environment variable
   -- just use ``development``.

Flask
^^^^^

Setting up HireFire support for Flask is (again!) also easy:

#. The module ``hirefire.contrib.flask.blueprint`` provides a
   ``build_hirefire_blueprint`` factory function that should be called with
   HireFire token and procs as arguments. The result is a blueprint providing
   the hirefire routes and which should be registered inside your app

   .. code-block:: python

     import os
     from flask import Flask
     from hirefire.contrib.flask.blueprint import build_hirefire_blueprint

     app = Flask(__name__)
     bp = build_hirefire_blueprint(os.environ['HIREFIRE_TOKEN'],
                                   ['mysite.procs.WorkerProc'])
     app.register_blueprint(bp)

   Make sure to pass a list of dotted paths to the ``build_hirefire_blueprint``
   function.

#. Set the ``HIREFIRE_TOKEN`` environment variable to the token that HireFire
   shows on the specific `application page`_ (optional)

   .. code-block:: bash

     export HIREFIRE_TOKEN='f69f0c0ddebe041248daf187caa6abb3e5d943ca'

   See the installation section above for how to do that on Heroku.

   .. _`application page`: https://manager.hirefire.io/applications

#. Check that the handlers have been correctly setup by opening the
   following URL in a browser::

     http://localhost:8080/hirefire/test

   You should see an empty page with 'HireFire Middleware Found!'.

   You can also have a look at the page that HireFire_ checks to get the
   number of current tasks::

     http://localhost:8080/hirefire/<HIREFIRE_TOKEN>/info

   where ``<HIREFIRE_TOKEN>`` needs to be replaced with your token or
   -- in case you haven't set the token as an environment variable
   -- just use ``development``.
