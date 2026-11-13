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
"""Methods supporting the Defense Meteorological Satellite Program (DMSP)."""

import numpy as np
import xarray as xr

import GeospaceDataManagement as gdm


def references(name):
    """Provide references for the DMSP instruments and experiments.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    refs : str
        String providing reference guidenance for the DMSP data

    """
    refs = {'ivm': ' '.join(('F. J. Rich, Users Guide for the Topside',
                             'Ionospheric Plasma Monitor (SSIES, SSIES-2 and',
                             'SSIES-3) on Spacecraft of the Defense',
                             'Meteorological Satellite Program (Air Force',
                             'Phillips Laboratory, Hanscom AFB, MA, 1994),',
                             'Vol. 1, p. 25.')),
            'ssj': ''.join(['Gussenhoven, M. S., D. A. Hardy and W. J. Burke, ',
                            'DMSP/F2 electron observations of equatorward ',
                            'auroral boundaries and their relationship to ',
                            'magnetospheric electric fields, J. Geophys. Res.,',
                            ' 86, 768-778, 1981.\nGussenhoven, M. S., D. A. ',
                            'Hardy and N. Heinemann, Systematics of the ',
                            'equatorward diffuse auroral boundary, J. Geophys.',
                            ' Res., 88, 5692-5708, 1983.\nHardy, D. A., E. ',
                            'G. Holeman, W. J. Burke, L. C. Gentile and K. H. ',
                            'Bounar (2008), Probability distributions of ',
                            'electron precipitation at high magnetic latitudes',
                            ', Journal of Geophysical Research, Volume 113, ',
                            'Issue A6, doi10.1029/2007JA012746.'])}

    return refs[name]


def smooth_ram_drifts(inst, rpa_flag_key=None, rpa_flag_max=1,
                      rpa_vel_key='ion_v_sat_for', smooth_key=None,
                      roll_window=15, roll_kwargs=None, desc_label='desc'):
    """Smooth the ram drifts using a rolling mean.

    Parameters
    ----------
    inst : gdm.Instrument
        DMSP IVM Instrument object
    rpa_flag_key : str or NoneType
        RPA flag key, if None then no data is selected. The UTD RPA flag key
        is 'rpa_flag_ut' (default=None)
    rpa_flag_max : int
        Maximum allowable RPA flag (default=1)
    rpa_vel_key : str
        RPA velocity data key (default='ion_v_sat_for')
    smooth_key : str or NoneType
        If None will fill old RPA data with smoothed data, otherwise assigns
        the smoothed data to this new variable
    roll_window : int, offset, or BaseIndexer subclass
        Size of the moving window (default=15)
    roll_kwargs : dict or NoneType
        Keyword args for rolling mean window.  If None uses {'min_periods': 5}
        (default=None)
    desc_label : str
        Meta data label for descrption (default='desc')

    Raises
    ------
    KeyError
        If unknown values are used for `rpa_flag_key` or `rpa_vel_key`

    See Also
    --------
    xr.Dataset.rolling

    """
    # Select the desired data for averaging
    if rpa_flag_key is None:
        rpa_idx = list()
    else:
        rpa_idx, = np.where(inst[rpa_flag_key] <= rpa_flag_max)

    # Smooth the data, if there is any data to smooth
    if len(rpa_idx) > 0:
        if roll_kwargs is None:
            roll_kwargs = {'min_periods': 5}

        roll_kwargs.update({inst.index.name: roll_window})

        smooth = inst[rpa_idx, rpa_vel_key].rolling(**roll_kwargs).mean(
            skipna=True)
    else:
        smooth = np.full(shape=inst.index.shape, fill_value=np.nan)

        if smooth_key is None:
            smooth = smooth[rpa_idx]

    # Assign the smoothed data
    if smooth_key is None:
        inst[rpa_idx, rpa_vel_key] = smooth
        smooth_key = rpa_vel_key
    else:
        inst[smooth_key] = smooth
        inst[smooth_key].attrs = inst[rpa_vel_key].attrs

    # Update the meta data
    desc = 'Rolling mean of window {:d} and {:} for {:s}'.format(
        roll_window, roll_kwargs, 'no data selected' if rpa_flag_key is None
        else 'RPA flag data <= {:d}'.format(rpa_flag_max))
    inst[smooth_key].attrs[desc_label] = desc

    return


def update_DMSP_ephemeris(inst, ephem=None):
    """Update DMSP instrument data with improved DMSP ephemeris.

    Parameters
    ----------
    inst : gdm.Instrument
       DMSP IVM Instrument object
    ephem : gdm.Instrument or NoneType
        DMSP IVM_EPHEM instrument object

    """
    # Ensure the right ephemera is loaded
    if ephem is None:
        gdm.logger.info('No ephemera provided for {:}'.format(inst.date))
        inst.data = xr.Dataset()
        return

    if ephem.inst_id != inst.inst_id:
        raise ValueError('ephemera provided for the wrong satellite')

    if ephem.date != inst.date:
        ephem.load(date=inst.date, verifyPad=True)

    # Ensure the correct satellite and time have ephemeris data
    if ephem.empty:
        gdm.logger.info('unable to load ephemera for {:}'.format(inst.date))
        inst.data = xr.Dataset()
        return

    # Interpolate the ephemeris to the time resolution of the measurements
    ephem.data = ephem.data.interp_like(inst.data)

    # Update the DMSP instrument
    inst['mlt'] = ephem['SC_AACGM_LTIME']
    inst['mlat'] = ephem['SC_AACGM_LAT']

    return


