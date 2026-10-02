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
"""Provides routines to support the geomagnetic indices, Kp and Ap."""

import datetime as dt
import numpy as np
import pandas as pds
import xarray as xr

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments.methods.general import is_fill_val
from GeospaceDataManagement.instruments.sw_methods import gfz
from GeospaceDataManagement.instruments.sw_methods import swpc


# --------------------------------------------------------------------------
# Instrument utilities

def acknowledgements(name, tag):
    """Define the acknowledgements for the geomagnetic data sets.

    Parameters
    ----------
    name : str
        Instrument name of space weather index, accepts 'kp' or 'ap'.
    tag : str
        Instrument tag.

    """

    ackn = {'kp': {'forecast': swpc.ackn, 'recent': swpc.ackn, 'def': gfz.ackn,
                   'now': gfz.ackn, 'prediction': swpc.ackn},
            'ap': {'forecast': swpc.ackn, 'recent': swpc.ackn,
                   'prediction': swpc.ackn, '45day': swpc.ackn,
                   'def': gfz.ackn, 'now': gfz.ackn},
            'cp': {'def': gfz.ackn, 'now': gfz.ackn}}

    return ackn[name][tag]


def references(name, tag):
    """Define the references for the geomagnetic data sets.

    Parameters
    ----------
    name : str
        Instrument name of space weather index, accepts kp or ap.
    tag : str
        Instrument tag.

    """

    gen_refs = "\n".join([''.join(["J. Bartels, The technique of scaling ",
                                   "indices K and Q of geomagnetic activity, ",
                                   "Ann. Intern. Geophys. Year 4, 215-226, ",
                                   "1957."]),
                          ''.join(["J. Bartels,The geomagnetic measures for ",
                                   "the time-variations of solar corpuscular ",
                                   "radiation, described for use in ",
                                   "correlation studies in other geophysical ",
                                   "fields, Ann. Intern. Geophys. Year 4, ",
                                   "227-236, 1957."]),
                          ''.join(["P.N. Mayaud, Derivation, Meaning and Use ",
                                   "of Geomagnetic Indices, Geophysical ",
                                   "Monograph 22, Am. Geophys. Union, ",
                                   "Washington D.C., 1980."]),
                          ''.join(["G.K. Rangarajan, Indices of magnetic ",
                                   "activity, in Geomagnetism, edited by I.A. ",
                                   "Jacobs, Academic, San Diego, 1989."]),
                          ''.join(["M. Menvielle and A. Berthelier, The ",
                                   "K-derived planetary indices: description ",
                                   "and availability, Rev. Geophys. 29, 3, ",
                                   "415-432, 1991."])])

    refs = {'kp': {'forecast': gen_refs, 'recent': gen_refs,
                   'prediction': gen_refs, 'def': gfz.geoind_refs,
                   'now': gfz.geoind_refs},
            'ap': {'recent': gen_refs, 'forecast': gen_refs, '45day': gen_refs,
                   'prediction': gen_refs, 'def': gfz.geoind_refs,
                   'now': gfz.geoind_refs},
            'cp': {'def': gfz.geoind_refs, 'now': gfz.geoind_refs}}

    return refs[name][tag]


def get_kp_metadata(fill_val=-1, unit_label='units', desc_label='desc',
                    min_label='min_val', max_label='max_val',
                    fill_label='fill_val'):
    """Initialize the Kp meta data using our knowledge of the index.

    Parameters
    ----------
    fill_val : int or float
        File-specific fill value (default=-1)
    unit_label : str
        Meta data label for units (default='units')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')

    Returns
    -------
    meta_dict : dict
        Dictionary with default meta data

    """
    meta_dict = {unit_label: '', desc_label: "Planetary K-index", min_label: 0,
                 max_label: 9, fill_label: fill_val}

    return meta_dict


def get_ap_metadata(fill_val=-1, unit_label='units', desc_label='desc',
                    min_label='min_val', max_label='max_val',
                    fill_label='fill_val'):
    """Initialize the ap meta data using our knowledge of the index.

    Parameters
    ----------
    fill_val : int or float
        File-specific fill value (default=-1)
    unit_label : str
        Meta data label for units (default='units')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')

    Returns
    -------
    meta_dict : dict
        Dictionary with default meta data

    """
    meta_dict = {unit_label: '', desc_label: "ap (equivalent range) index",
                 min_label: 0, max_label: 400, fill_label: fill_val}

    return meta_dict


