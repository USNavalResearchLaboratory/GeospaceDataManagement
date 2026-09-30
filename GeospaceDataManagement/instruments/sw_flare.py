#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# Original Authors: pysat development team, (c) 2020 pysat
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Supports solar flare values.

Properties
----------
platform
    'sw'
name
    'flare'
tag
    - 'prelim' Preliminary SWPC daily solar indices
    - 'daily' Daily SWPC solar indices (contains last 30 days)
    - 'prediction' Predictions from SWPC for the next 3 days

Examples
--------
Download and load the most recent flare predictions. To always ensure you are
loading the most recent data, load the data with tomorrow's date.
::

    flare = gdm.Instrument('sw', 'flare', tag='prediction')
    flare.download(start=flare.tomorrow())
    flare.load(date=flare.tomorrow())


Note
----
The forecast data is stored by generation date, where each file contains the
forecast for the next three days. Forecast data downloads are only supported
for the current day. When loading forecast data, the date specified with the
load command is the date the forecast was generated. The data loaded will span
three days. To always ensure you are loading the most recent data, load
the data with tomorrow's date.


Warnings
--------
The 'prediction' flare data loads three days at a time. Loading multiple files,
loading multiple days, the data padding feature, and multi_file_day feature
available from the pyast.Instrument object is not appropriate for 'prediction'
data.

