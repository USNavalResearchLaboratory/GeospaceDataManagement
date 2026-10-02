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
"""Routines for the F10.7 solar index."""

import datetime as dt
import numpy as np
import pandas as pds
import xarray as xr

import GeospaceDataManagement as gdm
from GeospaceDataManagement.instruments.methods.general import is_fill_val
from GeospaceDataManagement.utils.meta import default_fill_values_from_type


def acknowledgements(tag):
    """Define the acknowledgements for the F10.7 data.

    Parameters
    ----------
    tag : str
        Tag of the space weather index

    Returns
    -------
    ackn : str
        Acknowledgements string associated with the appropriate F10.7 tag.

    """
    lisird = 'NOAA radio flux obtained through LISIRD'
    swpc = ''.join(['Prepared by the U.S. Dept. of Commerce, NOAA, Space ',
                    'Weather Prediction Center'])

    ackn = {'historic': lisird, 'prelim': swpc, 'daily': swpc,
            'forecast': swpc, '45day': swpc,
            'now': gdm.instruments.sw_methods.gfz.ackn}

    return ackn[tag]


def references(tag):
    """Define the references for the F10.7 data.

    Parameters
    ----------
    tag : str
        Instrument tag for the F10.7 data.

    Returns
    -------
    refs : str
        Reference string associated with the appropriate F10.7 tag.

    """
    noaa_desc = ''.join(['Dataset description: ',
                         'https://www.ngdc.noaa.gov/stp/space-weather/',
                         'solar-data/solar-features/solar-radio/noontime-flux',
                         '/penticton/documentation/dataset-description',
                         '_penticton.pdf, accessed Dec 2020'])
    orig_ref = ''.join(["Covington, A.E. (1948), Solar noise observations on",
                        " 10.7 centimetersSolar noise observations on 10.7 ",
                        "centimeters, Proceedings of the IRE, 36(44), ",
                        "p 454-457."])
    swpc_desc = ''.join(['Dataset description: https://www.swpc.noaa.gov/',
                         'sites/default/files/images/u2/Usr_guide.pdf'])
    gfz_desc = ''.join(['Dataset description: https://kp.gfz-potsdam.de/app/',
                        'format/Kp_ap_Ap_SN_F107_format.txt'])

    refs = {'historic': "\n".join([noaa_desc, orig_ref]),
            'prelim': "\n".join([swpc_desc, orig_ref]),
            'now': "\n".join([gfz_desc, orig_ref]),
            'daily': "\n".join([swpc_desc, orig_ref]),
            'forecast': "\n".join([swpc_desc, orig_ref]),
            '45day': "\n".join([swpc_desc, orig_ref])}

    return refs[tag]