def get_bartel_metadata(data_key, fill_val=-1, unit_label='units',
                        name_label='name', desc_label='desc',
                        min_label='min_val', max_label='max_val',
                        fill_label='fill_val'):
    """Initialize the Bartel rotation meta data using our knowledge of the data.

    Parameters
    ----------
    data_key : str
        String denoting the data key
    fill_val : int or float
        File-specific fill value (default=-1)
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')

    Returns
    -------
    meta_dict : dict
        Dictionary with default meta data

    """

    if data_key.find('solar_rotation_num') >= 0:
        units = ''
        bname = 'Bartels solar rotation number'
        desc = 'A sequence of 27-day intervals counted from February 8, 1832'
        max_val = np.inf
    elif data_key.find('day_within') >= 0:
        units = 'day'
        bname = 'Days within Bartels solar rotation'
        desc = 'Number of days within the Bartels solar rotation'
        max_val = 27
    else:
        raise ValueError('unknown data key: {:}'.format(data_key))

    meta_dict = {unit_label: units, name_label: bname, desc_label: desc,
                 min_label: 1, max_label: max_val, fill_label: fill_val}

    return meta_dict

# --------------------------------------------------------------------------
# Common custom functions


def convert_3hr_kp_to_ap(kp_inst, var_name='Kp', unit_label='units',
                         name_label='name', desc_label='desc',
                         min_label='min_val', max_label='max_val',
                         fill_label='fill_val', note_label='notes'):
    """Calculate 3 hour ap from 3 hour Kp index.

    Parameters
    ----------
    kp_inst : gdm.Instrument
        Instrument containing Kp data
    var_name : str
        Variable name for the Kp data (default='Kp')
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')
    note_label : str
        Meta data notes label (default='notes')

    Raises
    ------
    ValueError
        If `var_name` is not present in `kp_inst`.

    Note
    ----
    Conversion between ap and Kp indices is described at:
    https://www.ngdc.noaa.gov/stp/GEOMAG/kp_ap.html

    Assigns new data to '3hr_ap'.

    """
    # Kp are keys, where n.3 = n+ and n.6 = (n+1)-. E.g., 0.6 = 1-
    kp_to_ap = {0: 0, 0.3: 2, 0.6: 3, 1: 4, 1.3: 5, 1.6: 6, 2: 7, 2.3: 9,
                2.6: 12, 3: 15, 3.3: 18, 3.6: 22, 4: 27, 4.3: 32, 4.6: 39,
                5: 48, 5.3: 56, 5.6: 67, 6: 80, 6.3: 94, 6.6: 111, 7: 132,
                7.3: 154, 7.6: 179, 8: 207, 8.3: 236, 8.6: 300, 9: 400}

    def ap(kk):
        if np.isfinite(kk):
            return kp_to_ap[np.floor(kk * 10.0) / 10.0]
        else:
            return np.nan

    # Test the input
    if var_name not in kp_inst.variables:
        raise ValueError('Variable name for Kp data is missing: {:}'.format(
            var_name))

    # Convert from Kp to ap
    fill_val = kp_inst[var_name].attrs[fill_label]
    ap_data = np.array([ap(kp) if kp != fill_val else fill_val
                        for kp in kp_inst[var_name].values])

    # Add metadata
    meta_dict = get_ap_metadata(fill_val, unit_label=unit_label,
                                min_label=min_label, max_label=max_label,
                                fill_label=fill_label, desc_label=desc_label)
    meta_dict[desc_label] = "3-hr ap (equivalent range) index"
    meta_dict[note_label] = ''.join([
        'ap converted from Kp as described at: ',
        'https://www.ngdc.noaa.gov/stp/GEOMAG/kp_ap.html'])

    # Append the output to the Instrument
    kp_inst['3hr_ap'] = ((kp_inst.index.name), ap_data, meta_dict)
    return


