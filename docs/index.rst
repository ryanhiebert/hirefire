.. include:: ../README.rst

Proc backends
-------------

Two base classes are includes that you can use to implement custom
backends. All the other contributed backends use those base classes,
too.

``hirefire.procs.Proc``
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: hirefire.procs.Proc
   :members:

``hirefire.procs.ClientProc``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: hirefire.procs.ClientProc
   :members:
   :inherited-members:

Contributed backends
^^^^^^^^^^^^^^^^^^^^

See the following API overview of the other supported queuing backends.

.. toctree::
   :maxdepth: 2

   procs

Issues & Feedback
-----------------

For bug reports, feature requests and general feedback, please use the
`Github issue tracker`_.

Thanks
------

Many thanks to the folks at Hirefire_ for building a great tool for
the Heroku ecosystem.

Authors
^^^^^^^

.. include:: ../AUTHORS.rst

Changes
-------

.. include:: ../CHANGES.rst

.. _HireFire: http://hirefire.io/
.. _`Github issue tracker`: https://github.com/jezdez/hirefire/issues
