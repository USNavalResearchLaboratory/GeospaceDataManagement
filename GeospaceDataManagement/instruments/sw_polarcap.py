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
"""Supports polar cap indexes.

Properties
----------
platform
    'sw'
name
    'polarcap'
tag
    - 'prediction' Predictions from SWPC for the next 3 days
inst_id
    - ''

Note
----
Downloads data from SWPC. These files also contain other data indices, and so
the additional data files will be saved to the appropriate data directories to
avoid multiple downloads.

The forecast/prediction data is stored by generation date, where each file
contains the forecast for the next three days. Forecast data downloads are only
supported for the current day. When loading forecast data, the date specified
with the load command is the date the forecast was generated. The data loaded
will span three days. To always ensure you are loading the most recent data,
load the data with tomorrow's date.

Examples
--------
::

    pc = gdm.Instrument('sw', 'polarcap', tag='prediction')
    pc.download()
    pc.load(date=pc.tomorrow())


Warnings
--------
The 'prediction' tag loads polar cap absoprtion predictions for a specific
period of time. Loading multiple files, loading multiple days, the data padding
feature, and multi_file_day feature available from the pyast.Instrument object
is not appropriate for these tags data.

"""

import datetime as dt
import functools
import pandas as pds

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments import sw_methods

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'sw'
name = 'polarcap'
tags = {'prediction': 'SWPC Predictions for the next three days'}
inst_ids = {'': list(tags.keys())}

# Generate todays date to support loading forecast data
now = dt.datetime.now(tz=dt.timezone.utc)
today = dt.datetime(now.year, now.month, now.day)
tomorrow = today + dt.timedelta(days=1)

# ----------------------------------------------------------------------------
# Instrument test attributes

# Set test dates
_test_dates = {'': {'prediction': tomorrow}}

# ----------------------------------------------------------------------------
# Instrument methods

preprocess = sw_methods.general.preprocess_fill


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    self.acknowledgements = sw_methods.swpc.ackn
    self.references = "".join(["Check SWPC for appropriate references: ",
                               "https://www.swpc.noaa.gov/phenomena"])
    gdm.logger.info(self.acknowledgements)
    return


def clean(self):
    """Clean the polar cap indexes, not required (empty function)."""

    return


# ----------------------------------------------------------------------------
# Instrument functions

list_files = functools.partial(sw_methods.swpc.list_files, name)


def load(fnames, tag='', inst_id=''):
    """Load storm probability files.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        Instrument tag (default='')
    inst_id : str
        Instrument ID, not used. (default='')

    Returns
    -------
    data : xr.Dataset
        Object containing satellite data

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """
    # Load the data
    all_data = []
    for fname in fnames:
        result = pds.read_csv(fname, index_col=0, parse_dates=True)
        all_data.append(result)

    data = pds.concat(all_data).to_xarray()

    # Initialize the metadata
    for dkey in data.data_vars.keys():
        data[dkey].attrs.update({'units': '', 'name': dkey,
                                 'desc': dkey.replace('_', ' '),
                                 'min_val': 'green', 'max_val': 'red',
                                 'fill_val': ''})

    return data


def download(date_array, tag, inst_id, data_path, mock_download_dir=None):
    """Download the polar cap indices from the appropriate repository.

    Parameters
    ----------
    date_array : array-like or pandas.DatetimeIndex
        Array-like or index of datetimes to be downloaded.
    tag : str
        Denotes type of file to load.
    inst_id : str
        Specifies the instrument identification, not used.
    data_path : str
        Path to data directory.
    mock_download_dir : str or NoneType
        Local directory with downloaded files or None. If not None, will
        process any files with the correct name and date as if they were
        downloaded. (default=None)

    Raises
    ------
    IOError
        If an unknown mock download directory is supplied.

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    Warnings
    --------
    Only able to download current recent data, not archived forecasts.

    """

    if tag == 'prediction':
        sw_methods.swpc.solar_geomag_predictions_download(
            name, date_array, data_path, mock_download_dir)

    return
