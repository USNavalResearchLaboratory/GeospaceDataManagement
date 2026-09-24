#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# Original Authors: pysat development team (c) 2016, Russell Stoneback
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Input/Output utilities."""
import datetime as dt
import numpy as np
import os
import pandas as pds
import xarray as xr

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import meta


def load_netcdf(fnames, file_format='NETCDF4', epoch_name='time',
                epoch_unit='ms', epoch_origin='unix', decode_timedelta=False,
                combine_by_coords=True, decode_times=True,
                strict_dim_check=True):
    """Load netCDF-3/4 file produced by GeospaceDataManagement.

    Parameters
    ----------
    fnames : str or array_like
        Filename(s) to load.
    file_format : str or NoneType
        file_format keyword passed to netCDF4 routine.  Expects one of
        'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', or 'NETCDF4'.
        (default='NETCDF4')
    epoch_name : str
        Data key for epoch variable.  The epoch variable is expected to be an
        array of integer or float values denoting time elapsed from an origin
        specified by `epoch_origin` with units specified by `epoch_unit`. This
        epoch variable will be converted to a `DatetimeIndex` for consistency
        across GeospaceDataManagement instruments.  (default='time')
    epoch_unit : str
        The pandas-defined unit of the epoch variable ('D', 's', 'ms', 'us',
        'ns'). (default='ms')
    epoch_origin : str or timestamp-convertable
        Origin of epoch calculation, following convention for
        `pandas.to_datetime`.  Accepts timestamp-convertable objects, as well as
        two specific strings for commonly used calendars.  These conversions are
        handled by `pandas.to_datetime`.
        If ‘unix’ (or POSIX) time; origin is set to 1970-01-01.
        If ‘julian’, `epoch_unit` must be ‘D’, and origin is set to beginning of
        Julian Calendar. Julian day number 0 is assigned to the day starting at
        noon on January 1, 4713 BC. (default='unix')
    decode_timedelta : bool
        If True, variables with unit attributes that are 'timelike' ('hours',
        'minutes', etc) are converted to `np.timedelta64`. (default=False)
    combine_by_coords : bool
        Used when loading a multi-file dataset. If True, uses
        `xarray.combine_by_coords`. If False, uses `xarray.combine_nested`.
        (default=True)
    decode_times : bool
        If True, variables with unit attributes that are 'timelike' ('hours',
        'minutes', etc) are converted to `np.timedelta64` by xarray. If False,
        then `epoch_name` will be converted to datetime using `epoch_unit`
        and `epoch_origin`. If None, will be set to False for backwards
        compatibility. (default=True)
    strict_dim_check : bool
        If True, warn the user that the desired epoch is not present in
        `xarray.dims`.  If False, no warning is raised. (default=True)

    Returns
    -------
    data : xarray.Dataset
        Class holding file data

    See Also
    --------
    load_netcdf

    """
    # Ensure inputs are in the correct format
    fnames = gdm.utils.listify(fnames)
    file_format = file_format.upper()

    if combine_by_coords:
        combine_kw = {'combine': 'by_coords'}
    else:
        combine_kw = {'combine': 'nested', 'concat_dim': epoch_name}

    # Load the data differently for single or multiple files
    if len(fnames) == 1:
        data = xr.open_dataset(fnames[0], decode_timedelta=decode_timedelta,
                               decode_times=decode_times)
    else:
        data = xr.open_mfdataset(fnames, decode_timedelta=decode_timedelta,
                                 decode_times=decode_times, **combine_kw)

    # Need to get a list of all variables, dimensions, and coordinates.
    all_vars = xarray_all_vars(data)

    # Rename `epoch_name` to 'time'
    if epoch_name != 'time':
        if 'time' not in all_vars:
            if epoch_name in data.dims:
                data = data.rename({epoch_name: 'time'})
            elif epoch_name in all_vars:
                data = data.rename({epoch_name: 'time'})
                if strict_dim_check:
                    wstr = ''.join(['Epoch label: "', epoch_name, '"',
                                    ' is not a dimension.'])
                    gdm.logger.warning(wstr)
            else:
                estr = ''.join(['Epoch label: "', epoch_name, '"',
                                ' was not found in loaded dimensions [',
                                ', '.join(all_vars), ']'])
                raise KeyError(estr)
        else:
            estr = ''.join(["'time' already present in file. Can't rename ",
                            epoch_name, " to 'time'. To load this file ",
                            "it may be necessary to set `decode_times=True`."])
            raise ValueError(estr)

    # Convert 'time' to datetime objects, depending upon settings.
    # If decode_times False, apply our own calculation. If True,
    # datetime objects were created by xarray.
    if not decode_times:
        edates = pds.to_datetime(data['time'].values, unit=epoch_unit,
                                 origin=epoch_origin)
        data['time'] = xr.DataArray(edates, coords=data['time'].coords)

    # Need to get a list of all variables, dimensions, and coordinates.
    # Variables could have been altered since last call.
    all_vars = xarray_all_vars(data)

    # Close any open links to file through xarray
    data.close()

    return data


def inst_to_netcdf(inst, fname, base_instrument=None, unit_label='units',
                   name_label='name', mode='w', zlib=False, complevel=4,
                   shuffle=True, export_gdm_info=True, unlimited_time=True):
    """Store Instrument data in a netCDF4 file.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument object with loaded data to save
    fname : str
        Output filename with full path
    base_instrument : gdm.Instrument or NoneType
        Class used as a comparison, only attributes that are present with
        `inst` and not on `base_instrument` are written to netCDF. Using None
        assigns an unmodified gdm.Instrument object. (default=None)
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for variable name (default='name')
    mode : str
        Write (‘w’) or append (‘a’) mode. If mode=’w’, any existing file at
        this location will be overwritten. If mode=’a’, existing variables will
        be overwritten. (default='w')
    zlib : bool
        Flag for engaging zlib compression, if True compression is used
        (default=False)
    complevel : int
        An integer flag between 1 and 9 describing the level of compression
        desired. Ignored if zlib=False. (default=4)
    shuffle : bool
        The HDF5 shuffle filter will be applied before compressing the data.
        This significantly improves compression. Ignored if zlib=False.
        (default=True)
    export_gdm_info : bool
        Appends the platform, name, tag, and inst_id to the metadata
        if True. Otherwise these attributes are lost. (default=True)
    unlimited_time : bool
        Flag specifying whether or not the epoch/time dimension should be
        unlimited; it is when the flag is True. (default=True)

    Notes
    -----
    Depending on which kwargs are specified, the input class, `inst`, will
    be modified.

    Stores 1-D data along the date time index.

    - The name of the main variable column is used to prepend subvariable
      names within netCDF, var_subvar_sub
    - A netCDF4 dimension is created for each main variable column
      with higher order data; first dimension Epoch
    - The index organizing the data stored as a dimension variable
      and the name label will be set to 'Epoch'.
    - `from_netcdf` uses the variable dimensions to reconstruct data
      structure

    All attributes attached to instrument are written to netCDF attrs
    with the exception of 'Date_End', 'Date_Start', 'File', 'File_Date',
    'Generation_Date', and 'Logical_File_ID'. These are defined within
    to_netCDF at the time the file is written.  To comply to a given file
    standard, the Instrument meta data should be formatted before output.

    """
    # Ensure there is data to write
    if inst.empty:
        gdm.logger.warning('Empty Instrument, not writing {:}'.format(fname))
        return

    # Ensure the provided meta data information is valid
    if unit_label not in inst.meta_labels:
        raise ValueError('unknown unit label: {:}, expected one of {:}'.format(
            unit_label, inst.meta_labels))

    if name_label not in inst.meta_labels:
        raise ValueError('unknown name label: {:}, expected one of {:}'.format(
            name_label, inst.meta_labels))

    # Ensure directory path leading up to filename exists
    gdm.utils.files.check_and_make_path(os.path.split(fname)[0])

    # `base_instrument` is used to define the standard attributes attached to
    # the Instrument object. Any additional attributes added to the main input
    # Instrument will be written to the netCDF4
    base_attrb = dir(gdm.Instrument()) if base_instrument is None else dir(
        base_instrument)

    # Store any non standard attributes. Compare this Instrument's attributes
    # to the standard, filtering out any 'private' attributes (those that start
    # with a '_') and saving any custom public attributes
    inst_attrb = dir(inst)
    attrb_dict = {}
    for ikey in inst_attrb:
        if ikey not in base_attrb:
            if ikey.find('_') != 0:
                attrb_dict[ikey] = getattr(inst, ikey)

    # Add additional metadata to conform to standards
    attrb_dict['gdm_version'] = gdm.__version__

    # Convert the time index to Unix time in ms
    unix_time = np.array([(val - dt.datetime(1970, 1, 1)).total_seconds()
                          * 1.0e3 for val in inst.index.to_pydatetime()])

    # Set the general file information
    if export_gdm_info:
        # For operational instruments, these should be set separately.
        attrb_dict['platform'] = inst.platform
        attrb_dict['name'] = inst.name
        attrb_dict['tag'] = inst.tag
        attrb_dict['inst_id'] = inst.inst_id
        attrb_dict['acknowledgements'] = inst.acknowledgements
        attrb_dict['references'] = inst.references

    attrb_dict['Date_End'] = dt.datetime.strftime(
        inst.index[-1], '%a, %d %b %Y,  %Y-%m-%dT%H:%M:%S.%f')
    attrb_dict['Date_End'] = attrb_dict['Date_End'][:-3] + ' UTC'

    attrb_dict['Date_Start'] = dt.datetime.strftime(
        inst.index[0], '%a, %d %b %Y,  %Y-%m-%dT%H:%M:%S.%f')
    attrb_dict['Date_Start'] = attrb_dict['Date_Start'][:-3] + ' UTC'
    attrb_dict['File'] = os.path.split(fname)
    attrb_dict['File_Date'] = inst.index[-1].strftime(
        '%a, %d %b %Y,  %Y-%m-%dT%H:%M:%S.%f')
    attrb_dict['File_Date'] = attrb_dict['File_Date'][:-3] + ' UTC'
    utcnow = dt.datetime.now(dt.timezone.utc)
    attrb_dict['Generation_Date'] = utcnow.strftime('%Y%m%d')
    attrb_dict['Logical_File_ID'] = os.path.split(fname)[-1].split('.')[:-1]

    # Check for binary types, convert to string or int when found
    for akey in attrb_dict.keys():
        if attrb_dict[akey] is None:
            attrb_dict[akey] = ''
        elif isinstance(attrb_dict[akey], bool):
            attrb_dict[akey] = int(attrb_dict[akey])

    # Update or add meta data to the epoch
    epoch_meta = meta.get_epoch_metadata(inst, inst.index.name,
                                         unit_label=unit_label,
                                         name_label=name_label)

    # Attach the metadata to a separate xarray.Dataset object, ensuring
    # the Instrument data object is unchanged. The downside is additional
    # memory use which will impact extremely large data files or memory
    # constrained environments.
    xr_data = inst.data.copy()

    # Convert datetime values into integers and then add meta data
    xr_data[inst.index.name] = unix_time.astype(np.int64)
    xr_data[inst.index.name] = xr_data[inst.index.name].assign_attrs(epoch_meta)

    # Set the standard encoding values
    encoding = {var: {'zlib': zlib, 'complevel': complevel,
                      'shuffle': shuffle} for var in xr_data.keys()}

    # netCDF4 doesn't support compression for string data. Reset values
    # in `encoding` for data found to be string type.
    for var in xr_data.keys():
        vtype = xr_data[var].dtype

        # Account for possible type for unicode strings
        if vtype == np.dtype('<U4'):
            vtype = str
        elif vtype == str:
            encoding[var]['dtype'] = 'S1'
        elif vtype == np.dtype('O'):
            vtype = type(xr_data[var].values.flatten()[0])
            encoding[var]['dtype'] = 'S1'

        if vtype == str:
            encoding[var]['zlib'] = False

    if unlimited_time:
        xr_data.encoding['unlimited_dims'] = {inst.index.name: True}

    # Add general attributes
    xr_data.attrs = attrb_dict

    # Write the netCDF4 file
    xr_data.to_netcdf(fname, mode=mode, encoding=encoding)

    # Close for safety
    xr_data.close()

    return


def xarray_vars_no_time(data, time_label='time'):
    """Extract all DataSet variables except `time_label` dimension.

    Parameters
    ----------
    data : xarray.Dataset
        Dataset to get variables from.
    time_label : str
        Label used within `data` for time information.

    Returns
    -------
    vars : list
        All variables, dimensions, and coordinates, except for `time_label`.

    Raises
    ------
    ValueError
        If `time_label` not present in `data`.

    """
    vars = list(data.variables.keys())

    # Remove `time_label` dimension
    if time_label in vars:
        for i, var in enumerate(vars):
            if var == time_label:
                vars.pop(i)
                break
    else:
        estr = ''.join(["Didn't find time dimension '", time_label, "'"])
        raise ValueError(estr)

    return vars


def xarray_all_vars(data):
    """Extract all variable names, including dimensions and coordinates.

    Parameters
    ----------
    data : xarray.Dataset
        Dataset to get all variables from.

    Returns
    -------
    all_vars : list
        List of all `data.data_vars`, `data.dims`, and `data.coords`.

    """

    # Construct a list of all variables, dimensions, and coordinates.
    # Start by obtaining the dimensions.
    all_vars = list(data.dims)

    # Add coordinate information
    coords = list(data.coords)
    for coord in coords:
        if coord not in all_vars:
            all_vars.append(coord)

    # Add variable information
    vars = list(data.data_vars.keys())
    for var in vars:
        if var not in all_vars:
            all_vars.append(var)

    return all_vars
