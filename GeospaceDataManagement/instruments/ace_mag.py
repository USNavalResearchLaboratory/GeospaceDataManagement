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
"""Supports ACE Magnetometer data.

Properties
----------
platform
    'ace' Advanced Composition Explorer
name
    'mag' Magnetometer
tag
    - 'realtime' Real-time data from the Space Weather Prediction Center (SWPC)
    - 'historic' Historic data from the SWPC
inst_id
    - ''

Note
----
This is not the ACE scientific data set, which will be available at NASA

Examples
--------
The real-time data is stored by generation date, where each file contains the
data for the current day.  If you leave download dates empty, though, it will
grab today's file three times and assign dates from yesterday, today, and
tomorrow.
::

    mag = gdm.Instrument('ace', 'mag', tag='realtime')
    mag.download(start=mag.today())
    mag.load(date=mag.today())



Warnings
--------
The 'realtime' data contains a changing period of time. Loading multiple files,
loading multiple days, the data padding feature, and multi_file_day feature
available from the pyast.Instrument object is not appropriate for 'realtime'
data.

"""

import datetime as dt
import functools
import numpy as np

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments.methods.general import load_csv_data
from GeospaceDataManagement.instruments.sw_methods import ace as mm_ace
from GeospaceDataManagement.instruments.sw_methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'ace'
name = 'mag'
tags = {'realtime': 'Real-time data from the SWPC',
        'historic': ' Historic data from the SWPC'}
inst_ids = {inst_id: [tag for tag in tags.keys()] for inst_id in ['']}

# Define today's date
now = dt.datetime.now(tz=dt.timezone.utc)

# ----------------------------------------------------------------------------
# Instrument test attributes

# Set test dates (first level: inst_id, second level: tag)
_test_dates = {inst_id: {'realtime': dt.datetime(now.year, now.month, now.day),
                         'historic': dt.datetime(2009, 1, 1)}
               for inst_id in inst_ids.keys()}

# Set clean warning tests
_clean_warn = {inst_id: {tag: mm_ace.clean_warn for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods

preprocess = general.preprocess_fill


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    # Set the appropraite acknowledgements and references
    self.acknowledgements = mm_ace.acknowledgements()
    self.references = mm_ace.references(self.name)
    gdm.logger.info(self.acknowledgements)

    return


def clean(self):
    """Clean real-time ACE data using the status flag.

    Note
    ----
    Supports 'clean' and 'dirty'.  Replaces all fill values with NaN.
    Clean - status flag of zero (nominal data)
    Dirty - status flag < 9 (accepts bad data record, removes no data record)

    """
    # Perform the standard ACE cleaning
    max_status = mm_ace.clean(self)

    # Replace bad values with NaN and remove times with no valid data
    self.data = self.data.where(self.data['status'] <= max_status, drop=True)

    return


# ----------------------------------------------------------------------------
# Instrument functions

download = functools.partial(mm_ace.download, name=name, now=now)
list_files = functools.partial(mm_ace.list_files, name=name)


def load(fnames, tag='', inst_id=''):
    """Load the ACE space weather prediction data.

    Parameters
    ----------
    fnames : array-like
        Series, list, or array of filenames
    tag : str
        Instrument tag, not used. (default='')
    inst_id : str
        ACE instrument ID, not used. (default='')

    Returns
    -------
    data : xr.Dataset
        Object containing instrument data

    See Also
    --------
    gdm.instruments.methods.general.load_csv_data

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """

    # Save each file to the output DataFrame
    data = load_csv_data(fnames,
                         read_csv_kwargs={'index_col': 0,
                                          'parse_dates': True}).to_xarray()

    # Assign the meta data
    meta, status_desc = mm_ace.common_metadata()

    meta['status'] = {'units': '', 'name': 'Status',
                      'notes': '', 'desc': status_desc,
                      'fill_val': np.nan, 'min_val': 0, 'max_val': 9}
    meta['bx_gsm'] = {'units': 'nT', 'name': 'Bx GSM',
                      'notes': '', 'desc': '1-min averaged IMF Bx',
                      'fill_val': -999.9, 'min_val': -np.inf, 'max_val': np.inf}
    meta['by_gsm'] = {'units': 'nT', 'name': 'By GSM',
                      'notes': '', 'desc': '1-min averaged IMF By',
                      'fill_val': -999.9, 'min_val': -np.inf, 'max_val': np.inf}
    meta['bz_gsm'] = {'units': 'nT', 'notes': '', 'name': 'Bz GSM',
                      'desc': '1-min averaged IMF Bz', 'fill_val': -999.9,
                      'min_val': -np.inf, 'max_val': np.inf}
    meta['bt_gsm'] = {'units': 'nT', 'name': 'Bt GSM', 'notes': '',
                      'desc': '1-min averaged IMF Bt', 'fill_val': -999.9,
                      'min_val': -np.inf, 'max_val': np.inf}
    meta['lat_gsm'] = {'units': 'degrees', 'name': 'GSM Lat',
                       'notes': '', 'desc': 'GSM Latitude', 'fill_val': -999.9,
                       'min_val': -90.0, 'max_val': 90.0}
    meta['lon_gsm'] = {'units': 'degrees', 'name': 'GSM Lon', 'notes': '',
                       'desc': 'GSM Longitude', 'fill_val': -999.9,
                       'min_val': 0.0, 'max_val': 360.0}

    # Add the meta data
    for dvar in data.data_vars.keys():
        if dvar in meta.keys():
            data[dvar].attrs.update(meta[dvar])

    return data