def add_drift_unit_vectors(inst, unit_label='units', name_label='name',
                           min_label='min_val', max_label='max_val',
                           desc_label='desc', fill_label='fill_val'):
    """Add unit vectors for expressing plasma motion at high latitudes.

    Parameters
    ----------
    inst : gdm.Instrument
        DMSP IVM Instrument object
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for name (default='name')
    min_label : str
        Meta data label for min value (default='min_val')
    max_label : str
        Meta data label for max value (default='max_val')
    desc_label : str
        Meta data label for descrption (default='desc')
    fill_label : str
        Meta data label for fill value (default='fill_val')

    Notes
    -----
    Assumes that the RAM vector is pointed perfectly forward. Expresses the
    satellite ram and crosstrack directions along x (points along 6 MLT)
    and y (points along 12 MLT) unit vectors. Also expresses the same
    parameters along polar coordinate directions, r (origin at magnetic pole)
    and theta (theta=0 points along x). Adds variables `unit_ram_x`,
    `unit_ram_y`, `unit_cross_x`, `unit_cross_y`, `unit_ram_r`,
    `unit_ram_theta`, `unit_cross_r`, `unit_cross_theta`.

    """
    def swap_sign(data):
        data['unit_cross_x'] = -1.0 * data['unit_cross_x']
        data['unit_cross_y'] = -1.0 * data['unit_cross_y']

    # Calculate theta and R in radians from MLT and MLat, respectively
    theta = inst['mlt'] * (np.pi / 12.0) - np.pi * 0.5
    r = np.radians(90.0 - np.abs(inst['mlat']))

    # Determine the positions in cartesian coordinates
    pos_x = r * np.cos(theta)
    pos_y = r * np.sin(theta)
    diff_x = pos_x.diff(inst.index.name)
    diff_y = pos_y.diff(inst.index.name)
    norm = np.sqrt(diff_x**2 + diff_y**2)

    # Calculate the RAM and cross-track unit vectors in cartesian and polar
    # coordinates.
    # x points along MLT = 6, y points along MLT = 12
    inst['unit_ram_x'] = diff_x / norm
    inst['unit_ram_y'] = diff_y / norm
    inst['unit_cross_x'] = -diff_y / norm
    inst['unit_cross_y'] = diff_x / norm
    inst.data = inst.data.where(inst['mlat'] >= 0, other=swap_sign)

    inst['unit_ram_r'] = (inst['unit_ram_x'] * np.cos(theta)
                          + inst['unit_ram_y'] * np.sin(theta))
    inst['unit_ram_theta'] = (-inst['unit_ram_x'] * np.sin(theta)
                              + inst['unit_ram_y'] * np.cos(theta))

    inst['unit_cross_r'] = (inst['unit_cross_x'] * np.cos(theta)
                            + inst['unit_cross_y'] * np.sin(theta))
    inst['unit_cross_theta'] = (-inst['unit_cross_x'] * np.sin(theta)
                                + inst['unit_cross_y'] * np.cos(theta))

    # Add meta data, ram drift, x-y
    desc = ''.join(['Unit vector for the satellite ram direction, polar x',
                    ' component. Origin at magnetic pole, points toward ',
                    '6 MLT.'])
    meta_dict = {unit_label: '', name_label: 'Unit Vector - ram - x',
                 desc_label: desc, fill_label: np.nan, min_label: -1.0,
                 max_label: 1.0}
    inst['unit_ram_x'].attrs = meta_dict

    desc = ''.join(['Unit vector for the satellite ram direction, polar y ',
                    'component. Origin at magnetic pole, points toward ',
                    '12 MLT.'])
    meta_dict[desc_label] = desc
    meta_dict[name_label] = 'Unit Vector - ram - y'
    inst['unit_ram_y'].attrs = meta_dict

    # Cross-track metadata, x-y
    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar x component. Origin at magnetic pole, ',
                    'points toward 6 MLT.'])
    meta_dict = {unit_label: '', desc_label: desc,
                 name_label: 'Unit Vector - cross - x',
                 fill_label: np.nan, min_label: -1.0, max_label: 1.0}
    inst['unit_cross_x'].attrs = meta_dict

    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar y component. Origin at magnetic pole, ',
                    'points toward 12 MLT.'])
    meta_dict[desc_label] = desc
    meta_dict[name_label] = 'Unit Vector - cross - y'
    inst['unit_cross_y'].attrs = meta_dict

    # Ram metadata, polar coords
    desc = ''.join(['Unit vector for the satellite ram direction, polar radial',
                    ' component. Origin at magnetic pole.'])
    meta_dict = {unit_label: '', name_label: 'Unit Vector - ram - r',
                 desc_label: desc, fill_label: np.nan, min_label: -1.0,
                 max_label: 1.0}
    inst['unit_ram_r'].attrs = meta_dict

    desc = ''.join(['Unit vector for the satellite ram direction, polar theta ',
                    'component. Origin at magnetic pole.'])
    meta_dict[desc_label] = desc
    meta_dict[name_label] = 'Unit Vector - ram - theta'
    inst['unit_ram_theta'].attrs = meta_dict

    # Cross-track metadata, polar coords
    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar radial component. Origin at magnetic pole.'])
    meta_dict = {unit_label: '', name_label: 'Unit Vector - cross - r',
                 desc_label: desc, fill_label: np.nan, min_label: -1.0,
                 max_label: 1.0}
    inst['unit_cross_r'].attrs = meta_dict

    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar theta component. Origin at magnetic pole.'])
    meta_dict[desc_label] = desc
    meta_dict[name_label] = 'Unit Vector - cross - theta'
    inst['unit_cross_theta'].attrs = meta_dict

    return


