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
"""Supports ACE Solar Wind Electron Proton Alpha Monitor data.

Properties
----------
platform
    'ace' Advanced Composition Explorer
name
    'swepam' Solar Wind Electron Proton Alpha Monitor
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


    swepam = gdm.Instrument('ace', 'swepam', tag='realtime')
    swepam.download(start=swepam.today())
    swepam.load(date=swepam.today())

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
name = 'swepam'
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
    self.data = self.data[self.data['status'] <= max_status]

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
        Series, list, or array of filenames.
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
    GeospaceDataManagement.instruments.methods.general.load_csv_data

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """

    # Save each file to the output DataFrame
    data = load_csv_data(fnames, read_csv_kwargs={'index_col': 0,
                                                  'parse_dates': True})

    # Assign the meta data
    meta, status_desc = mm_ace.common_metadata()
    sw_desc = '1-min averaged Solar Wind '

    meta['status'] = {'units': '', 'name': 'Status', 'notes': '',
                      'desc': status_desc, 'fill_val': np.nan, 'min_val': 0,
                      'max_val': 9}
    meta['sw_proton_dens'] = {'units': 'p/cc',
                              'name': 'Solar Wind Proton Density', 'notes': '',
                              'desc': ''.join([sw_desc, 'Proton Density']),
                              'fill_val': -9999.9, 'min_val': 0.0,
                              'max_val': np.inf}
    meta['sw_bulk_speed'] = {'units': 'km/s', 'name': 'Solar Wind Bulk Speed',
                             'notes': '',
                             'desc': ''.join([sw_desc, 'Bulk Speed']),
                             'fill_val': -9999.9, 'min_val': -np.inf,
                             'max_val': np.inf}
    meta['sw_ion_temp'] = {'units': 'K', 'name': 'Solar Wind Ti', 'notes': '',
                           'desc': ''.join([sw_desc, 'Ion Temperature']),
                           'fill_val': -1.0e5, 'min_val': 0.0,
                           'max_val': np.inf}

    # Convert the data to xarray and add meta data
    data = data.to_xarray()
    for dvar in data.data_vars.keys():
        if dvar in meta.keys():
            data[dvar].attrs.update(meta[dvar])

    return data
