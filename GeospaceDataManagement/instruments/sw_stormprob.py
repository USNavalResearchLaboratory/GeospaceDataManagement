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
"""Supports storm probabilities.

Properties
----------
platform
    'sw'
name
    'stormprob'
tag
    - 'prediction' Predictions from SWPC for the next 3 days
    - 'forecast' Grab forecast data from SWPC (next 3 days)
inst_id
    - ''

Note
----
Downloads data from SWPC. These files also contain other data indices, and so
the additional data files will be saved to the appropriate data directories to
avoid multiple downloads.

The forecast data is stored by generation date, where each file contains the
forecast for the next three days. Forecast data downloads are only supported
for the current day. When loading forecast data, the date specified with the
load command is the date the forecast was generated. The data loaded will span
three days. To always ensure you are loading the most recent data, load
the data with tomorrow's date.

Examples
--------
::

    storm = gdm.Instrument('sw', 'stormprob', tag='forecast')
    storm.download()
    storm.load(date=storm.tomorrow())


Warnings
--------
The 'forecast' tag loads storm probabilities for a specific period of time.
Loading multiple files, loading multiple days, the data padding feature, and
multi_file_day feature available from the pyast.Instrument object is not
appropriate for these tags data.

"""

import datetime as dt
import functools
import pandas as pds

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments import sw_methods

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'sw'
name = 'stormprob'
tags = {'forecast': 'SWPC Forecast data next (3 days)',
        'prediction': 'SWPC Predictions for the next three days'}
inst_ids = {'': list(tags.keys())}

# Generate todays date to support loading forecast data
now = dt.datetime.now(tz=dt.timezone.utc)
today = dt.datetime(now.year, now.month, now.day)
tomorrow = today + dt.timedelta(days=1)

# ----------------------------------------------------------------------------
# Instrument test attributes

# Set test dates
_test_dates = {'': {'forecast': tomorrow,
                    'prediction': tomorrow}}

# ----------------------------------------------------------------------------
# Instrument methods

preprocess = sw_methods.general.preprocess_fill


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    self.acknowledgements = sw_methods.swpc.ackn
    self.references = "".join(["https://www.swpc.noaa.gov/sites/default/files",
                               "/images/NOAAscales.pdf"])
    gdm.logger.info(self.acknowledgements)
    return


def clean(self):
    """Clean the Kp, not required for this index (empty function)."""

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

    Warnings
    --------
    tag '' has been deprecated, will be removed in version 0.2.0+

    """

    # Load the data
    all_data = []
    for fname in fnames:
        result = pds.read_csv(fname, index_col=0, parse_dates=True)
        all_data.append(result)

    data = pds.concat(all_data).to_xarray()
    fill_val = -1

    # Initialize the metadata
    for dkey in data.data_vars.keys():
        data[dkey].attrs.update({'units': '', 'name': dkey,
                                 'desc': dkey.replace('_', ' '),
                                 'min_val': 0, 'max_val': 100,
                                 'fill_val': fill_val})

    return data


def download(date_array, tag, inst_id, data_path, mock_download_dir=None):
    """Download the storm probabilities from the appropriate repository.

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

    if tag == 'forecast':
        sw_methods.swpc.geomag_forecast_download(name, date_array, data_path,
                                                 mock_download_dir)
    elif tag == 'prediction':
        sw_methods.swpc.solar_geomag_predictions_download(
            name, date_array, data_path, mock_download_dir)

    return