def add_drifts_polar_cap_x_y(inst, rpa_flag_key=None,
                             rpa_vel_key='ion_v_sat_for',
                             cross_vel_key='ion_v_sat_left',
                             unit_label='units', name_label='name',
                             min_label='min_val', max_label='max_val',
                             desc_label='desc', fill_label='fill_val',
                             note_label='notes'):
    """Add polar cap drifts in cartesian coordinates.

    Parameters
    ----------
    inst : gdm.Instrument
        DMSP IVM Instrument object
    rpa_flag_key : string or NoneType
        RPA flag key, if None will not select any data. The UTD RPA flag key
        is 'rpa_flag_ut' (default=None)
    rpa_vel_key : string
        RPA velocity data key (default='ion_v_sat_for')
    cross_vel_key : string
        Cross-track velocity data key (default='ion_v_sat_left')
    unit_label : str
        Meta data label for units (default='units')
    name_label : str
        Meta data label for name (default='name')
    min_label : str
        Meta data label for min_value (default='min_val')
    max_label : str
        Meta data label for max value (default='max_val')
    desc_label : str
        Meta data label for descrption (default='desc')
    fill_label : str
        Meta data label for fill value (default='fill_val')
    note_label : str
        Meta data label for notes (default='notes')

    Notes
    -----
    Polar cap drifts assume there is no vertical component to the X-Y
    velocities.

    x points along same direction as from magnetic pole towards 6 MLT, and
    y points along same direction as from magnetic pole towards 12 MLT.

    Adds 'ion_vel_pc_x', 'ion_vel_pc_y', and 'partial'.  The last data key
    indicates whether RPA data was available (False) or not (True).

    """
    # Get the good RPA data, if available
    if rpa_flag_key in list(inst.data.keys()):
        rpa_idx, = np.where(inst[rpa_flag_key] != 1)
    else:
        rpa_idx = list()

    # Use the cartesian unit vectors to calculate the desired velocities
    iv_x = inst[rpa_vel_key].copy()
    iv_x[rpa_idx] = 0.0

    # Check to see if unit vectors have been created
    if 'unit_ram_y' not in list(inst.data.keys()):
        add_drift_unit_vectors(inst)

    # Calculate the velocities
    inst['ion_vel_pc_x'] = (iv_x * inst['unit_ram_x']
                            + inst[cross_vel_key] * inst['unit_cross_x'])
    inst['ion_vel_pc_y'] = (iv_x * inst['unit_ram_y']
                            + inst[cross_vel_key] * inst['unit_cross_y'])

    # Add meta data
    desc = ''.join(['Ion velocity along the polar cap "{}" direction,',
                    'which points from the magnetic pole towards {:02d} MLT.'])
    notes = ''.join(['Generated by combining plasma drift measurements ',
                     'from the RPA and DM along the "x" or "y" polar cap ',
                     'directions, as appropriate.'])
    if unit_label in inst[cross_vel_key].attrs:
        units = inst[cross_vel_key].attrs[unit_label]
    else:
        units = ''

    inst['ion_vel_pc_x'].attrs = {
        unit_label: units, name_label: 'Ion Velocity - Polar Cap - x',
        desc_label: desc.format('x', 6), fill_label: np.nan,
        min_label: -np.inf, max_label: np.inf, note_label: notes}

    inst['ion_vel_pc_y'].attrs = {
        unit_label: units, name_label: 'Ion Velocity - Polar Cap - y',
        desc_label: desc.format('y', 12), fill_label: np.nan,
        min_label: -np.inf, max_label: np.inf, note_label: notes}

    # Flag the velocities as full (False) or partial (True)
    inst['partial'] = False
    inst[rpa_idx, 'partial'] = True

    desc = ''.join(['True if reported measurement is incomplete as it only ',
                    'has contributions from either the RPA or DM, not both.'])
    inst['partial'].attrs = {
        unit_label: '', name_label: 'Partial Vector Flag', desc_label: desc,
        fill_label: np.nan, min_label: False, max_label: True}

    return