def combine_f107(standard_inst, forecast_inst, start=None, stop=None,
                 note_label='notes', fill_label='fill_val'):
    """Combine the output from the measured and forecasted F10.7 sources.

    Parameters
    ----------
    standard_inst : gdm.Instrument or NoneType
        Instrument object containing data for the 'sw' platform, 'f107' name,
        and 'historic', 'prelim', 'now', or 'daily' tag
    forecast_inst : gdm.Instrument or NoneType
        Instrument object containing data for the 'sw' platform, 'f107' name,
        and 'now', 'prelim', '45day' or 'forecast' tag
    start : dt.datetime or NoneType
        Starting time for combining data, or None to use earliest loaded
        date from the gdm Instruments (default=None)
    stop : dt.datetime or NoneType
        Ending time for combining data, or None to use the latest loaded date
        from the gdm Instruments (default=None)
    note_label : str
        Meta label for notes (default='notes')
    fill_label : str
        Meta label for fill value (default='fill_val')

    Returns
    -------
    f107_inst : gdm.Instrument
        Instrument object containing F10.7 observations for the desired period
        of time, merging the standard, 45day, and forecasted values based on
        their reliability

    Raises
    ------
    ValueError
        If appropriate time data is not supplied, or if the date range is badly
        formed.

    Notes
    -----
    Merging prioritizes the standard data, then the 45day data, and finally
    the forecast data.

    Will not attempt to download any missing data, but will load data.

    If no data is present, but dates are provided, supplies a series of fill
    values.

    """

    # Initialize metadata and flags
    notes = "Combines data from"
    stag = standard_inst.tag if len(standard_inst.tag) > 0 else 'default'
    tag = 'combined_{:s}_{:s}'.format(stag, forecast_inst.tag)
    inst_flag = 'standard'

    # If the start or stop times are not defined, get them from the Instruments
    if start is None:
        stimes = [inst.index.min() for inst in [standard_inst, forecast_inst]
                  if len(inst.index) > 0]
        start = min(stimes) if len(stimes) > 0 else None

    if stop is None:
        stimes = [inst.index.max() for inst in [standard_inst, forecast_inst]
                  if len(inst.index) > 0]
        stop = max(stimes) + pds.DateOffset(days=1) if len(stimes) > 0 else None

    if start is None or stop is None:
        raise ValueError(' '.join(("must either load in Instrument objects or",
                                   "provide starting and ending times")))

    if start >= stop:
        raise ValueError("date range is zero or negative")

    # Initialize the output instrument
    f107_inst = gdm.Instrument()
    f107_inst.inst_module = gdm.instruments.sw_f107
    f107_inst.tag = tag
    f107_inst.date = start
    f107_inst.doy = np.int64(start.strftime("%j"))
    fill_val = None
    index_name = None

    f107_times = list()
    f107_values = list()

    # Cycle through the desired time range
    itime = dt.datetime(start.year, start.month, start.day)
    while itime < stop and inst_flag is not None:
        # Load and save the standard data for as many times as possible
        if inst_flag == 'standard':
            # Test to see if data loading is needed
            if not np.any(standard_inst.index == itime):
                # Set the load kwargs, which vary by GeospaceDataManagement
                # version and tag
                load_kwargs = {'date': itime}

                if standard_inst.tag == 'daily':
                    # Add 30 days
                    load_kwargs['date'] += dt.timedelta(days=30)

                standard_inst.load(**load_kwargs)

            if standard_inst.empty:
                good_times = [False]
            else:
                index_name = standard_inst.index.name
                good_times = ((standard_inst.index >= itime)
                              & (standard_inst.index < stop))

            if notes.find("standard") < 0:
                notes += " the {:} source ({:} to ".format(inst_flag,
                                                           itime.date())

            if np.any(good_times):
                if fill_val is None:
                    f107_inst.data.attrs.update(standard_inst.data.attrs)
                    for var in standard_inst.variables:
                        f107_inst[var].attrs.update(standard_inst[var].attrs)

                    if fill_label in f107_inst['f107'].attrs:
                        fill_val = f107_inst['f107'].attrs[fill_label]
                    else:
                        fill_val = default_fill_values_from_type(float)

                good_vals = np.array([not is_fill_val(val, fill_val) for val
                                      in standard_inst['f107'][good_times]])
                new_times = list(standard_inst.index[good_times][good_vals])
            else:
                new_times = []

            if len(new_times) > 0:
                f107_times.extend(new_times)
                new_vals = list(standard_inst['f107'].values[good_times][
                    good_vals])
                f107_values.extend(new_vals)
                itime = f107_times[-1] + pds.DateOffset(days=1)
            else:
                inst_flag = 'forecast'
                notes += "{:})".format(itime.date())

        # Load and save the forecast data for as many times as possible
        if inst_flag == "forecast":
            # Determine which files should be loaded
            if len(forecast_inst.index) == 0:
                if len(forecast_inst.files.files) > 0:
                    files = np.unique(forecast_inst.files.files[itime:stop])
                else:
                    files = [None]  # No load, because no files are available
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
                if forecast_inst.empty:
                    good_vals = []
                else:
                    # Check in case there was a problem with the standard data
                    if fill_val is None:
                        f107_inst.data.attrs.update(forecast_inst.data.attrs)
                        for var in forecast_inst.variables:
                            if var in f107_inst.variables:
                                f107_inst[var].attrs.update(
                                    forecast_inst[var].attrs)

                        if fill_label in f107_inst['f107'].attrs:
                            fill_val = f107_inst['f107'].attrs[fill_label]
                        else:
                            fill_val = default_fill_values_from_type(float)

                    # Get the good times and values
                    good_times = ((forecast_inst.index >= itime)
                                  & (forecast_inst.index < stop))
                    good_vals = np.array([
                        not is_fill_val(val, fill_val) for val
                        in forecast_inst['f107'][good_times]])
                    if index_name is None:
                        index_name = forecast_inst.index.name

                # Save desired data and cycle time
                if len(good_vals) > 0:
                    new_times = list(forecast_inst.index[good_times][
                        good_vals])
                    f107_times.extend(new_times)
                    new_vals = list(
                        forecast_inst['f107'][good_times].values[good_vals])
                    f107_values.extend(new_vals)
                    itime = f107_times[-1] + pds.DateOffset(days=1)

            notes += "{:})".format(itime.date())

            inst_flag = None

    if inst_flag is not None:
        notes += "{:})".format(itime.date())

    if index_name is None:
        index_name = 'time'
    if fill_val is None:
        fill_val = default_fill_values_from_type(float)

    # Determine if the beginning or end of the time series needs to be padded
    if len(f107_times) >= 2:
        freq = gdm.utils.time.calc_freq(f107_times)
    else:
        freq = None
    end_date = stop - pds.DateOffset(days=1)
    date_range = pds.date_range(start=start, end=end_date, freq=freq)

    if len(f107_times) == 0:
        f107_times = date_range
        freq = gdm.utils.time.calc_freq(f107_times)
        f107_values = [fill_val for i in range(len(f107_times))]

    if date_range[0] < f107_times[0]:
        # Extend the time and value arrays from their beginning with fill
        # values
        itime = abs(date_range - f107_times[0]).argmin()
        f107_times.reverse()
        f107_values.reverse()
        extend_times = list(date_range[:itime])
        extend_times.reverse()
        f107_times.extend(extend_times)
        f107_values.extend([fill_val for kk in extend_times])
        f107_times.reverse()
        f107_values.reverse()

    if date_range[-1] > f107_times[-1]:
        # Extend the time and value arrays from their end with fill values
        itime = abs(date_range - f107_times[-1]).argmin() + 1
        extend_times = list(date_range[itime:])
        f107_times.extend(extend_times)
        f107_values.extend([fill_val for kk in extend_times])

    # Save output data
    data = xr.Dataset(data_vars={'f107': ((index_name), f107_values)},
                      coords={index_name: f107_times})

    # Resample the output data, filling missing values
    if (date_range.shape != f107_inst.index.shape
            or abs(date_range - f107_inst.index).max().total_seconds() > 0.0):
        data = data.resample(**{index_name: freq}).asfreq()
        if fill_val is not None and np.isfinite(fill_val):
            data[np.isnan(f107_inst.data)] = fill_val

    # Save the data to the instrument
    f107_inst.data = data

    # Update the metadata notes for this procedure
    notes += ", in that order"
    f107_inst['f107'].attrs.update({note_label: notes})

    return f107_inst


