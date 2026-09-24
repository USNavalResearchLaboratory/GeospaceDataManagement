.. _api:

API
===


.. _api-instrument:

Instrument
----------

.. autoclass:: GeospaceDataManagement.Instrument
   :members:
   :noindex:

.. _api-files:

Files
-----

.. autoclass:: GeospaceDataManagement.Files
   :members:


.. _api-params:

Parameters
----------

.. autoclass:: GeospaceDataManagement._params.Parameters
   :members:


.. _api-instrument-methods:

Instrument Methods
------------------

The following methods support a variety of actions commonly needed by
GeospaceDataManagement.Instrument modules regardless of the data source.


.. _api-methods-general:

General
^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.methods.general
   :members:


.. _api-methods-testing:

Testing
^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.methods.testing
   :members:


.. _api-utilities:

Utilities
---------
The utilites module contains functions used throughout the
GeospaceDataManagement package. This includes utilities for determining the
available Instruments, loading files, et cetera.


.. _api-utils-core:

Core Utilities
^^^^^^^^^^^^^^
These utilities are available directly from the :py:mod:`GeospaceDataManagement.utils` module.

.. automodule:: GeospaceDataManagement.utils._core
   :members:


.. _api-utils-coords:

Coordinates
^^^^^^^^^^^

.. automodule:: GeospaceDataManagement.utils.coords
   :members:


.. _api-utils-io:

I/O
^^^

.. automodule:: GeospaceDataManagement.utils.io
   :members:


.. _api-utils-files:

Files
^^^^^

.. automodule:: GeospaceDataManagement.utils.files
  :members:


.. _api-utils-meta:

Meta
^^^^

.. automodule:: GeospaceDataManagement.utils.meta
  :members:


.. _api-gdm-registry:

Registry
^^^^^^^^

.. automodule:: GeospaceDataManagement.utils.registry
   :members:


.. _api-utils-time:

Time
^^^^

.. automodule:: GeospaceDataManagement.utils.time
   :members:


.. _api-utils-testing:

Testing
^^^^^^^

.. automodule:: GeospaceDataManagement.utils.testing
   :members:


.. _api-instrument-template:

Instrument Template
-------------------

.. automodule:: GeospaceDataManagement.instruments.templates.template_instrument
   :members: __doc__, init, clean, preprocess, list_files, download, load, list_remote_files


.. _api-geninst:

General Instruments
-------------------

The following Instrument modules support I/O and analysis in
GeospaceDataManagement.


.. _api-gdm-ndtesting:

gdm_ndtesting
^^^^^^^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.gdm_ndtesting
   :members:


.. _api-gdm-netcdf:

gdm_netcdf
^^^^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.gdm_netcdf
   :members:


.. _api-testinst:

Test Instruments
----------------

The following Instrument modules support unit and integration testing for
packages that depend on GeospaceDataManagement.


.. _api-gdm-testing:

gdm_testing
^^^^^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.gdm_testing
   :members:


.. _api-gdm-testmodel:

gdm_testmodel
^^^^^^^^^^^^^

.. automodule:: GeospaceDataManagement.instruments.gdm_testmodel
   :members:
