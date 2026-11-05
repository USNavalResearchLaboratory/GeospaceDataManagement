.. _tutorial-analysis:

Analysis
--------

Because :py:mod:`GeospaceDataManagement` allows you to load and cycle through
data from different instruments in similar manners, it's easy to write
instrument-independent analysis routines.  Here we provide a simple example
where a mean value is calculated for the loaded data from an instrument.  As
;py:mod:`GeospaceDataManagement` allows data to be iteratively loaded by the
desired time period, the same method can produce different results for the same
instrument.

Sample Period Mean Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code below creates a function called :py:func:`periodic_mean` that takes
a :py:class:`~GeospaceDataManagement._instrument.Instrument` object and
calculates the mean at the cadence and over the period of time supplied by
:py:attr:`Instrument.bounds`.

.. code:: python

   import datetime as dt
   import GeospaceDataManagement as gdm
   import pandas as pds

   def periodic_mean(inst_iterator, data_label):
       """ Calculate the periodic mean over a range of dates

       Parameters
       ----------
       inst_iterator : pysat.Instrument iterator
           Expecting either pysat.Instrument for daily or pysat.Orbits for
           orbital periods
       data_label : str
           Instrument data label

       Returns
       -------
       mean_val : pds.Series
           Pandas time series containing periodic means of the desired value

       """
       # Create empty series to hold result
       mean_val = pds.Series()

       # Iterate over season, calculate the mean
       for inst in inst_iterator:
           if not inst.empty:
               # Compute mean absolute using pandas functions and store.  The
               # data could be an image, or lower dimension, account for 2D and
               # lower
               data_date = inst.index[0]
               mean_val[data_date] = inst[data_label].mean(skipna=True).item()

       return mean_val

You may apply this function as demonstrated below.

.. code:: python

   stime = dt.datetime(2009, 1, 1)
   etime = dt.datetime(2009, 1, 3)
   inst = gdm.Instrument('gdm', 'testing')

   # Load and process the daily mean of the test variable `dummy1`
   inst.load(date=stime)
   inst.bounds = (stime, etime)
   daily_mean_val = periodic_mean(inst, 'dummy1')
   print(daily_mean_val)

   2009-01-01    11.393588
   2009-01-02    11.432014
   2009-01-03    11.470440
   dtype: float64

   # Before running at different orbital cadences, reset to the start time
   inst.load(date=stime)
   inst.bounds = (stime, etime, '2d')
   twoday_mean_val2 = periodic_mean(inst, 'dummy2')
   print(twoday_mean_val2)

   2009-01-01    11.387500
   2009-01-03    11.468981
   dtype: float64

The functions such as `periodic_mean` could support for other types of
statistics or more complex processing.