def calc_daily_Ap(ap_inst, ap_name='3hr_ap', daily_name='Ap',
                  running_name=None, min_periods=8, unit_label='units',
                  name_label='name', desc_label='desc', min_label='min_val',
                  max_label='max_val', fill_label='fill_val',
                  note_label='notes'):
    """Calculate the daily Ap index from the 3hr ap index.

    Parameters
    ----------
    ap_inst : gdm.Instrument
        Instrument containing 3-hourly ap data
    ap_name : str
        Column name for 3-hourly ap data (default='3hr_ap')
    daily_name : str
        Column name for daily Ap data (default='Ap')
    running_name : str or NoneType
        Column name for daily running average of ap, not output if None
        (default=None)
    min_periods : int
        Mininmum number of observations needed to output an average value
        (default=8)
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')
    note_label : str
        Meta data notes label (default='notes')

    Raises
    ------
    ValueError
        If `ap_name` or `daily_name` aren't present in `ap_inst`

    Note
    ----
    Ap is the mean of the 3hr ap indices measured for a given day

    Option for running average is included since this information is used
    by MSIS when running with sub-daily geophysical inputs

    """

    # Test that the necessary data is available
    if ap_name not in ap_inst.variables:
        raise ValueError("bad 3-hourly ap variable name: {:}".format(ap_name))

    # Test to see that we will not be overwritting data
    if daily_name in ap_inst.variables:
        raise ValueError("daily Ap variable name already exists: " + daily_name)

    # Calculate the daily mean value, first filling the data to the desired
    # 3-hour frequency
    time_name = ap_inst.index.name
    ap_fill = ap_inst.data.resample(**{time_name: '3h'}).asfreq()

    # Now replace the time index with an ordinal in hours
    time_ind = ap_fill[time_name].values
    ap_fill['ordinal'] = ((time_name), [
        int((tt - time_ind[0]) / np.timedelta64(3, 'h')) for tt in time_ind])
    ap_fill = ap_fill.swap_dims({time_name: 'ordinal'})

    # Calculate the mean
    ap_mean = ap_fill[ap_name].rolling(ordinal=8,
                                       min_periods=min_periods).mean()

    # Replace the ordinal index with the time
    ap_mean = ap_mean.swap_dims({'ordinal': time_name})
    ap_mean.drop_vars('ordinal')

    if running_name is not None:
        ap_inst[running_name] = ap_mean

        meta_dict = get_ap_metadata(
            ap_inst[ap_name].attrs[fill_label], unit_label=unit_label,
            desc_label=desc_label, min_label=min_label, max_label=max_label,
            fill_label=fill_label)
        meta_dict[desc_label] = "running daily Ap index"
        meta_dict[note_label] = '24-h running ave of 3-hourly ap indices'

        ap_inst[running_name].attrs.update(meta_dict)

    # Resample, backfilling so that each day uses the mean for the data from
    # that day only
    #
    # Pad the data so the first day will be backfilled and incomplete days will
    # have fill values
    ap_pad = pds.Series(np.full(shape=(1,), fill_value=np.nan),
                        index=[ap_mean[time_name].values[0]
                               - pds.DateOffset(hours=3)])
    ap_full = pds.Series(
        np.full(shape=ap_mean[time_name].shape, fill_value=np.nan),
        index=ap_mean[time_name].values)
    mean_ser = pds.Series(ap_mean, index=ap_mean[time_name])

    # Extract the mean that only uses data for one day
    ap_sel = ap_pad.combine_first(mean_ser.iloc[[i for i, tt in
                                                 enumerate(mean_ser.index)
                                                 if tt.hour == 21]])

    # Backfill this data
    ap_data = ap_sel.resample('3h').bfill().combine_first(ap_full)

    # Save the output for the original time range
    ap_inst[daily_name] = ((time_name), pds.Series(ap_data[1:],
                                                   index=ap_data.index[1:]))

    # Add metadata
    meta_dict = get_ap_metadata(ap_inst[ap_name].attrs[fill_label],
                                unit_label=unit_label, desc_label=desc_label,
                                min_label=min_label, max_label=max_label,
                                fill_label=fill_label)
    meta_dict[desc_label] = "daily Ap index"
    meta_dict[note_label] = 'Ap daily mean calculated from 3-hourly ap indices'
    ap_inst.data[daily_name].attrs.update(meta_dict)

    return


