#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# This is a U.S. government work and not under copyright protection in the U.S.
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Provides support utilities for adding and updating meta data."""

import numpy as np

import GeospaceDataManagement as gdm


def default_fill_values_from_type(data_type):
    """Retrieve the default fill values for data based on their type.

    Parameters
    ----------
    data_type : type
        Type for the data values

    Returns
    -------
    default_val : str, float, int, NoneType
        Sets NaN for all float values, -1 for all int values, and '' for
        all str values, and None for any other data type

    """
    # Perform some pre-checks on type, checks that could error with
    # unexpected input.
    try:
        floating_check = isinstance(data_type(), np.floating)
    except TypeError as err:
        if str(err).find('not a callable function') > 0:
            floating_check = False
        else:
            # Unexpected input
            floating_check = None

    try:
        int_check = isinstance(data_type(), np.integer)
    except TypeError as err:
        if str(err).find('not a callable function') > 0:
            int_check = False
        else:
            # Unexpected input
            int_check = None

    try:
        str_check = issubclass(data_type, str)
    except TypeError as err:
        if str(err).find('must be a class') > 0:
            str_check = False
        else:
            # Unexpected input
            str_check = None

    # Assign the default value
    if str_check:
        default_val = ''
    elif data_type is float or floating_check:
        default_val = np.nan
    elif data_type is int or int_check:
        default_val = -1
    else:
        mstr = ''.join(('No type match found for ', str(data_type)))
        gdm.logger.info(mstr)
        default_val = None

    return default_val


def get_meta_dict(**kwargs):
    """Get a dictionary to assign meta data with default and/or custom values.

    Parameters
    ----------
    **kwargs : dict
        Dict with keys as meta data labels (e.g., 'units') and values as the
        meta data values (e.g., 'hours')

    Returns
    -------
    meta_dict : dict
        Dictionary with keys of 'units', 'name', 'min_val', 'max_val', 'desc',
        'notes', and 'fill_val', along with any additional keys from the input
         parameters. Standard values will be assigned, unless these keys are
         supplied upon input.

    """
    # Set the defaults
    default_dict = {'units': '', 'name': '', 'min_val': -np.inf,
                    'max_val': np.inf, 'fill_val': np.nan, 'desc': '',
                    'notes': ''}

    # Initialize the output
    meta_dict = dict(kwargs)

    # Create a list of the keys with user data, but all lower case to
    # ensure that two keys for the same thing are not added
    lower_keys = [mkey.lower() for mkey in meta_dict.keys()]

    # Assign any defaults
    for dkey in default_dict.keys():
        if dkey not in lower_keys:
            meta_dict[dkey] = default_dict[dkey]

    return meta_dict


def standardize_meta_attrs(inst, include_time=False, default_dict=None,
                           fill_label='fill_val'):
    """Ensure all variables have the same meta data attributes.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument object that will be updated
    include_time : bool
        Include time in the meta data update (default=False)
    default_dict : dict or NoneType
        Dictionary with keys as meta data labels and values as default values
        or None to set default values to those supplied by `get_meta_dict` or
        '' if the label is not present in that output (default=None)
    fill_label : str
        If present in the Instrument `meta_labels` or `default_dict`, the
        default values for this attribute will be set to the default based on
        the data type.

    Notes
    -----
    If a new meta label is supplied through `default_dict` it will be added
    to the Instrument with the default value.

    See Also
    --------
    get_meta_dict, default_fill_values_from_type

    """
    # Initalize the default dict, if necessary
    if default_dict is None:
        default_dict = {}

    # Get the GeospaceDataManagement meta defaults
    default_gdm = get_meta_dict()

    # Update the default dict for any meta data labels that are not included
    for meta_label in inst.meta_labels:
        if meta_label not in default_dict.keys():
            if meta_label in default_gdm.keys():
                default_dict[meta_label] = default_gdm[meta_label]
            else:
                default_dict[meta_label] = ''

    # Cycle through the data variables, ensuring all have attributes for all
    # the meta data labels
    data_vars = inst.variables if include_time else inst.vars_no_time

    for dvar in data_vars:
        data_meta = inst[dvar].attrs

        if len(data_meta.keys()) < len(default_dict.keys()):
            # Some meta labels are missing, update this data variable
            for dkey in default_dict.keys():
                if dkey not in data_meta.keys():
                    # Only update meta data that is missing
                    if dkey == fill_label:
                        # Use a data type dependent value
                        data_meta[dkey] = default_fill_values_from_type(
                            inst[dvar].dtype.type)
                    else:
                        # Use the basic default
                        data_meta[dkey] = default_dict[dkey]

            # Update the data variable with the new meta data
            inst[dvar] = inst[dvar].assign_attrs(data_meta)

    return


def get_epoch_metadata(inst, epoch_name, unit_label='units', name_label='name'):
    """Create epoch or time-index metadata.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument object with data and metadata.
    epoch_name : str
        Data key for time-index or epoch data.
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')

    Returns
    -------
    epoch_dict : dict
        Dictionary of meta data for the Epoch

    """
    # Get existing meta data
    epoch_dict = inst[epoch_name].attrs

    # Update basic labels, if they are missing.
    if unit_label not in epoch_dict or epoch_dict[unit_label] == '':
        epoch_dict[unit_label] = 'Milliseconds since 1970-1-1 00:00:00'

    # Assign name
    if name_label not in epoch_dict or epoch_dict[name_label] == '':
        epoch_dict[name_label] = epoch_name

    # Update the time standards
    epoch_dict.update({'calendar': 'standard', 'Format': 'i8',
                       'Var_Type': 'data', 'Time_Base': epoch_dict[unit_label],
                       'Time_Scale': 'UTC'})

    if inst.index.is_monotonic_increasing:
        epoch_dict['MonoTon'] = 'increase'
    elif inst.index.is_monotonic_decreasing:
        epoch_dict['MonoTon'] = 'decrease'

    return epoch_dict
