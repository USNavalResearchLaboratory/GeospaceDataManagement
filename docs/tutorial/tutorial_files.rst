.. _tutorial-files:

netCDF4 Files
-------------


.. _tutorial-files-write:

Writing Files
^^^^^^^^^^^^^

:py:mod:`GeospaceDataManagement` includes support for creating netCDF4 files
suitable for sharing with collaborators and supports additional infrastructure
that would make them suitable for public distribution. Both the data and meta
data attached to a :py:class:`~GeospaceDataManagement._instrument.Instrument`
object are used to create a file that both humans and machines may understand
and parse without any outside information. This process is built with a variety
of options to help meet the range of needs of the scientific community.

For many users a netCDF4 file suitable for distribution to research colleagues
may be created using default parameters as shown below.

.. code:: python

   import datetime as dt
   import GeospaceDataManagement as gdm

   # Instantiate Instrument object
   inst = gdm.Instrument('gdm', 'testing')
   stime = dt.datetime(2009, 1, 1)

   # Load data into Instrument
   inst.load(date=stime)

   # Create netCDF4 file
   fname = stime.strftime('~/test_%Y%j.nc')
   inst.to_netcdf4(fname)

This process writes all of the data within ``inst.data`` to a netCDF4 file,
including the meta data stored within the :py:class:`xarray.Dataset`. It also
adds a variety of supplemental attributes to the file indicating the file's
conventions, creation date, and more.

A table of attributes written to every netCDF file is shown below. Any
:py:class:`~GeospaceDataMangement._instrument.Instrument` attributes added by a
user are also written to the file.

================     ==================================
File Attribute       Description
================     ==================================
acknowledgements     Ackowledgements from Instrument
Date_End             Timestamp of last data entry
Date_Start           Timestamp of first data entry
File                 Original filepath and filename
File_Date            Timestamp of last data entry
Generation_Date      YearMonthDay of file creation
inst_id              gdm.Instrument ``inst_id``
Logical_File_ID      Filename without any path or type
name                 gdm.Instrument ``name``
gdm_version          GeospaceDataManagement version information
platform             gdm.Instrument ``platform``
references           Journal references from Instrument
tag                  gdm.Instrument ``tag``
================     ==================================

Meta data is also provided for each variable containing data in the
:py:attr:`attr` dictionary.


.. _tutorial-files-load:

Loading Files
^^^^^^^^^^^^^

:py:mod:`GeospaceDataManagement` includes support for loading netCDF4 files
directly into xarray formats.  These routines will load the data and meta data
into the appropriate structures.  :py:mod:`GeospaceDataManagement` NetCDF files
may also be directly loaded into a general
:py:class:`~GeospaceDataManagement._instrument.Instrument`. Loading functions
are provided through :py:mod:`GeospaceDataManagement.utils.load_netcdf4`. These
functions are intended to be used within a
:py:class:`~GeospaceDataManagement._instrument.Instrument` support module,
particularly the :py:meth:`load` function, but can be used to create an
:py:class:`xarray.Dataset`. An example of this is shown below.

.. code:: python

   inst_ds = gdm.utils.io.load_netcdf(fname)
   print(inst_ds)
   
   <xarray.Dataset> Size: 11MB
   Dimensions:        (time: 86400)
   Coordinates:
     * time           (time) datetime64[ns] 691kB 2009-01-01 ... 2009-01-01T23:5...
   Data variables: (12/17)
       uts            (time) float64 691kB ...
       mlt            (time) float64 691kB ...
       slt            (time) float64 691kB ...
       longitude      (time) float64 691kB ...
       latitude       (time) float64 691kB ...
       altitude       (time) float64 691kB ...
       ...             ...
       string_dummy   (time) object 691kB ...
       unicode_dummy  (time) object 691kB ...
       int8_dummy     (time) int8 86kB ...
       int16_dummy    (time) int16 173kB ...
       int32_dummy    (time) int32 346kB ...
       int64_dummy    (time) int64 691kB ...
   Attributes: (12/17)
       acknowledgements:       Test instruments provided through GeospaceDataMan...
       new_thing:              1
       references:             Burrell, A. G. (2026). USNavalResearchLaboratory/...
       test_clean_kwarg:       
       test_init_kwarg:        
       test_preprocess_kwarg:  
       ...                     ...
       Date_End:               Thu, 01 Jan 2009,  2009-01-01T23:59:59.000 UTC
       Date_Start:             Thu, 01 Jan 2009,  2009-01-01T00:00:00.000 UTC
       File:                   ['~', 'test_2009001.nc']
       File_Date:              Thu, 01 Jan 2009,  2009-01-01T23:59:59.000 UTC
       Generation_Date:        20261105
       Logical_File_ID:        test_2009001


An example of the output produced when loading a
:py:mod:`GeospaceDataManagement` produced file direct via netCDF4 is included
below. Note that the :py:mod:`GeospaceDataManagement` produced file attribute
s are present along with some user defined values, such as references and
acknowledgements, that are attached to the :py:mod:`GeospaceDataManagement`
testing :py:class:`~GeospaceDataManagement._instrument.Instrument` object.

.. code::

   import netCDF4
   import os

   ndata = netCDF4.Dataset(os.path.expanduser(fname))
   print(ndata)

   <class 'netCDF4.Dataset'>
    root group (NETCDF4 data model, file format HDF5):
    acknowledgements: Test instruments provided through GeospaceDataManagement at https://www.github.com/USNavalResearchLaboratory/GeospaceDataManagement
    new_thing: 1
    references: Burrell, A. G. (2026). USNavalResearchLaboratory/GeospaceDataManagement v0.0.2 (Version v0.0.2). https://github.com/USNavalResearchLaboratory/GeospaceDataManagement

    test_clean_kwarg: 
    test_init_kwarg: 
    test_preprocess_kwarg: 
    gdm_version: 0.0.1
    platform: gdm
    name: testing
    tag: 
    inst_id: 
    Date_End: Thu, 01 Jan 2009,  2009-01-01T23:59:59.000 UTC
    Date_Start: Thu, 01 Jan 2009,  2009-01-01T00:00:00.000 UTC
    File: ['~', 'test_2009001.nc']
    File_Date: Thu, 01 Jan 2009,  2009-01-01T23:59:59.000 UTC
    Generation_Date: 20261105
    Logical_File_ID: test_2009001
    dimensions(sizes): time(86400), string4(4)
    variables(dimensions): float64 uts(time), float64 mlt(time), float64 slt(time), float64 longitude(time), float64 latitude(time), float64 altitude(time), int64 orbit_num(time), int64 dummy1(time), int64 dummy2(time), float64 dummy3(time), float64 dummy4(time), |S1 string_dummy(time, string4), |S1 unicode_dummy(time, string4), int8 int8_dummy(time), int16 int16_dummy(time), int32 int32_dummy(time), int64 int64_dummy(time), int64 time(time)
    groups:

To use these loading functions within an
:py:class:`~GeospaceDataManagement._instrument.Instrument` module, consider the
complete instrument load function needed for such a dataset shown below. For
more information on adding a new dataset to :py:mod:`GeospaceDataManagement`,
see :ref:`rst_new_inst`.

    
.. code:: python

   def load(fnames, tag='', inst_id=''):
       """Load the example Instrument produced data files.

       Parameters
       ----------
       fnames : list
           List of filenames
       tag : str
           Instrument tag (accepts '' or a string to change the behaviour of
           certain instrument aspects for testing). (default='')
       inst_id : str
           Instrument ID (accepts ''). (default='')

       Returns
       -------
       data : xr.Dataset
           Instrument data

       """

       return gdm.utils.io.load_netcdf4(fnames)


Now consider loading the file written in the example shown in
Section :ref:`tutorial-files-write`. :py:mod:`GeospaceDataManagement` also
expects all filenames to have some type of date format.  However, by using the
``data_dir`` keyword argument, we can easily load files outside of the standard
:py:mod:`GeospaceDataManagement` data paths.

.. code:: python

   import datetime as dt
   import GeospaceDataManagement as gdm

   stime = dt.datetime(2009, 1, 1)
   test_inst = gdm.Instrument("gdm", "netcdf",
                              data_dir='/example/file/path/name',
                              file_format='test_{year:04}{day:03}.nc')
   test_inst.load(date=stime)