def filter_geomag(inst, min_kp=0, max_kp=9, filter_time=24, kp_inst=None,
                  var_name='Kp'):
    """Filter Instrument data for given time after Kp drops below gate.

    Parameters
    ----------
    inst : gdm.Instrument or NoneType
        Instrument with non-Kp data to be filtered by geomagnetic activity
    min_kp : float
        Minimum Kp value allowed. Kp values below this filter the data in
        inst (default=0)
    max_kp : float
        Maximum Kp value allowed. Kp values above this filter the data in
        inst (default=9)
    filter_time : int
        Number of hours to filter data after Kp drops below max_kp (default=24)
    kp_inst : gdm.Instrument or NoneType
        Kp gdm.Instrument object with or without data already loaded. If None,
        will load GFZ definitive kp data for the instrument date (default=None)
    var_name : str
        String providing the variable name for the Kp data (default='Kp')

    Raises
    ------
    IOError
        If no Kp data is available to load

    Note
    ----
    Loads Kp data for the same timeframe covered by inst and sets inst.data to
    NaN for times when Kp > max_kp or Kp < min_kp and for filter_time after Kp
    drops below max_kp.

    Default max and min values accept all Kp, so changing only one will cause
    the filter to act as a high- or low-pass function.

    This routine is written for standard Kp data (tags of 'def', 'now'), not
    the forecast or recent data.  However, it will work with these Kp data if
    they are supplied.

    """
    # Load the desired data
    if kp_inst is None:
        kp_inst = gdm.Instrument(inst_module=gdm.instruments.sw_kp,
                                 tag='def', pad=dt.timedelta(days=1))

    if kp_inst.empty:
        load_kwargs = {'date': inst.index[0], 'end_date': inst.index[-1],
                       'verifyPad': True}
        kp_inst.load(**load_kwargs)

    if kp_inst.empty:
        raise IOError(
            'unable to load {:} data for {:}-{:}, check local data'.format(
                ':'.join([inst.platform, inst.name, inst.tag, inst.inst_id]),
                inst.index[0], inst.index[-1]))

    # Begin filtering, starting at the beginning of the instrument data
    sel_data = kp_inst[(inst.index[0] - dt.timedelta(days=1)):
                       (inst.index[-1] + dt.timedelta(days=1))]
    drop_data = sel_data.where((sel_data[var_name] > max_kp)
                               | (sel_data[var_name] < min_kp), drop=True)

    # Determine the time filter range for removing each flagged data
    for dtime in drop_data[kp_inst.index.name].values:
        sind = pds.Timestamp(dtime).to_pydatetime()
        eind = sind + dt.timedelta(hours=filter_time)
        inst.data = inst.data.where(
            (inst.data[inst.index.name] < np.datetime64(sind))
            | (inst.data[inst.index.name] > np.datetime64(eind)), other=np.nan)

    # Drop fill data
    inst.data = inst.data.dropna(dim=inst.index.name, how='all')

    return


# --------------------------------------------------------------------------
# Common analysis functions

def convert_ap_to_kp(ap_data, fill_val=-1, ap_name='ap', kp_name='Kp',
                     unit_label='units', name_label='name', desc_label='desc',
                     min_label='min_val', max_label='max_val',
                     fill_label='fill_val', note_label='notes'):
    """Convert Ap into Kp.

    Parameters
    ----------
    ap_data : array-like
        Array-like object containing Ap data
    fill_val : int, float, NoneType
        Fill value for the data set (default=-1)
    ap_name : str
        Name of the input ap (default='ap')
    kp_name : str
        Name of the output Kp (default='Kp')
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')
    note_label : str
        Meta data notes label (default='notes')

    Returns
    -------
    kp_data : array-like
        Array-like object containing Kp data
    meta_dict : dict
        Dictionary with meta data

    """
    # Ensure ap data is list-like
    ap_data = gdm.utils.listify(ap_data)

    # Convert from ap to Kp
    kp_data = np.array([round_ap(aa, fill_val=fill_val) for aa in ap_data])

    # Set the metadata
    meta_dict = get_kp_metadata(fill_val=fill_val, unit_label=unit_label,
                                desc_label=desc_label, min_label=min_label,
                                max_label=max_label, fill_label=fill_label)
    meta_dict[desc_label] = 'Kp converted from {:}'.format(ap_name)
    meta_dict[note_label] = ''.join(
        ['Kp converted from ', ap_name, 'as described at: ',
         'https://www.ngdc.noaa.gov/stp/GEOMAG/kp_ap.html'])
    meta_dict[name_label] = 'Kp'

    # Return the data and metadata in the Instrument
    return kp_data, meta_dict


