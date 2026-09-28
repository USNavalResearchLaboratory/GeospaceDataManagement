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
"""Supports Cp index values.

Properties
----------
platform
    'sw'
name
    'cp'
tag
    - 'def' Definitive Cp data from GFZ
    - 'now' Nowcast Cp data from GFZ
inst_id
    - ''

Note
----
Downloads data from ftp.gfz-potsdam.de (GFZ). These files also contain ap and Kp
data, and so the additional data files will be saved to the appropriate data
directories to avoid multiple downloads.

The historic definitive and nowcast Cp files are stored in yearly files, with
the current year being updated remotely on a regular basis.  If you are using
historic data for the current year, we recommend re-downloading it before
performing your data processing.

Examples
--------
::

    cp_ind = gdm.Instrument('sw', 'cp', tag='def')
    cp_ind.download(start=dt.datetime(2010, 1, 1))
    cp_ind.load(2010, 1)

"""

import datetime as dt
import functools
import numpy as np

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments import sw_methods

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'sw'
name = 'cp'
tags = {'def': 'Definitive Cp data from GFZ',
        'now': 'Nowcast Cp data from GFZ'}
inst_ids = {'': list(tags.keys())}

# ----------------------------------------------------------------------------
# Instrument test attributes

# Set test dates
_test_dates = {'': {'def': dt.datetime(2009, 1, 1),
                    'now': dt.datetime(2020, 1, 1)}}

# ----------------------------------------------------------------------------
# Instrument methods

preprocess = sw_methods.general.preprocess_fill


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    self.acknowledgements = sw_methods.kp_ap.acknowledgements(
        self.name, self.tag)
    self.references = sw_methods.kp_ap.references(self.name, self.tag)
    gdm.logger.info(self.acknowledgements)
    return


def clean(self):
    """Clean the Kp, not required for this index (empty function)."""

    return


# ----------------------------------------------------------------------------
# Instrument functions

download = functools.partial(sw_methods.gfz.kp_ap_cp_download, platform, name)
list_files = functools.partial(sw_methods.gfz.kp_ap_cp_list_files, name)


def load(fnames, tag='', inst_id=''):
    """Load Cp index files.

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
        Object containing satellite data

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """

    # Load the definitive or nowcast data. The Cp data stored in yearly
    # files, and we need to return data daily.  The daily date is
    # attached to filename.  Parse off the last date, load month of data,
    # and downselect to the desired day
    data = sw_methods.gfz.load_def_now(fnames).to_xarray()

    # Initalize the meta data
    data['Bartels_solar_rotation_num'].attrs.update(
        sw_methods.kp_ap.get_bartel_metadata('Bartels_solar_rotation_num'))
    data['day_within_Bartels_rotation'].attrs.update(
        sw_methods.kp_ap.get_bartel_metadata('day_within_Bartels_rotation'))
    data['Cp'].attrs.update({'units': '', 'name': 'Cp index',
                             'desc': ''.join([
                                 'the daily planetary character figure, a ',
                                 'qualitative estimate of the overall level ',
                                 'of geomagnetic activity for this day ',
                                 'determined from the sum of the eight ap ',
                                 'amplitudes']), 'min_val': 0.0,
                             'max_val': 2.5, 'fill_val': np.nan})
    data['C9'].attrs.update({'units': '', 'name': 'C9 index',
                             'desc': 'the contracted scale for Cp',
                             'min_val': 0, 'max_val': 9, 'fill_val': -1})

    return data
