.. _exmultdown:

Downloading data from multiple Instruments
==========================================

Unlike most data sets, space weather index data sets often contain a combination
of related indices. This means that data from multiple
:py:class:`GeospaceDataManagement.Instrument` sub-modules may be available in a
single file. This data is saved for all
:py:class:`GeospaceDataManagement.Instrument` sub-modules when downloading any
one of them. In this way, downloads are minimized and no data sets are hidden
or thrown away. The following example returns both F\ :sub:`10.7`\ and Ap
forecasts from SWPC.

::

   import GeospaceDataManagement as gdm

   f107 = gdm.Instrument(inst_module=gdm.instruments.sw_f107, tag='45day')
   ap = gdm.Instrument(inst_module=gdm.instruments.sw_ap, tag='45day')

   # Test to see this data hasn't already been downloaded
   assert (ap.today() not in f107.files.files) and (ap.today()
                                                    not in ap.files.files)

   # Download both data sets using only one Instrument
   f107.download(start=f107.tomorrow())
   ap.download(start=ap.tomorrow())

   # Show that both files have been downloaded
   print(f107.files.files[f107.today()], ap.files.files[ap.today()])


This will yield ``f107_45day_YYYY-MM-DD.txt ap_45day_YYYY-MM-DD.txt``, where
YYYY-MM-DD is the day you run this example.  The table below shows a list of
the :py:class:`GeospaceDataManagement.Instrument` sub-modules and tags that
download multiple data sets.  When possible, the same tag has been used across
:py:class:`GeospaceDataManagement.Instrument` sub-modules.


+----------------------+----------+-----------+------------+------------+
| Remote Data Set      | Platform | Name      | Tag(s)     | Inst ID(s) |
+======================+==========+===========+============+============+
| GFZ Kp               | SW       | Kp        | def, now   |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Ap        |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Cp        |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC Daily DSD       | SW       | F107      | daily      |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Flare     |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | SSN       |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | SBField   |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC Prelim DSD      | SW       | F107      | prelim     |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Flare     |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | SSN       |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | SBField   |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC 3-day Solar-Geo | SW       | F107      | forecast   |            |
+----------------------+----------+-----------+------------+------------+
| Predictions          |          | Kp        | prediction |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Ap        |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | StormProb |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Flare     |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | PolarCap  |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC 3-day Geomag    | SW       | Kp        | forecast   |            |
+----------------------+----------+-----------+------------+------------+
| Forecast             |          | Ap        |            |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | StormProb |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC Daily Geomag    | SW       | Kp        | recent     |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Ap        |            |            |
+----------------------+----------+-----------+------------+------------+
| SWPC 45-day Forecast | SW       | F107      | 45day      |            |
+----------------------+----------+-----------+------------+------------+
|                      |          | Ap        |            |            |
+----------------------+----------+-----------+------------+------------+
