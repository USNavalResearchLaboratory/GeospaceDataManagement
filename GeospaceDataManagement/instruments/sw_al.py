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
"""Supports the auroral electrojet AL values.

Properties
----------
platform
    'sw'
name
    'al'
tag
    - 'lasp' Predicted AL from real-time ACE or DSCOVR provided by LASP
inst_id
    - ''

"""

import datetime as dt
import numpy as np

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments.sw_methods import auroral_electrojet
from GeospaceDataManagement.instruments.sw_methods import lasp

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'sw'
name = 'al'
tags = {'lasp': 'Predicted AL from real-time ACE or DSCOVR provided by LASP'}
inst_ids = {'': [tag for tag in tags.keys()]}

# Generate today's date to support loading predicted data sets
today = gdm.utils.time.today()
tomorrow = today + dt.timedelta(days=1)

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'lasp': today}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with instrument specific values."""

    self.acknowledgements = auroral_electrojet.acknowledgements(
        self.name, self.tag)
    self.references = auroral_electrojet.references(self.name, self.tag)
    gdm.logger.info(self.acknowledgements)
    return


def clean(self):
    """Clean the AL index, empty function."""
    return


# ----------------------------------------------------------------------------
# Instrument functions


def load(fnames, tag='', inst_id=''):
    """Load the AL index files.

    Parameters
    ----------
    fnames : pandas.Series
        Series of filenames
    tag : str
        Instrument tag string. (default='')
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
    data = gdm.instruments.methods.general.load_csv_data(
        fnames, read_csv_kwargs={'index_col': 0,
                                 'parse_dates': True}).to_xarray()

    # Create metadata
    data['al'].attrs.update({'units': 'nT', 'name': 'AL', 'notes': tags[tag],
                             'desc': ''.join(['Auroral Electrojet lower ',
                                              'envelope, best estimate of the',
                                              ' average value over the next ',
                                              'two hours']),
                             'fill_val': np.nan, 'min_val': -np.inf,
                             'max_val': 0.0})

    return data


def list_files(tag='', inst_id='', data_path='', format_str=None):
    """List local data files for AL data.

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
    files : gdm.Files
        A class containing the verified available files

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """
    # Get the format string, if not supplied by the user
    if format_str is None:
        format_str = ''.join(['sw_al_', tag, '_{year:4d}-{month:2d}-',
                              '{day:2d}.txt'])

    # Get the desired files
    files = gdm.Files.from_os(data_path=data_path, format_str=format_str)

    return files


def download(date_array, tag, inst_id, data_path, mock_download_dir=None):
    """Download the AL index data from the appropriate repository.

    Parameters
    ----------
    date_array : array-like or pandas.DatetimeIndex
        Array-like or index of datetimes for which files will be downloaded.
    tag : str
        Instrument tag, used to determine download location.
    inst_id : str
        Instrument ID, not used.
    data_path : str
        Path to data directory.
    mock_download_dir : str or NoneType
        Local directory with downloaded files or None. If not None, will
        process any files with the correct name and date as if they were
        downloaded (default=None)

    Raises
    ------
    IOError
        If the data link has an unexpected format or if an unknown mock
        download directory is supplied.

    Note
    ----
    Called by GeospaceDataManagement. Not intended for direct use by user.

    """
    lasp.prediction_downloads(name, tag, data_path, mock_download_dir)

    return