def round_ap(ap_in, fill_val=np.nan):
    """Round an ap value to the nearest Kp value.

    Parameters
    ----------
    ap_in : float
        Ap value as a floating point number.
    fill_val : float
        Value for unassigned or bad indices. (default=np.nan)

    Returns
    -------
    float
        Fill value for infinite or out-of-range data, otherwise the best kp
        index is provided.

    """

    # Define the ap to kp conversion
    one_third = 1.0 / 3.0
    two_third = 2.0 / 3.0
    ap_to_kp = {0: 0, 2: one_third, 3: two_third, 4: 1, 5: 1.0 + one_third,
                6: 1.0 + two_third, 7: 2, 9: 2.0 + one_third,
                12: 2.0 + two_third, 15: 3, 18: 3.0 + one_third,
                22: 3.0 + two_third, 27: 4, 32: 4.0 + one_third,
                39: 4.0 + two_third, 48: 5, 56: 5.0 + one_third,
                67: 5.0 + two_third, 80: 6, 94: 6.0 + one_third,
                111: 6.0 + two_third, 132: 7, 154: 7.0 + one_third,
                179: 7.0 + two_third, 207: 8, 236: 8.0 + one_third,
                300: 8.0 + two_third, 400: 9}
    max_ap = 400

    # Infinite or NaN values will return the fill value
    if not np.isfinite(ap_in):
        return fill_val

    # Ap values that correspond exactly to a Kp value will return that value
    if ap_in in ap_to_kp.keys():
        return ap_to_kp[ap_in]

    # The input Ap value may be appropriate, but does not correspond directly
    # to a Kp index.  Get a sorted list of directly corresponding Ap indices,
    # with Kp returned as double (N- = N.6667, N+ = N.3333333)
    ap_keys = sorted([akey for akey in ap_to_kp.keys() if akey <= ap_in])

    # If the value is too large or too small, return the fill value
    if len(ap_keys) == 0 or (ap_keys[-1] < ap_in and ap_keys[-1] == max_ap):
        return fill_val

    # The value is realistic, return the Kp value
    return ap_to_kp[ap_keys[-1]]