"""

import datetime as dt
import numpy as np
import os
import pandas as pds

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments import sw_methods

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'sw'
name = 'flare'
tags = {'prelim': 'Preliminary SWPC daily solar indices',
        'daily': 'Daily SWPC solar indices (contains last 30 days)',
        'prediction': 'Predictions from SWPC for the next 3 days'}

# Dict keyed by inst_id that lists supported tags for each inst_id
inst_ids = {'': [tag for tag in tags.keys()]}

# Dict keyed by inst_id that lists supported tags and a good day of test data
# generate todays date to support loading forecast data
now = dt.datetime.now(tz=dt.timezone.utc)
today = dt.datetime(now.year, now.month, now.day)
tomorrow = today + dt.timedelta(days=1)

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'prelim': dt.datetime(2009, 1, 1),
                    'daily': tomorrow,
                    'prediction': tomorrow}}

# Other tags assumed to be True
_test_download_ci = {'': {'prelim': False}}

# ----------------------------------------------------------------------------
# Instrument methods

preprocess = sw_methods.general.preprocess_fill


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    # Set the required Instrument attributes
    self.acknowledgements = sw_methods.swpc.ackn
    self.references = "".join(["Check SWPC for appropriate references: ",
                               "https://www.swpc.noaa.gov/phenomena"])
    gdm.logger.info(self.acknowledgements)

    return


def clean(self):
    """Clean the F10.7 data, empty function as this is not necessary."""

    return


# ----------------------------------------------------------------------------
# Instrument functions


def load(fnames, tag='', inst_id=''):
    """Load the solar flare files.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames.
    tag : str
        Instrument tag. (default='')
    inst_id : str
        Instrument ID, not used. (default='')

    Returns
    -------
    data : xr.Dataset
        Object containing satellite data.

    See Also
    --------
    gdm.instruments.methods.general.load_csv_data

    """

    # Get the desired file dates and file names from the daily indexed list
    file_dates = list()
    if tag in ['prelim']:
        unique_files = list()
        for fname in fnames:
            file_dates.append(dt.datetime.strptime(fname[-10:], '%Y-%m-%d'))
            if fname[0:-11] not in unique_files:
                unique_files.append(fname[0:-11])
        fnames = unique_files

    # Load the CSV data files
    data = gdm.instruments.methods.general.load_csv_data(
        fnames, read_csv_kwargs={"index_col": 0, "parse_dates": True})

    # If there is a date range, downselect here
    if len(file_dates) > 0:
        idx, = np.where((data.index >= min(file_dates))
                        & (data.index < max(file_dates) + dt.timedelta(days=1)))
        data = data.iloc[idx, :]

    # Recast data
    data = data.to_xarray()

    # Initialize the metadata
    if tag == 'daily' or tag == 'prelim':
        data['goes_bgd_flux'].attrs.update(
            {'units': 'W/m^2', 'name': 'X-ray Background Flux', 'notes': '',
             'desc': 'GOES X-ray Background Flux', 'fill_val': '*',
             'min_val': -np.inf, 'max_val': np.inf})
        if 'c_flare' in data:
            data['c_flare'].attrs.update(
                {'units': '', 'name': 'C X-Ray Flares', 'notes': '',
                 'desc': 'C-class X-Ray Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
        if 'm_flare' in data:
            data['m_flare'].attrs.update(
                {'units': '', 'name': 'M X-Ray Flares', 'notes': '',
                 'desc': 'M-class X-Ray Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
        if 'x_flare' in data:
            data['x_flare'].attrs.update(
                {'units': '', 'name': 'X X-Ray Flares', 'notes': '',
                 'desc': 'X-class X-Ray Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
        if 'o1_flare' in data:
            data['o1_flare'].attrs.update(
                {'units': '', 'name': '1 Optical Flares', 'notes': '',
                 'desc': '1-class Optical Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
        if 'o2_flare' in data:
            data['o2_flare'].attrs.update(
                {'units': '', 'name': '2 Optical Flares', 'notes': '',
                 'desc': '2-class Optical Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
        if 'o3_flare' in data:
            data['o3_flare'].attrs.update(
                {'units': '', 'name': '3 Optical Flares', 'notes': '',
                 'desc': '3-class Optical Flares', 'fill_val': -1,
                 'min_val': 0, 'max_val': 9})
    elif tag == 'prediction':
        for dkey in data:
            if dkey.find('Region') < 0:
                data[dkey].attrs.update(
                    {'units': '', 'name': dkey, 'notes': '',
                     'desc': ''.join([dkey.replace('_', ' '),
                                      ' Probabilities']), 'fill_val': -1,
                     'min_val': 0, 'max_val': 100})
            else:
                data[dkey].attrs.update(
                    {'units': '', 'name': dkey, 'notes': '',
                     'desc': 'SWPC Solar Region Number', 'fill_val': -1,
                     'min_val': 1, 'max_val': 9999})

    return data


def list_files(tag='', inst_id='', data_path='', format_str=None):
    """List local solar flare data files.

    Parameters
    ----------
    tag : str
        Instrument tag, accepts any value from `tags`. (default='')
    inst_id : str
        Instrument ID, not used. (default='')
    data_path : str
        Path to data directory. (default='')
    format_str : str or NoneType
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)

    Returns
    -------
    out_files : gdm._files.Files
        A class containing the verified available files

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """
    if tag == 'prelim':
        # Files are by year (and quarter)
        if format_str is None:
            format_str = ''.join(['flare_prelim_{year:04d}_{month:02d}',
                                  '_v{version:01d}.txt'])
        out_files = gdm.Files.from_os(data_path=data_path,
                                      format_str=format_str)

        if not out_files.empty:
            # Set each file's valid length at a 1-day resolution
            orig_files = out_files.sort_index().copy()
            new_files = list()

            for orig in orig_files.items():
                # Version determines each file's valid length
                version = int(orig[1].split("_v")[1][0])
                doff = pds.DateOffset(years=1) if version == 2 \
                    else pds.DateOffset(months=3)
                istart = orig[0]
                iend = istart + doff - pds.DateOffset(days=1)

                # Ensure the end time does not extend past the number of
                # possible days included based on the file's download time
                fname = os.path.join(data_path, orig[1])
                dend = dt.datetime.utcfromtimestamp(os.path.getctime(fname))
                dend = dend - pds.DateOffset(days=1)
                if dend < iend:
                    iend = dend

                # Pad the original file index
                out_files.loc[iend] = orig[1]
                out_files = out_files.sort_index()

                # Save the files at a daily cadence over the desired period
                new_files.append(out_files.loc[istart:
                                               iend].asfreq('D', 'pad'))
            # Add the newly indexed files to the file output
            out_files = pds.concat(new_files, sort=True)
            out_files = out_files.dropna()
            out_files = out_files.sort_index()
            out_files = out_files + '_' + out_files.index.strftime('%Y-%m-%d')

    else:
        out_files = sw_methods.swpc.list_files(name, tag, inst_id, data_path,
                                               format_str=format_str)

    return out_files


def download(date_array, tag, inst_id, data_path, update_files=False,
             mock_download_dir=None):
    """Download solar flare data from the appropriate repository.

    Parameters
    ----------
    date_array : array-like
        Sequence of dates for which files will be downloaded.
    tag : str
        Denotes type of file to load.
    inst_id : str
        Specifies the satellite ID for a constellation.
    data_path : str
        Path to data directory.
    update_files : bool
        Re-download data for files that already exist if True (default=False)
    mock_download_dir : str or NoneType
        Local directory with downloaded files or None. If not None, will
        process any files with the correct name and date as if they were
        downloaded (default=None)

    Raises
    ------
    IOError
        If a problem is encountered connecting to the gateway or retrieving
        data from the remote or local repository.

    Warnings
    --------
    Only able to download current forecast data, not archived forecasts.

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """
    if tag == 'prelim':
        # Get the local files, to ensure that the version 1 files are
        # downloaded again if more data has been added
        local_files = list_files(tag, inst_id, data_path)

        sw_methods.swpc.old_indices_dsd_download(name, date_array, data_path,
                                                 local_files, today,
                                                 mock_download_dir)

    elif tag == 'daily':
        sw_methods.swpc.daily_dsd_download(name, today, data_path,
                                           mock_download_dir)

    elif tag == 'prediction':
        sw_methods.swpc.solar_geomag_predictions_download(
            name, date_array, data_path, mock_download_dir)

    return
