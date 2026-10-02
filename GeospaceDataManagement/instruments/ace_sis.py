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
"""Supports ACE Solar Isotope Spectrometer data.

Properties
----------
platform
    'ace' Advanced Composition Explorer
name
    'sis' Solar Isotope Spectrometer
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

    sis = gdm.Instrument('ace', 'sis', tag='realtime')
    sis.download(start=sis.today())
    sis.load(date=sis.today())



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
name = 'sis'
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

    # Evaluate the different proton fluxes. Replace bad values with NaN and
    # times with no valid data
    self.data['int_pflux_10MeV'] = self.data['int_pflux_10MeV'].where(
        (self.data['status_10'] <= max_status), other=np.nan)
    self.data['int_pflux_30MeV'] = self.data['int_pflux_30MeV'].where(
        (self.data['status_30'] <= max_status), other=np.nan)

    eval_cols = ['int_pflux_10MeV', 'int_pflux_30MeV']

    # Remove lines without any good data
    good_sum = np.isfinite([self.data[ecol].values for ecol in eval_cols]).sum(
        axis=0)
    if 0 in good_sum:
        self.data = self.data.where(self.data['Epoch'][good_sum != 0],
                                    drop=True)

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
    flux_name = 'Integral Proton Flux'

    meta['status_10'] = {'units': '',
                         'name': ''.join([flux_name, ' > 10 MeV Status']),
                         'notes': '', 'desc': status_desc, 'fill_val': np.nan,
                         'min_val': 0, 'max_val': 9}
    meta['status_30'] = {'units': '',
                         'name': ''.join([flux_name, ' > 30 MeV Status']),
                         'notes': '', 'desc': status_desc, 'fill_val': np.nan,
                         'min_val': 0, 'max_val': 9}
    meta['int_pflux_10MeV'] = {'units': 'p/cs2-sec-ster',
                               'name': ''.join([flux_name, ' > 10 MeV']),
                               'notes': '',
                               'desc': ''.join(['5-min averaged ', flux_name,
                                                ' > 10 MeV']),
                               'fill_val': -1.0e5, 'min_val': -np.inf,
                               'max_val': np.inf}
    meta['int_pflux_30MeV'] = {'units': 'p/cs2-sec-ster',
                               'name': ''.join([flux_name, ' > 30 MeV']),
                               'notes': '',
                               'desc': ''.join(['5-min averaged ', flux_name,
                                                ' > 30 MeV']),
                               'fill_val': -1.0e5, 'min_val': -np.inf,
                               'max_val': np.inf}

    # Convert the data to xarray and add meta data
    data = data.to_xarray()
    for dvar in data.data_vars.keys():
        if dvar in meta.keys():
            data[dvar].attrs.update(meta[dvar])

    return data
