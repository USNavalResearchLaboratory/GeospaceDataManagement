.. _instruments-madrigal:

Madrigal Instruments
====================

These :py:class:`~GeospaceDataManagement._instruments.Instrument` modules are
made available with the 'madrigal' installation option.

DMSP
----

The Defense Meteorological Satellite Program carries many instruments whose
measurements may be obtained from a variety of data bases.  Madrigal currently
maintains two of these instrument data sets.

DMSP_IVM
^^^^^^^^

Supports the DMSP Special Sensor for Electrion, Ions, and Scintilations (SSEIS)
by providing data from the Ion Velocity Meter (IVM).


.. automodule:: GeospaceDataManagement.instruments.dmsp_ivm
   :members:

DMSP_SSJ
^^^^^^^^

Supports the Defense Meteorological Satellite Program (DMSP) Special Sensor J
(SSJ) Madrigal data.


.. automodule:: GeospaceDataManagement.instruments.dmsp_ssj
   :members:

GNSS_TEC
--------

The Global Navigation Satellite System (GNSS) Total Electron Content (TEC)
provides a measure of column plasma density over the globle.  The Madrigal
TEC is provided by MIT Haystack.

.. automodule:: GeospaceDataManagement.instruments.gnss_tec
   :members:

JRO_ISR
-------

The incoherent scatter radar (ISR) at the
`Jicamarca Radio Observatory <https://www.igp.gob.pe/observatorios/radio-observatorio-jicamarca/?page_id=6609>`_
regularly measures the velocity, density, and other ionospheric characteristics
near the magnetic equator over Peru.

.. automodule:: GeospaceDataManagement.instruments.jro_isr
   :members:


Madrigal_Dst
------------

An instrument for the Madrigal Dst index data.  This data set spans the years
of 1957 through a period close to today, with all data saved in a single file.
Because of this, you only need to download the data once and any desired time
period may be loaded (unless you require a time between your last download and
now).

.. automodule:: GeospaceDataManagement.instruments.madrigal_dst
   :members:


Madrigal_Geoind
---------------

An instrument for the Madrigal geomagnetic index data.  This data set spans the
years of 1950 through a period close to today, with all data saved in a single
file. Because of this, you only need to download the data once and any desired
time period may be loaded (unless you require a time between your last download
and now).

.. automodule:: GeospaceDataManagement.instruments.madrigal_geoind
   :members:


Madrigal_Timeseries
-------------------

A general instrument for Madrigal time-series data.  This
:py:class:`pysat.Instrument` uses Madrigal instrument codes and kindats to
support the use of any of the Madrigal time-series data sets.  There are some
further constraints in that the data set's Madrigal naming convention must be
parsable by pysat.  Currently three Madrigal instrument codes are supported by
this :py:class:`pysat.Instrument`.  When possible, using a specific instrument
module is recommended, since that instrument module will have additional
support (e.g., cleaning methods, experiment acknowledgements, and references).

.. automodule:: GeospaceDataManagement.instruments.madrigal_timeseries
   :members:


NGDC_AE
-------

An instrument for the Geophysical indices from NGDC, which include AE, AL, AU,
and AO.  The :py:attr:`name` is AE due to the Madrigal naming conventions.  The
data set spans the years of 1978 through 1987, will all data saved in a single
file.  Because of this, you only need to download the data once and any desired
time period may be loaded.

.. automodule:: GeospaceDataManagement.instruments.ngdc_ae
   :members:


OMNI2_IMF
---------

An instrument for the interplanetary magnetic field (IMF) data from OMNI 2. The
data starts in 1963 and the entire data set is contained in a single file.  The
file is occasionally updated, and so obtaining the most recent data means that
all historic data must also be downloaded (or re-downloaded). OMNI data may
also be obtained more directly from NASA.

.. automodule:: GeospaceDataManagement.instruments.omni2_imf
   :members:


.. _madrigal-methods:

Madrigal Methods
----------------

Several methods exist to support interactions with MadrigalWeb, provide
common references and awknowledgements, and analyse specific data sets.  Most of
these directly support the Instrument sub-modules, but others contain useful
tools for manipulating specific data sets.

.. _madrigal-methods-dmsp:

DMSP Methods
^^^^^^^^^^^^

Supports the DMSP instruments.


.. automodule:: GeospaceDataManagement.instruments.madrigal_methods.dmsp
   :members:



.. _madrigal-methods-general:

General Methods
^^^^^^^^^^^^^^^

Supports the interactions with the Madrigal database.


.. automodule:: GeospaceDataManagement.instruments.madrigal_methods.general
   :members:


.. _madrigal-methods-gnss:

GNSS Methods
^^^^^^^^^^^^

Supports the interactions with the GNSS data sets.


.. automodule:: GeospaceDataManagement.instruments.madrigal_methods.gnss
   :members:


.. _madrigal-methods-jro:

JRO Methods
^^^^^^^^^^^

Supports the interactions with the Jicamarca data sets.


.. automodule:: GeospaceDataManagement.instruments.madrigal_methods.jro
   :members:
