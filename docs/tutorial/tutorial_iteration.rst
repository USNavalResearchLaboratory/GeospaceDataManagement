.. _tutorial-iter:

Iteration
---------

:py:mod:`GeospaceDataManagement` supports iterative loading of data at daily
(the default) or custom cadences. The examples below show you how this works and
how to specify the loading limits.

Daily Iteration
^^^^^^^^^^^^^^^

By default, :py:mod:`GeospaceDataManagement` will iteratively load data at the
instrument's file cadence. If this is not specified in the instrument module,
:py:mod:`GeospaceDataManagement` will assume a daily cadence.

.. code:: python

   import datetime as dt
   import GeospaceDataManagement as gdm

   # Instantiate Instrument object
   epam = gdm.Instrument(inst_module=gdm.instruments.ace_epam, tag='historic')

   # Set range of dates and create corresponding array.
   start = dt.datetime(2026, 1, 1)
   stop = dt.datetime(2026, 1, 5)
   date_array = gdm.utils.time.create_date_range(start, stop)

   # Download data, if needed.  Download is inclusive of stop time.
   if len(epam.files[start:stop + dt.timedelta(days=1)]) < 5:
       epam.download(start=start, stop=stop)

   # Iterate over dates, load data for each date, and determine maximum
   # Electron flux between 38-53 eV for each day
   out_str = ''.join(('Maximum e Flux between 38-53 eV: ',
                      '{max:3.2f} {units} on {day}'))

   for load_date in date_array:
       epam.load(date=load_date)
       print(out_str.format(max=epam['eflux_38-53'].max(),
                            units=epam['eflux_38-53'].attrs['units'],
                            day=epam.index[0].strftime('%d %b %Y')))


Iteration support is built into the :py:class:`Instrument` object to support
this and similar cases. The whole of a data set may be iterated over on a daily
basis using:

.. code:: python

   # Load the first date and set the bounds for consideration
   epam.load(date=start)
   epam.bounds = (start, stop)  # `bounds` defaults to all available files

   # Perform the same iteration as the previous block
   for epam in epam:
       print(out_str.format(max=epam['eflux_38-53'].max(),
                            units=epam['eflux_38-53'].attrs['units'],
                            day=epam.index[0].strftime('%d %b %Y')))


You can also set the :py:attr:`bounds` to be a range of files:

.. code:: python

   # Load the first date and set the file bounds for consideration
   epam.load(date=start)
   epam.bounds = (epam.files[start], epam.files[stop])

   for epam in epam:
       print(out_str.format(max=epam['eflux_38-53'].max(),
                            units=epam['eflux_38-53'].attrs['units'],
                            day=epam.index[0].strftime('%d %b %Y')))


The output in all the above cases is:

.. code:: ipython

   Maximum e Flux between 38-53 eV: 6070.00 particles/cm2-s-ster-MeV on 01 Jan 2026
   Maximum e Flux between 38-53 eV: 5160.00 particles/cm2-s-ster-MeV on 02 Jan 2026
   Maximum e Flux between 38-53 eV: 13800.00 particles/cm2-s-ster-MeV on 03 Jan 2026
   Maximum e Flux between 38-53 eV: 27000.00 particles/cm2-s-ster-MeV on 04 Jan 2026
   Maximum e Flux between 38-53 eV: 4740.00 particles/cm2-s-ster-MeV on 05 Jan 2026


By default, :py:attr:`bounds` is set to the first and last date of the locally
available instrument files, all of which are listed (for this example) in
``epam.files.files``.


Non-standard Iteration
^^^^^^^^^^^^^^^^^^^^^^

Non-continuous data iteration is also supported.  This can be useful, for
example, when you want to load data from both the March and September equinoxes
or for several case studies.

.. code:: python

   # Two case studies
   start1 = start
   stop1 = dt.datetime(2026, 1, 2)

   start2 = dt.datetime(2026, 1, 4)
   stop2 = stop
   epam.bounds = ([start1, start2], [stop1, stop2])

   # Iterate over custom season
   epam.load(date=start1)
   for epam in epam:
       print(out_str.format(max=epam['eflux_38-53'].max(),
                            units=epam['eflux_38-53'].attrs['units'],
                            day=epam.index[0].strftime('%d %b %Y')))

Now, the output is:

.. code:: ipython

   Maximum e Flux between 38-53 eV: 6070.00 particles/cm2-s-ster-MeV on 01 Jan 2026
   Maximum e Flux between 38-53 eV: 5160.00 particles/cm2-s-ster-MeV on 02 Jan 2026
   Maximum e Flux between 38-53 eV: 27000.00 particles/cm2-s-ster-MeV on 04 Jan 2026
   Maximum e Flux between 38-53 eV: 4740.00 particles/cm2-s-ster-MeV on 05 Jan 2026


:py:mod:`GeospaceDataManagement` iteration also supports loading more than a
single day/file of data at a time as well as stepping through the data in daily
increments larger than a single day. Assignment of the data step size and width
is also set via the bounds attribute.

.. code:: python

   # Set a season with an expanded load range and increased step size. This
   # sets a data width of 2 days
   epam.bounds = (starts, stops, '2D', dt.timedelta(days=2))

   # Similar behaviour is supported with file bounds. This sets the
   # file width to 2 files and the file step size is 2 files
   epam.bounds = (start_files, stop_files, 2, 2)

Note that when iterating over date limits the limits are applied to the dates
associated with the files themselves and do not necessarily apply to the
datetimes associated with the data within the files.

The abstraction provided by the iteration support is also used for the next
section on orbit data.