def calc_f107a(f107_inst, f107_name='f107', f107a_name='f107a', min_pnts=41,
               fill_label='fill_val'):
    """Calculate the 81 day mean F10.7.

    Parameters
    ----------
    f107_inst : gdm.Instrument
        Instrument holding the F10.7 data
    f107_name : str
        Data column name for the F10.7 data (default='f107')
    f107a_name : str
        Data column name for the F10.7a data (default='f107a')
    min_pnts : int
        Minimum number of points required to calculate an average (default=41)
    fill_label : str
        Meta fill value label (default='fill_val')

    Note
    ----
    Will not pad data on its own

    """

    # Test to see that the input data is present
    if f107_name not in f107_inst.variables:
        raise ValueError("unknown input data variable: {:}".format(f107_name))

    # Test to see that the output data does not already exist
    if f107a_name in f107_inst.variables:
        raise ValueError("output data variable already exists: {:}".format(
            f107a_name))

    if fill_label in f107_inst[f107_name].attrs:
        fill_val = f107_inst.meta[f107_name].attrs[fill_label]
    else:
        fill_val = default_fill_values_from_type(float)

    # Calculate the rolling mean.  Since these values are centered but rolling
    # function doesn't allow temporal windows to be calculated this way, create
    # a hack for this.
    #
    # Ensure the data are evenly sampled at a daily frequency, since this is
    # how often F10.7 is calculated.
    time_name = f107_inst.index.name
    f107_fill = f107_inst.data.resample(**{time_name: '1D'}).asfreq()

    # Replace the time index with an ordinal
    time_ind = f107_fill[time_name].values
    f107_fill['ordinal'] = ((time_name), [pds.Timestamp(tt).toordinal()
                                          for tt in time_ind])
    f107_fill = f107_fill.swap_dims({time_name: 'ordinal'})

    # Calculate the mean
    f107_fill[f107a_name] = f107_fill[f107_name].rolling(
        ordinal=81, min_periods=min_pnts, center=True).mean(skipna=True)

    # Replace the ordinal index with the time
    f107_fill = f107_fill.swap_dims({'ordinal': time_name})
    f107_fill.drop_vars('ordinal')

    # Resample to the original frequency, if it is not equal to 1 day
    freq = gdm.utils.time.calc_freq(f107_inst.index)
    if freq != "86400s":
        # Resample to the desired frequency
        f107_fill = f107_fill.resample(**{time_name: freq}).ffill()

        # Save the output in a list
        f107a = f107_fill[f107a_name]
        f107a_values = list(f107a.values)

        # Fill any dates that fall just outside of the range
        time_ind = pds.date_range(f107a[time_name].values[0],
                                  f107_inst.index[-1], freq=freq)
        for itime in time_ind[f107a[time_name].shape[0]:]:
            if (itime - f107a[time_name].values[-1]).total_seconds() < 86400.0:
                f107a_values.append(f107a[-1])
            else:
                f107a_values.append(fill_val)

        # Redefine the data

        f107_fill = xr.Dataset({f107a_name: ((time_name), f107a_values),
                                time_name: ((time_name), time_ind)})

    # There may be missing days in the output data, remove these
    if f107_inst.index.shape < f107_fill[time_name].shape:
        f107_fill = f107_fill.loc[f107_inst.index]

    # Update the metadata
    if len(f107_inst.index) > 1:
        notes = ''.join(('Calculated using data between ',
                         '{:} and {:}'.format(f107_inst.index[0],
                                              f107_inst.index[-1])))
    else:
        notes = 'Calculated using times: {:}'.format(f107_inst.index)
    meta_dict = {'units': 'SFU', 'name': 'F10.7a', 'notes': notes,
                 'desc': "81-day centered average of F10.7",
                 'min_val': 0.0, 'max_val': np.nan, fill_label: fill_val}

    # Save the data
    f107_inst[f107a_name] = f107_fill[f107a_name]
    f107_inst[f107a_name].attrs.update(meta_dict)

    return
