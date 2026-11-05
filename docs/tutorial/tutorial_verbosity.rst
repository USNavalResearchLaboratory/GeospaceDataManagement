.. _tutorial-verb:

Verbosity
---------

:py:mod:`GeospaceDataManagement` uses Python's standard
`logging tools <https://docs.python.org/3/library/logging.html>`_
to control the verbosity of output. By default only logger.warning messages
are shown. For more detailed output you may change the logging level.

.. code:: python

  import logging
  import GeospaceDataMangaement as gdm
  gdm.logger.set_level(logging.INFO)

The logging level will be applied to all
:py:class:`~GeospaceDataManagement._instrument.Instrument` data loaded by
:py:mod:`GeospaceDataMangement`.  If you try to update the logger level after
doing anything with :py:mod:`GeospaceDataManagement` in an interactive session,
it may not work.
