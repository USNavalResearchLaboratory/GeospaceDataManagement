#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# Original Authors: pysat development team (c) 2016, Russell Stoneback
#                   pysat development team, (c) 2020 pysat
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Coordinate transformation functions."""

import numpy as np
import pandas as pds
import xarray as xr

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import meta


def adjust_cyclic_data(samples, high=2.0 * np.pi, low=0.0):
    """Adjust cyclic values such as longitude to a different scale.

    Parameters
    ----------
    samples : array_like
        Input array
    high: float or int
        Upper boundary for circular standard deviation range (default=2 pi)
    low : float or int
        Lower boundary for circular standard deviation range (default=0)
    axis : int or NoneType
        Axis along which standard deviations are computed.  The default is to
        compute the standard deviation of the flattened array

    Returns
    -------
    out_samples : float
        Circular standard deviation

    """

    out_samples = np.array(samples)
    sample_range = high - low

    # Update data to work with modulus
    out_samples -= low

    # Find and fix locations too large or too small
    idx, = np.where((out_samples >= sample_range) | (out_samples < 0))
    if len(idx) > 0:
        out_samples[idx] = np.mod(out_samples[idx], sample_range)

    # Restore original baseline
    out_samples += low

    return out_samples


def update_longitude(inst, lon_name=None, high=180.0, low=-180.0):
    """Update longitude to the desired range.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument class object to be updated
    lon_name : str
        Name of the longtiude data in `inst`
    high : float
        Highest allowed longitude value (default=180.0)
    low : float
        Lowest allowed longitude value (default=-180.0)

    Notes
    -----
    Updates instrument data in column provided by `lon_name`

    """
    if lon_name not in inst.variables:
        raise ValueError('unknown longitude variable name')

    new_lon = adjust_cyclic_data(inst[lon_name], high=high, low=low)
    inst[lon_name] = new_lon

    return


def calc_solar_local_time(inst, lon_name=None, slt_name='slt',
                          apply_modulus=True, ref_date=None, meta_labels=None):
    """Append solar local time to an instrument object.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument class object to be updated
    lon_name : str
        Name of the longtiude data key (assumes data are in degrees)
    slt_name : str
        Name of the output solar local time data key (default='slt')
    apply_modulus : bool
        If True, SLT values are confined to [0, 24), if False they may be
        positive or negative based on the value of their universal time
        relative to that of the reference date `ref_date`.
        (default=True)
    ref_date : dt.datetime or NoneType
        Reference initial date. If None, will use the date found at
        `inst.date`. Only valid if apply_modulus is True. (default=None)
    meta_labels : dict or NoneType
        Map for meta data labels, or None to use defaults.  If used, expects
        keys to include any of: 'units', 'name', 'desc', 'min_val', 'max_val',
        or 'fill_val' (default=None)

    Notes
    -----
    Updates Instrument data in column specified by `slt_name`, as well as
    Metadata

    """
    fill_val = np.nan

    if lon_name not in inst.data.keys():
        raise ValueError('unknown longitude variable name')

    if ref_date is not None and apply_modulus:
        istr = 'Keyword `ref_date` only supported if `apply_modulus`=False.'
        gdm.logger.info(istr)

    if ref_date is None:
        # Use date information attached to Instrument object
        ref_date = pds.Timestamp(inst.date)
    else:
        # Use user supplied reference date.
        ref_date = pds.Timestamp(ref_date)

    # Convert from numpy epoch nanoseconds to UT seconds of day
    ut_hr = list()
    for nptime in inst.index.values:
        # Use pandas to convert from numpy to Python daetime
        dtime = pds.to_datetime(nptime).to_pydatetime()
        ut_hr.append((dtime.hour * 3600.0 + dtime.minute * 60.0
                      + dtime.second + dtime.microsecond * 1.0e-6) / 3600.0)

    ut_hr = np.array(ut_hr)

    # Account for difference in days for calculations without modulus
    if not apply_modulus:
        day_diff = inst.index - ref_date
        day_diff = np.array([diff.days for diff in day_diff])
        ut_hr += day_diff * 24.

    # Calculate solar local time
    if inst[lon_name].shape == ut_hr.shape or inst[lon_name].shape == ():
        if inst[lon_name].shape == ():
            lon = np.float64(inst[lon_name])
        else:
            lon = inst[lon_name]

        slt = ut_hr + lon / 15.0
        coords = inst.index.name
    else:
        # This can only be accessed by xarray input, but longitude may or
        # may not depend on time
        if inst.index.name in inst[lon_name].coords:
            # Initalize the new shape and coordinatesx
            coords = [ckey for ckey in inst[lon_name].dims]
            slt = np.full(shape=inst[lon_name].shape, fill_value=fill_val)

            # Calculate for each UT hr
            for i, hr in enumerate(ut_hr):
                lon = inst[lon_name][inst.index.name == inst.index[0]]
                slt[i] = hr + lon / 15.0
        else:
            # Initialize the new shape and coordinates
            sshape = list(ut_hr.shape)
            sshape.extend(list(inst[lon_name].shape))

            coords = [ckey for ckey in inst[lon_name].dims]
            coords.insert(0, inst.index.name)

            slt = np.full(shape=sshape, fill_value=fill_val)

            # Calculate for each UT hr
            for i, hr in enumerate(ut_hr):
                slt[i] = hr + inst[lon_name] / 15.0

    if apply_modulus:
        # Ensure that solar local time falls between 0 and 24 hours
        slt = np.mod(slt, 24.0)
        min_val = 0.0
        max_val = 24.0
    else:
        # No modulus applied. Values are unbounded.
        min_val = -np.inf
        max_val = np.inf

    # Add units to the metadata
    meta_dict = {'units': 'h', 'name': "Solar Local Time",
                 'desc': "Solar local time in hours", 'min_val': min_val,
                 'max_val': max_val, 'fill_val': fill_val}

    if meta_labels is not None:
        for mlabel in meta_labels.keys():
            # Update the meta data label from the default to the custom value
            meta_dict[meta_labels[mlabel]] = meta_dict[mlabel]
            del meta_dict[mlabel]

    # Add the solar local time to the instrument with the meta data
    inst.data = inst.data.assign({slt_name: (coords, slt.data, meta_dict)})

    return


def establish_common_coord(coord_vals, common=True):
    """Create a coordinate array that is appropriate for multiple data sets.

    Parameters
    ----------
    coord_vals : list-like
        A list of coordinate arrays of the same type: e.g., all geodetic
        latitude in degrees
    common : bool
        True to include locations where all coordinate arrays cover, False to
        use the maximum location range from the list of coordinates
        (default=True)

    Returns
    -------
    out_coord : array-like
        An array appropriate for the list of coordinate values

    Notes
    -----
    Assumes that the supplied coordinates are distinct representations of
    the same value in the same units and range (e.g., longitude in degrees
    from 0-360).

    """

    start_val = None
    end_val = None
    res = None

    for coord_spec in coord_vals:
        # Ensure the coordinate specification is array-like
        coord_spec = np.array(coord_spec)
        if coord_spec.shape == ():
            coord_spec = np.array([coord_spec])

        if start_val is None:
            # Initialize the start and stop values
            start_val = coord_spec[0]
            end_val = coord_spec[-1]

            # Determine the resolution
            if start_val == end_val:
                res = np.inf
            else:
                res = (coord_spec[1:] - coord_spec[:-1]).mean()
        else:
            # Adjust the start and stop time as appropriate
            if common:
                if start_val < coord_spec[0]:
                    start_val = coord_spec[0]
                if end_val > coord_spec[-1]:
                    end_val = coord_spec[-1]
            else:
                if start_val > coord_spec[0]:
                    start_val = coord_spec[0]
                if end_val < coord_spec[-1]:
                    end_val = coord_spec[-1]

            # Update the resolution
            new_res = (coord_spec[1:] - coord_spec[:-1]).mean()
            if new_res < res:
                res = new_res

    # Construct the common index
    npnts = int((end_val - start_val) / res) + 1
    out_coord = np.linspace(start_val, end_val, npnts)

    return out_coord


def expand_xarray_dims(data_list, dims_equal=False, exclude_dims=None,
                       fill_label='fill_val'):
    """Ensure that dimensions do not vary when concatenating data.

    Parameters
    ----------
    data_list : list-like
        List of xr.Dataset objects with the same dimensions and variables
    dims_equal : bool
        Assert that all xr.Dataset objects have the same dimensions if True,
        the Datasets in `data_list` may have differing dimensions if False.
        (default=False)
    exclude_dims : list-like or NoneType
        Dimensions to exclude from evaluation or None (default=None)
    fill_label : str
        Meta data label for fill values (default='fill_val')

    Returns
    -------
    out_list : list-like
        List of xr.Dataset objects with the same dimensions and variables,
        and with dimensions that all have the same values and data padded when
        needed.

    """
    # Get a list of the dimensions to exclude
    if exclude_dims is None:
        exclude_dims = []
    else:
        exclude_dims = gdm.utils.listify(exclude_dims)

    # Get a list of all the dimensions
    if dims_equal:
        if len(data_list) > 0:
            dims = [dim_key for dim_key in data_list[0].dims
                    if dim_key not in exclude_dims]
        else:
            dims = []
    else:
        dims = list()
        for sdata in data_list:
            if len(dims) == 0:
                dims = [dim_key for dim_key in sdata.dims
                        if dim_key not in exclude_dims]
            else:
                for dim in sdata.dims:
                    if dim not in dims and dim not in exclude_dims:
                        dims.append(dim)

    # After loading all the data, determine which dimensions may need to be
    # expanded, as they could differ in dimensions from file to file
    combo_dims = {dim: max([sdata.sizes[dim] for sdata in data_list
                            if dim in sdata.sizes.keys()]) for dim in dims}

    # Expand the data so that all dimensions are the same shape
    out_list = list()
    for i, sdata in enumerate(data_list):
        # Determine which dimensions need to be updated
        fix_dims = [dim for dim in sdata.sizes.keys()
                    if dim in combo_dims.keys()
                    and sdata.sizes[dim] < combo_dims[dim]]

        new_data = {}
        update_new = False
        for dvar in sdata.data_vars.keys():
            # See if any dimensions need to be updated
            update_dims = list(set(sdata[dvar].dims) & set(fix_dims))

            # Save the old data as is, or pad it to have the right dims
            if len(update_dims) > 0:
                update_new = True
                new_shape = list(sdata[dvar].values.shape)
                old_slice = [slice(0, ns) for ns in new_shape]

                for dim in update_dims:
                    idim = list(sdata[dvar].dims).index(dim)
                    new_shape[idim] = combo_dims[dim]

                # Get the fill value
                if fill_label in sdata[dvar].attrs.keys():
                    # If available, take it from the metadata
                    fill_val = sdata[dvar].attrs[fill_label]
                else:
                    # Otherwise, use the data type
                    fill_val = meta.default_fill_values_from_type(
                        sdata[dvar].dtype.type)

                # Set the new data for output
                new_dat = np.full(shape=new_shape, fill_value=fill_val)
                new_dat[tuple(old_slice)] = sdata[dvar].values
                new_data[dvar] = (sdata[dvar].dims, new_dat, sdata[dvar].attrs)
            else:
                new_data[dvar] = sdata[dvar]

        # Get the updated dataset
        out_list.append(xr.Dataset(new_data) if update_new else sdata)

    return out_list


def geodetic_to_geocentric(lat_in, lon_in=None, inverse=False):
    """Convert position from geodetic to geocentric or vice-versa.

    Parameters
    ----------
    lat_in : float
        latitude in degrees.
    lon_in : float or NoneType
        longitude in degrees.  Remains unchanged, so does not need to be
        included. (default=None)
    inverse : bool
        False for geodetic to geocentric, True for geocentric to geodetic.
        (default=False)

    Returns
    -------
    lat_out : float
        latitude [degree] (geocentric/detic if inverse=False/True)
    lon_out : float or NoneType
        longitude [degree] (geocentric/detic if inverse=False/True)
    rad_earth : float
        Earth radius [km] (geocentric/detic if inverse=False/True)

    Notes
    ------
    Uses WGS-84 values. Tested against:
    https://www.vcalc.com/wiki/vcalc/geodetic+to+geocentric+latitude

    References
    ----------
    Based on J.M. Ruohoniemi's geopack and R.J. Barnes radar.pro

    """
    rad_eq = 6378.1370  # WGS-84 semi-major axis
    flat = 1.0 / 298.257223563  # WGS-84 flattening
    rad_pol = rad_eq * (1.0 - flat)  # WGS-84 semi-minor axis

    # The ratio between the semi-major and minor axis is used several times
    rad_ratio_sq = (rad_eq / rad_pol)**2

    # Calculate the square of the second eccentricity (e')
    eprime_sq = rad_ratio_sq - 1.0

    # Calculate the tangent of the input latitude
    tan_in = np.tan(np.radians(lat_in))

    # If converting from geodetic to geocentric, take the inverse of the
    # radius ratio
    if not inverse:
        rad_ratio_sq = 1.0 / rad_ratio_sq

    # Calculate the output latitude
    lat_out = np.degrees(np.arctan(rad_ratio_sq * tan_in))

    # Calculate the Earth radius at this latitude
    rad_earth = rad_eq / np.sqrt(1.0 + eprime_sq
                                 * np.sin(np.radians(lat_out))**2)

    # longitude remains unchanged
    lon_out = lon_in

    return lat_out, lon_out, rad_earth


def geodetic_to_geocentric_horizontal(lat_in, lon_in, az_in, el_in,
                                      inverse=False):
    """Convert from geodetic to geocentric local horizontal coordinates.

    Parameters
    ----------
    lat_in : float
        latitude in degrees of the local horizontal coordinate system center
    lon_in : float
        longitude in degrees of the local horizontal coordinate system center
    az_in : float
        azimuth in degrees within the local horizontal coordinate system
    el_in : float
        elevation in degrees within the local horizontal coordinate system
    inverse : bool
        False for geodetic to geocentric, True for inverse (default=False)

    Returns
    -------
    lat_out : float
        latitude in degrees of the converted horizontal coordinate system
        center
    lon_out : float
        longitude in degrees of the converted horizontal coordinate system
        center
    rad_earth : float
        Earth radius in km at the geocentric/detic (False/True) location
    az_out : float
        azimuth in degrees of the converted horizontal coordinate system
    el_out : float
        elevation in degrees of the converted horizontal coordinate system

    References
    ----------
    Based on J.M. Ruohoniemi's geopack and R.J. Barnes radar.pro

    """
    az = np.radians(az_in)
    el = np.radians(el_in)

    # Transform the location of the local horizontal coordinate system center
    lat_out, lon_out, rad_earth = geodetic_to_geocentric(lat_in, lon_in,
                                                         inverse=inverse)

    # Calculate the deviation from vertical in radians
    dev_vert = np.radians(lat_in - lat_out)

    # Calculate cartesian coordinated in local system
    x_local = np.cos(el) * np.sin(az)  # W-E axis
    y_local = np.cos(el) * np.cos(az)  # N-S axis
    z_local = np.sin(el)  # Vertical axis

    # Now rotate system about the x-axis (W-E) to align local vertical vector
    # with Earth radial vector
    x_out = x_local
    y_out = y_local * np.cos(dev_vert) + z_local * np.sin(dev_vert)
    z_out = -y_local * np.sin(dev_vert) + z_local * np.cos(dev_vert)

    # Transform the azimuth and elevation angles
    az_out = np.degrees(np.arctan2(x_out, y_out))
    el_out = np.degrees(np.arctan(z_out / np.sqrt(x_out**2 + y_out**2)))

    return lat_out, lon_out, rad_earth, az_out, el_out


def local_spherical_to_cartesian(az_in, el_in, r_in, inverse=False):
    """Convert a position from spherical to cartesian, or vice-versa.

    Parameters
    ----------
    az_in : float
        azimuth/longitude in degrees or cartesian x in km (inverse=False/True)
    el_in : float
        elevation/latitude in degrees or cartesian y in km (inverse=False/True)
    r_in : float
        distance from origin in km or cartesian z in km (inverse=False/True)
    inverse : bool
        False to go from spherical to cartesian and True for the inverse
        (default=False)

    Returns
    -------
    x_out : float
        cartesian x in km or azimuth/longitude in degrees (inverse=False/True)
    y_out : float
        cartesian y in km or elevation/latitude in degrees (inverse=False/True)
    z_out : float
        cartesian z in km or distance from origin in km (inverse=False/True)

    Notes
    -----
    This transform differs from the standard by defining azimuth as starting
    at zero from the positive y-axis instead of the positive x-axis.

    Returns elevation angle (angle from the xy plane) rather than zenith angle
    (angle from the z-axis)

    """
    if inverse:
        # Cartesian to Spherical
        xy_sq = az_in**2 + el_in**2
        z_out = np.sqrt(xy_sq + r_in**2)  # This is r
        y_out = np.degrees(np.arctan2(np.sqrt(xy_sq), r_in))  # This is zenith
        y_out = 90.0 - y_out  # This is the elevation
        x_out = np.degrees(np.arctan2(az_in, el_in))  # This is azimuth
    else:
        # Spherical coordinate system uses zenith angle (degrees from the
        # z-axis) and not the elevation angle (degrees from the x-y plane)
        zen_in = np.radians(90.0 - el_in)

        # Spherical to Cartesian: varies from standard to have azimuth
        # start from zero at the y-axis
        x_out = r_in * np.sin(zen_in) * np.sin(np.radians(az_in))
        y_out = r_in * np.sin(zen_in) * np.cos(np.radians(az_in))
        z_out = r_in * np.cos(zen_in)

    return x_out, y_out, z_out


def spherical_to_cartesian(theta_in, phi_in, r_in, inverse=False):
    """Convert a position from spherical to cartesian, or vice-versa.

    Parameters
    ----------
    theta_in : float
        theta in degrees or cartesian x (inverse=False/True)
    phi_in : float
        phi in degrees or cartesian y (inverse=False/True)
    r_in : float
        distance from origin or cartesian z (inverse=False/True)
    inverse : bool
        False to go from spherical to cartesian and True for the inverse
        (default=False)

    Returns
    -------
    x_out : float
        cartesian x or theta in degrees (inverse=False/True)
    y_out : float
        cartesian y or phi in degrees (inverse=False/True)
    z_out : float
        cartesian z or radial distance from origin (inverse=False/True)

    Notes
    -----
    This transform differs from the standard by defining azimuth as starting
    at zero from the positive y-axis instead of the positive x-axis.

    Returns elevation angle (angle from the xy plane) rather than zenith angle
    (angle from the z-axis)

    """
    if inverse:
        # Cartesian to Spherical
        xy_sq = theta_in**2 + phi_in**2
        z_out = np.sqrt(xy_sq + r_in**2)  # This is r
        y_out = np.degrees(np.arctan2(np.sqrt(xy_sq), r_in))  # This is zenith
        y_out = 90.0 - y_out  # This is the elevation or phi
        x_out = np.degrees(np.arctan2(phi_in, theta_in))  # This is theta
    else:
        # Spherical coordinate system uses zenith angle (degrees from the
        # z-axis) and not the elevation angle (degrees from the x-y plane)
        zen_in = np.radians(90.0 - phi_in)

        # Spherical to Cartesian
        x_out = r_in * np.sin(zen_in) * np.cos(np.radians(theta_in))
        y_out = r_in * np.sin(zen_in) * np.sin(np.radians(theta_in))
        z_out = r_in * np.cos(zen_in)

    return x_out, y_out, z_out


def global_to_local_cartesian(x_in, y_in, z_in, lat_cent, lon_cent, rad_cent,
                              inverse=False):
    """Convert a position from global to local cartesian or vice-versa.

    Parameters
    ----------
    x_in : float
        global or local cartesian x in km (inverse=False/True)
    y_in : float
        global or local cartesian y in km (inverse=False/True)
    z_in : float
        global or local cartesian z in km (inverse=False/True)
    lat_cent : float
        geocentric latitude in degrees of local cartesian system origin
    lon_cent : float
        geocentric longitude in degrees of local cartesian system origin
    rad_cent : float
        distance from center of the Earth in km of local cartesian system
        origin
    inverse : bool
        False to convert from global to local cartesian coodiantes, and True
        for the inverse (default=False)

    Returns
    -------
    x_out : float
        local or global cartesian x in km (inverse=False/True)
    y_out : float
        local or global cartesian y in km (inverse=False/True)
    z_out : float
        local or global cartesian z in km (inverse=False/True)

    Notes
    -----
    The global cartesian coordinate system has its origin at the center of the
    Earth, while the local system has its origin specified by the input
    latitude, longitude, and radius.  The global system has x intersecting
    the equatorial plane and the prime meridian, z pointing North along the
    rotational axis, and y completing the right-handed coodinate system.
    The local system has z pointing up, y pointing North, and x pointing East.

    """
    # Get the global cartesian coordinates of local origin
    x_cent, y_cent, z_cent = spherical_to_cartesian(lon_cent, lat_cent,
                                                    rad_cent)

    # Get the amount of rotation needed to align the x-axis with the
    # Earth's rotational axis
    ax_rot = np.radians(90.0 - lat_cent)

    # Get the amount of rotation needed to align the global x-axis with the
    # prime meridian
    mer_rot = np.radians(lon_cent + 90.0)

    if inverse:
        # Local to global conversion
        #
        # Rotate about the x-axis to align the z-axis with the Earth's
        # rotational axis
        xrot = x_in
        yrot = y_in * np.cos(ax_rot) - z_in * np.sin(ax_rot)
        zrot = y_in * np.sin(ax_rot) + z_in * np.cos(ax_rot)

        # Rotate about the global z-axis to get the global x-axis aligned
        # with the prime meridian and translate the local center to the
        # global origin
        x_out = xrot * np.cos(mer_rot) - yrot * np.sin(mer_rot) + x_cent
        y_out = xrot * np.sin(mer_rot) + yrot * np.cos(mer_rot) + y_cent
        z_out = zrot + z_cent
    else:
        # Global to local conversion
        #
        # Translate global origin to the local origin
        xtrans = x_in - x_cent
        ytrans = y_in - y_cent
        ztrans = z_in - z_cent

        # Rotate about the global z-axis to get the local x-axis pointing East
        xrot = xtrans * np.cos(-mer_rot) - ytrans * np.sin(-mer_rot)
        yrot = xtrans * np.sin(-mer_rot) + ytrans * np.cos(-mer_rot)
        zrot = ztrans

        # Rotate about the x-axis to get the z-axis pointing up
        x_out = xrot
        y_out = yrot * np.cos(-ax_rot) - zrot * np.sin(-ax_rot)
        z_out = yrot * np.sin(-ax_rot) + zrot * np.cos(-ax_rot)

    return x_out, y_out, z_out


def local_horizontal_to_global_geo(az, el, dist, lat_orig, lon_orig, alt_orig,
                                   geodetic=True):
    """Convert from local horizontal coords to geodetic or geocentric coords.

    Parameters
    ----------
    az : float
        Azimuth (angle from North) of point in degrees
    el : float
        Elevation (angle from ground) of point in degrees
    dist : float
        Distance from origin to point in km
    lat_orig : float
        Latitude of origin in degrees
    lon_orig : float
        Longitude of origin in degrees
    alt_orig : float
        Altitude of origin in km from the surface of the Earth
    geodetic : bool
        True if origin coordinates are geodetic, False if they are geocentric.
        Will return coordinates in the same system as the origin input.
        (default=True)

    Returns
    -------
    lat_pnt : float
        Latitude of point in degrees
    lon_pnt : float
        Longitude of point in degrees
    rad_pnt : float
        Distance to the point from the centre of the Earth in km

    References
    ----------
    Based on J.M. Ruohoniemi's geopack and R.J. Barnes radar.pro

    """
    # If the data are in geodetic coordiantes, convert to geocentric
    if geodetic:
        (glat, glon, rearth, gaz, gel) = geodetic_to_geocentric_horizontal(
            lat_orig, lon_orig, az, el, inverse=False)
        grad = rearth + alt_orig
    else:
        glat = lat_orig
        glon = lon_orig
        grad = alt_orig + 6371.0  # Add the mean earth radius in km
        gaz = az
        gel = el

    # Convert from local horizontal to local cartesian coordiantes
    x_loc, y_loc, z_loc = local_spherical_to_cartesian(gaz, gel, dist,
                                                       inverse=False)

    # Convert from local to global cartesian coordiantes
    x_glob, y_glob, z_glob = global_to_local_cartesian(x_loc, y_loc, z_loc,
                                                       glat, glon, grad,
                                                       inverse=True)

    # Convert from global cartesian to geocentric coordinates
    lon_pnt, lat_pnt, rad_pnt = spherical_to_cartesian(x_glob, y_glob, z_glob,
                                                       inverse=True)

    # Convert from geocentric to geodetic, if desired
    if geodetic:
        lat_pnt, lon_pnt, rearth = geodetic_to_geocentric(lat_pnt, lon_pnt,
                                                          inverse=True)
        rad_pnt = rearth + rad_pnt - 6371.0

    return lat_pnt, lon_pnt, rad_pnt
