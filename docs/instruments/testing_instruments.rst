.. _instruments-testing:


Test Instruments
----------------

The following Instrument modules support unit and integration testing for
packages that depend on :py:mod:`GeospaceDataManagement`.


gdm_testing
^^^^^^^^^^^
An instrument with satellite-like data as a function of latitude, longitude,
and altitude in a pandas format. See :ref:`api-gdm-testing` for more details.


gdm_ndtesting
^^^^^^^^^^^^^
An instrument with satellite-like data like :py:mod:`gdm_testing` that
also has an imager-like 3D data variable. See :ref:`api-gdm-ndtesting`
for more details.


gdm_testmodel
^^^^^^^^^^^^^
An instrument with model-like data that returns a 4D object as a function of
latitude, longitude, altitude, and time. See :ref:`api-gdm-testmodel` for more
details.