def combine_kp(standard_inst=None, recent_inst=None, forecast_inst=None,
               start=None, stop=None, fill_val=np.nan, unit_label='units',
               name_label='name', desc_label='desc', min_label='min_val',
               max_label='max_val', fill_label='fill_val', note_label='notes'):
    """Combine the output from the different Kp sources for a range of dates.

    Parameters
    ----------
    standard_inst : gdm.Instrument or NoneType
        Instrument object containing data for the 'sw' platform, 'kp' name,
        and 'def' tag or None to exclude (default=None)
    recent_inst : gdm.Instrument or NoneType
        Instrument object containing data for the 'sw' platform, 'kp' name,
        and 'recent' tag or None to exclude (default=None)
    forecast_inst : gdm.Instrument or NoneType
        Instrument object containing data for the 'sw' platform, 'kp' name,
        and 'forecast' tag or None to exclude (default=None)
    start : dt.datetime or NoneType
        Starting time for combining data, or None to use earliest loaded
        date from the Instruments (default=None)
    stop : dt.datetime
        Ending time for combining data, or None to use the latest loaded date
        from the Instruments (default=None)
    fill_val : int or float
        Desired fill value (since the standard instrument fill value differs
        from the other sources) (default=np.nan)
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    desc_label : str
        Meta data label for description (default='desc')
    min_label : str
        Meta data label for minimum value (default='min_val')
    max_label : str
        Meta data label for maximum value (default='max_val')
    fill_label : str
        Meta data label for fill value (default='fill_val')
    note_label : str
        Meta data notes label (default='notes')

    Returns
    -------
    kp_inst : gdm.Instrument
        Instrument object containing Kp observations for the desired period of
        time, merging the standard, recent, and forecasted values based on
        their reliability

    Raises
    ------
    ValueError
        If only one Kp instrument or bad times are provided

    Note
    ----
    Merging prioritizes the standard data, then the recent data, and finally
    the forecast data.

    Will not attempt to download any missing data, but will load data.

    If no data is present, but dates are provided, supplies a series of fill
    values.

    """
    notes = "Combines data from"

    # Create an ordered list of the Instruments, excluding any that are None
    all_inst = list()
    tag = 'combined'
    inst_flag = None
    if standard_inst is not None:
        all_inst.append(standard_inst)
        tag += '_standard'
        if inst_flag is None:
            inst_flag = 'standard'

    if recent_inst is not None:
        all_inst.append(recent_inst)
        tag += '_recent'
        if inst_flag is None:
            inst_flag = 'recent'

    if forecast_inst is not None:
        all_inst.append(forecast_inst)
        tag += '_forecast'
        if inst_flag is None:
            inst_flag = 'forecast'

    if len(all_inst) < 2:
        raise ValueError("need at two Kp Instrument objects to combine them")

    # If the start or stop times are not defined, get them from the Instruments
    if start is None:
        stimes = [inst.index.min() for inst in all_inst if len(inst.index) > 0]
        start = min(stimes) if len(stimes) > 0 else None

    if stop is None:
        stimes = [inst.index.max() for inst in all_inst if len(inst.index) > 0]
        stop = max(stimes) + dt.timedelta(days=1) if len(stimes) > 0 else None

    if start is None or stop is None:
        raise ValueError(' '.join(("must either load in Instrument objects or",
                                   "provide starting and ending times")))

    # Initialize the output instrument
    kp_inst = gdm.Instrument()

    kp_inst.inst_module = gdm.instruments.sw_kp
    kp_inst.tag = tag
    kp_inst.date = start
    kp_inst.doy = np.int64(start.strftime("%j"))
    kp_meta = get_kp_metadata(fill_val=fill_val, unit_label=unit_label,
                              desc_label=desc_label, min_label=min_label,
                              max_label=max_label, fill_label=fill_label)

    kp_times = list()
    kp_values = list()
    index_name = None

    # Cycle through the desired time range
    itime = start
    while itime < stop and inst_flag is not None:
        # Load and save the standard data for as many times as possible
        if inst_flag == 'standard':
            # Test to see if data loading is needed
            if not np.any(standard_inst.index == itime):
                standard_inst.load(date=itime)

            if notes.find("standard") < 0:
                notes += " the {:} source ({:} to ".format(inst_flag,
                                                           itime.date())

            if len(standard_inst.index) == 0:
                inst_flag = 'forecast' if recent_inst is None else 'recent'
                notes += "{:})".format(itime.date())
            else:
                local_fill_val = standard_inst['Kp'].attrs[fill_label]
                good_times = ((standard_inst.index >= itime)
                              & (standard_inst.index < stop))
                good_vals = np.array([
                    not is_fill_val(val, local_fill_val)
                    for val in standard_inst['Kp'][good_times]])
                new_times = list(standard_inst.index[good_times][good_vals])

                if len(new_times) > 0:
                    kp_times.extend(new_times)
                    kp_values.extend(list(
                        standard_inst['Kp'][good_times].values[good_vals]))
                    itime = kp_times[-1] + pds.DateOffset(hours=3)

                    if index_name is None:
                        index_name = standard_inst.index.name
                else:
                    inst_flag = 'forecast' if recent_inst is None else 'recent'
                    notes += "{:})".format(itime.date())

        # Load and save the recent data for as many times as possible
        if inst_flag == 'recent':
            # Determine which files should be loaded
            if len(recent_inst.index) == 0:
                if len(recent_inst.files.files) > 0:
                    files = np.unique(recent_inst.files.files[itime:stop])
                else:
                    files = [None]  # No files available
            else:
                files = [None]  # No load needed, if already initialized

            # Cycle through all possible files of interest, saving relevant
            # data
            for filename in files:
                if filename is not None:
                    recent_inst.load(fname=filename)

                if notes.find("recent") < 0:
                    notes += " the {:} source ({:} to ".format(inst_flag,
                                                               itime.date())

                # Determine which times to save
                if recent_inst.empty:
                    new_times = []
                else:
                    local_fill_val = recent_inst['Kp'].attrs[fill_label]
                    good_times = ((recent_inst.index >= itime)
                                  & (recent_inst.index < stop))
                    good_vals = np.array([
                        not is_fill_val(val, local_fill_val)
                        for val in recent_inst['Kp'][good_times]])
                    new_times = list(recent_inst.index[good_times][good_vals])

                # Save output data and cycle time
                if len(new_times) > 0:
                    kp_times.extend(new_times)
                    kp_values.extend(list(
                        recent_inst['Kp'][good_times].values[good_vals]))
                    itime = kp_times[-1] + pds.DateOffset(hours=3)

                    if index_name is None:
                        index_name = recent_inst.index.name

            inst_flag = 'forecast' if forecast_inst is not None else None
            notes += "{:})".format(itime.date())

        # Load and save the forecast data for as many times as possible
        if inst_flag == "forecast":
            # Determine which files should be loaded
            if len(forecast_inst.index) == 0:
                if len(forecast_inst.files.files) > 0:
                    files = np.unique(forecast_inst.files.files[itime:stop])
                else:
                    files = [None]  # No files have been downloaded
            else:
                files = [None]  # No load needed, if already initialized

            # Cycle through all possible files of interest, saving relevant
            # data
            for filename in files:
                if filename is not None:
                    forecast_inst.load(fname=filename)

                if notes.find("forecast") < 0:
                    notes += " the {:} source ({:} to ".format(inst_flag,
                                                               itime.date())

                # Determine which times to save
                if not forecast_inst.empty:
                    local_fill_val = forecast_inst['Kp'].attrs[fill_label]
                    good_times = ((forecast_inst.index >= itime)
                                  & (forecast_inst.index < stop))
                    good_vals = np.array([
                        not is_fill_val(val, local_fill_val)
                        for val in forecast_inst['Kp'][good_times]])

                    # Save desired data
                    new_times = list(forecast_inst.index[good_times][good_vals])

                    if index_name is None:
                        index_name = forecast_inst.index.name

                    if len(new_times) > 0:
                        kp_times.extend(new_times)
                        new_vals = list(forecast_inst['Kp'][good_times][
                            good_vals])
                        kp_values.extend(new_vals)

                        # Cycle time
                        itime = kp_times[-1] + pds.DateOffset(hours=3)
            notes += "{:})".format(itime.date())

            inst_flag = None

    if inst_flag is not None:
        notes += "{:})".format(itime.date())

    if index_name is None:
        index_name = 'time'

    # Determine if the beginning or end of the time series needs to be padded
    freq = None if len(kp_times) < 2 else gdm.utils.time.calc_freq(kp_times)
    end_date = stop - pds.DateOffset(days=1)
    date_range = pds.date_range(start=start, end=end_date, freq=freq)

    if len(kp_times) == 0:
        kp_times = date_range
        kp_values = [fill_val for i in range(len(kp_times))]

    if date_range[0] < kp_times[0]:
        # Extend the time and value arrays from their beginning with fill
        # values
        itime = abs(date_range - kp_times[0]).argmin()
        kp_times.reverse()
        kp_values.reverse()
        extend_times = list(date_range[:itime])
        extend_times.reverse()
        kp_times.extend(extend_times)
        kp_values.extend([fill_val for kk in extend_times])
        kp_times.reverse()
        kp_values.reverse()

    if date_range[-1] > kp_times[-1]:
        # Extend the time and value arrays from their end with fill values
        itime = abs(date_range - kp_times[-1]).argmin() + 1
        extend_times = list(date_range[itime:])
        kp_times.extend(extend_times)
        kp_values.extend([fill_val for kk in extend_times])

    # Update the metadata notes for this procedure
    notes += ", in that order"
    kp_meta[note_label] = notes

    # Save output data and meta data
    kp_inst.data = xr.Dataset({index_name: ((index_name), kp_times),
                               'Kp': ((index_name), kp_values, kp_meta)})

    # Resample the output data, filling missing values
    if (date_range.shape != kp_inst.index.shape
            or abs(date_range - kp_inst.index).max().total_seconds() > 0.0):
        kp_inst.data = kp_inst.data.resample(**{index_name: freq}).asfreq()
        nan_fill = np.isnan(kp_inst.data['Kp'].values)
        if np.isfinite(fill_val) and nan_fill.any():
            kp_inst.data['Kp'][nan_fill] = fill_val

    return kp_inst
