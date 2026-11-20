#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# Original Authors: pysat development team (c) 2016, Russell Stoneback
#                   pysat development team (c) 2020, pysat
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Tests the `gdm.utils.coords` functions."""

import datetime as dt
import logging
import numpy as np
import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import coords
from GeospaceDataManagement.utils.meta import default_fill_values_from_type
from GeospaceDataManagement.utils import testing


class TestCyclicData(object):
    """Unit tests for the `adjust_cyclic_data` function."""

    def setup_method(self):
        """Set up the unit test environment."""
        self.ref_angles = np.array([340.0, 348.0, 358.9, 0.5, 5.0, 9.87])
        return

    def teardown_method(self):
        """Clean up the unit test environment."""
        del self.ref_angles
        return

    def test_adjust_cyclic_data_default(self):
        """Test adjust_cyclic_data with default range."""

        ref_rad = np.radians(self.ref_angles) - np.pi
        ref_angles = coords.adjust_cyclic_data(ref_rad)

        assert ref_angles.max() < 2.0 * np.pi
        assert ref_angles.min() >= 0.0
        return

    def test_adjust_cyclic_data_extended_range(self):
        """Test adjust_cyclic_data that deviate by more than one range."""

        ref_rad = np.radians(self.ref_angles) - 9.0 * np.pi
        ref_angles = coords.adjust_cyclic_data(ref_rad)

        assert ref_angles.max() < 2.0 * np.pi
        assert ref_angles.min() >= 0.0
        return

    def test_adjust_cyclic_data_custom(self):
        """Test adjust_cyclic_data with a custom range."""

        ref_angles = coords.adjust_cyclic_data(self.ref_angles,
                                               high=180.0, low=-180.0)

        assert ref_angles.max() < 180.0
        assert ref_angles.min() >= -180.0
        return


class TestUpdateLon(object):
    """Unit tests for the `update_longitude` function."""

    def setup_method(self):
        """Set up the unit test environment."""
        self.inst = None
        self.inst_time = gdm.instruments.gdm_testing._test_dates['']['']
        return

    def teardown_method(self):
        """Clean up the unit test environment."""
        del self.inst, self.inst_time
        return

    @pytest.mark.parametrize("name", ["testing", "ndtesting", "testmodel"])
    def test_update_longitude(self, name):
        """Test `update_longitude` successful run."""

        self.inst = gdm.Instrument(platform='gdm', name=name)
        self.inst.load(date=self.inst_time)

        # Test instruments initially define longitude between 0-360 deg
        assert np.all(self.inst.data['longitude'] < 360.0)
        assert np.all(self.inst.data['longitude'] >= 0.0)

        # Longitude defaults to updating range from -180 to 180 deg
        coords.update_longitude(self.inst, lon_name="longitude")

        assert np.all(self.inst.data['longitude'] < 180.0)
        assert np.all(self.inst.data['longitude'] >= -180.0)
        return

    def test_bad_lon_name_update_longitude(self):
        """Test update_longitude with a bad longitude name."""

        self.inst = gdm.Instrument(platform='gdm', name="testing")
        self.inst.load(date=self.inst_time)

        testing.eval_bad_input(coords.update_longitude, ValueError,
                               "unknown longitude variable name",
                               [self.inst], {'lon_name': "not longitude"})

        return


class TestCalcSLT(object):
    """Unit tests for `calc_solar_local_time`.

    Notes
    -----
    Includes integration tests with `update_longitude`.

    """

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.inst = None
        self.inst_time = gdm.instruments.gdm_testing._test_dates['']['']
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.inst, self.inst_time
        return

    @pytest.mark.parametrize("name", ["testing", "ndtesting"])
    def test_calc_solar_local_time(self, name):
        """Test SLT calculation with longitudes from 0-360 deg for 0 UTH."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name, num_samples=1)
        self.inst.load(date=self.inst_time)

        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt')

        # This works because test instrument longitude ranges from 0-360 deg.
        # Testing the difference in periodic space to guard against changes
        # in numerical precision across platforms.
        diff = abs(self.inst['slt'].values
                   - self.inst['longitude'].values / 15.0)
        diff_radians = diff * np.pi / 12.0
        sin_diff = np.sin(diff_radians)
        cos_diff = np.cos(diff_radians)
        assert np.max(np.abs(sin_diff)) < 1.0e-6
        assert np.min(np.abs(cos_diff)) > 1.0 - 1.0e-6
        return

    @pytest.mark.parametrize("name", ["testing", "ndtesting"])
    def test_calc_solar_local_time_inconsistent_keywords(self, name, caplog):
        """Test that ref_date only works when apply_modulus=False."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name, num_samples=1)
        self.inst.load(date=self.inst_time)

        # Apply solar local time method and capture logging output
        with caplog.at_level(logging.INFO, logger='GeospaceDataManagement'):
            coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                         slt_name='slt',
                                         ref_date=self.inst.date,
                                         apply_modulus=True)
        captured = caplog.text

        # Confirm we have the correct informational message
        assert captured.find('Keyword `ref_date` only supported if') >= 0
        return

    def test_calc_solar_local_time_w_neg_longitude(self):
        """Test calc_solar_local_time with longitudes from -180 to 180 deg."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name="testing")
        self.inst.load(date=self.inst_time)

        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt')
        coords.update_longitude(self.inst, lon_name="longitude", low=-180.0,
                                high=180.0)
        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt2')

        # Test the output agrees to an acceptable tolerance
        assert (abs(self.inst['slt'] - self.inst['slt2'])).max() < 1.0e-6
        return

    def test_bad_lon_name_calc_solar_local_time(self):
        """Test raises ValueError with a bad longitude name."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name="testing")
        self.inst.load(date=self.inst_time)

        # Test that the correct Exception and error message are raised
        testing.eval_bad_input(coords.calc_solar_local_time, ValueError,
                               "unknown longitude variable name",
                               [self.inst], {"lon_name": "not longitude",
                                             "slt_name": 'slt'})

        return

    @pytest.mark.parametrize("name", ["testmodel", "ndtesting"])
    def test_lon_broadcasting_calc_solar_local_time(self, name):
        """Test calc_solar_local_time with longitude coordinates."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name)
        self.inst.load(date=self.inst_time)
        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt')

        # Test the output range
        assert self.inst['slt'].max() < 24.0
        assert self.inst['slt'].min() >= 0.0
        return

    @pytest.mark.parametrize("name", ["testmodel", "ndtesting"])
    def test_lon_broadcasting_calc_solar_local_time_no_mod_multiday(self, name):
        """Test non modulated solar local time output for a 2 day range."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name)
        self.inst.load(date=self.inst_time,
                       end_date=self.inst_time + dt.timedelta(days=2))
        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt', apply_modulus=False)

        # Test the output range
        assert self.inst['slt'].max() > 48.0
        assert self.inst['slt'].max() < 72.0
        assert self.inst['slt'].min() >= 0.0
        return

    @pytest.mark.parametrize("name", ["testmodel", "ndtesting"])
    def test_lon_broadcasting_calc_solar_local_time_no_mod_ref_date(self, name):
        """Test non modulated SLT output for a 2 day range with a ref date."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name)
        self.inst.load(date=self.inst_time, end_date=self.inst_time
                       + dt.timedelta(days=2))
        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt', apply_modulus=False,
                                     ref_date=self.inst_time
                                     - dt.timedelta(days=1))

        # Test the output range
        assert self.inst['slt'].max() > 72.0
        assert self.inst['slt'].max() < 96.0
        assert self.inst['slt'].min() >= 24.0
        return

    @pytest.mark.parametrize("name", ["testmodel", "ndtesting"])
    def test_lon_broadcasting_calc_solar_local_time_no_mod(self, name):
        """Test SLT calc with longitude coordinates and no modulus."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name=name)
        self.inst.load(date=self.inst_time)
        coords.calc_solar_local_time(self.inst, lon_name="longitude",
                                     slt_name='slt', apply_modulus=False)

        # Test the output range
        assert self.inst['slt'].max() > 24.0
        assert self.inst['slt'].max() < 48.0
        assert self.inst['slt'].min() >= 0.0
        return

    def test_single_lon_calc_solar_local_time(self):
        """Test calc_solar_local_time with a single longitude value."""

        # Instantiate instrument and load data
        self.inst = gdm.Instrument(platform='gdm', name="ndtesting")
        self.inst.load(date=self.inst_time)
        lon_name = 'lon2'

        # Create a second longitude with a single value
        out = self.inst.data.update({lon_name: (lon_name, [10.0])})
        if out is not None:
            self.inst.data = out

        self.inst.data = self.inst.data.squeeze(dim=lon_name)

        # Calculate and test the SLT
        coords.calc_solar_local_time(self.inst, lon_name=lon_name,
                                     slt_name='slt')

        assert self.inst['slt'].max() < 24.0
        assert self.inst['slt'].min() >= 0.0
        assert self.inst['slt'].shape == self.inst.index.shape
        return


class TestEstCommonCoord(object):
    """Unit tests for the `establish_common_coord` function."""

    def setup_method(self):
        """Set up the unit test environment."""
        self.res = 1.0
        self.long_coord = np.arange(0, 360, self.res)
        self.short_coord = np.arange(10, 350, 10.0 * self.res)
        return

    def teardown_method(self):
        """Clean up the unit test environment."""
        del self.long_coord, self.short_coord, self.res
        return

    def test_establish_common_coord_overlap(self):
        """Test `establish_common_coord` with common=True."""

        out = coords.establish_common_coord([self.long_coord, self.short_coord])
        out_res = np.unique(out[1:] - out[:-1])

        assert self.short_coord.min() == out.min(), "unexpected minimum value"
        assert self.short_coord.max() == out.max(), "unexpected maximum value"
        assert len(out_res) == 1, "inconsistend coordinate resolution"
        assert out_res[0] == self.res, "unexpected coordinate resolution"
        return

    def test_establish_common_coord_max_range(self):
        """Test `establish_common_coord` with common=False."""

        out = coords.establish_common_coord([self.short_coord, self.long_coord],
                                            common=False)
        out_res = np.unique(out[1:] - out[:-1])

        assert self.long_coord.min() == out.min(), "unexpected minimum value"
        assert self.long_coord.max() == out.max(), "unexpected maximum value"
        assert len(out_res) == 1, "inconsistend coordinate resolution"
        assert out_res[0] == self.res, "unexpected coordinate resolution"
        return

    def test_establish_common_coord_single_val(self):
        """Test `establish_common_coord` where one coordinate is a value."""

        out = coords.establish_common_coord([self.short_coord[0],
                                             self.long_coord], common=False)
        out_res = np.unique(out[1:] - out[:-1])

        assert self.long_coord.min() == out.min(), "unexpected minimum value"
        assert self.long_coord.max() == out.max(), "unexpected maximum value"
        assert len(out_res) == 1, "inconsistend coordinate resolution"
        assert out_res[0] == self.res, "unexpected coordinate resolution"
        return

    def test_establish_common_coord_single_val_only(self):
        """Test `establish_common_coord` where tje coordinate is a value."""

        out = coords.establish_common_coord([self.short_coord[0]])

        assert self.short_coord[0] == out[0], "unexpected value"
        assert len(out) == 1, "unexpected coordinate length"
        return


class TestExpandXarrayDims(object):
    """Unit tests for the `expand_xarray_dims` function."""

    def setup_method(self):
        """Set up the unit test environment."""
        self.test_inst = gdm.Instrument(
            inst_module=gdm.instruments.gdm_ndtesting)
        self.start_time = gdm.instruments.gdm_ndtesting._test_dates['']['']
        self.data_list = []
        self.out = None
        return

    def teardown_method(self):
        """Clean up the unit test environment."""
        del self.test_inst, self.start_time, self.data_list, self.out
        return

    def set_data_meta(self, dims_equal):
        """Set the input data list and meta data.

        Parameters
        ----------
        dims_equal : bool
            If True, the dimension variables for the data sets should be the
            same; if False they should have different dimensions apart from
            the 'time' dimension

        """

        self.test_inst.load(date=self.start_time)
        self.data_list.append(self.test_inst.data)

        # The second data set should have half the time samples
        num_samples = int(self.test_inst.index.shape[0] / 2)

        if dims_equal:
            # Load a second data set with half the time samples
            self.test_inst = gdm.Instrument(
                inst_module=self.test_inst.inst_module,
                num_samples=num_samples)
        else:
            # Load a second data set with different dimensions apart from time
            self.test_inst = gdm.Instrument(
                inst_module=gdm.instruments.gdm_testmodel,
                num_samples=num_samples)

        self.test_inst.load(date=self.start_time + dt.timedelta(days=1))
        self.data_list.append(self.test_inst.data)

        return

    def eval_dims(self, dims_equal, exclude_dims=None):
        """Set the input data list and meta data.

        Parameters
        ----------
        dims_equal : bool
            If True, the dimension variables for the data sets should be the
            same; if False they should have different dimensions apart from
            the 'time' dimension
        exclude_dims : list-like or NoneType
            A list of dimensions that have the same name, but can have different
            values or None if all the dimensions with the same name should
            have the same shape. (default=None)

        """
        if exclude_dims is None:
            exclude_dims = []

        # Define the reference Dataset
        ref_dims = list(self.out[0].sizes.keys())

        # Cycle through the remaining Datasets
        for i, xdata in enumerate(self.out[1:]):
            test_dims = list(xdata.sizes.keys())

            # Test that the expected dimension names overlap between datasets
            if dims_equal:
                testing.assert_lists_equal(test_dims, ref_dims)
            else:
                for tdim in test_dims:
                    assert (tdim == 'time' if tdim in ref_dims else tdim
                            != 'time'), "unexpected dimension: {:}".format(tdim)

            # Test the dimensions shapes for expected (lack of) differences
            for tdim in test_dims:
                if tdim in ref_dims:
                    if tdim in exclude_dims:
                        assert xdata[tdim].shape != self.out[0][tdim].shape
                    else:
                        assert xdata[tdim].shape == self.out[0][tdim].shape

                        if xdata[tdim].shape != self.data_list[
                                i + 1][tdim].shape:
                            # This data set is smaller, test for fill values
                            for dvar in xdata.data_vars.keys():
                                if tdim in xdata[dvar].dims:
                                    if 'fill_val' in xdata[dvar].attrs:
                                        fval = xdata[dvar].attrs['fill_val']
                                    else:
                                        fval = default_fill_values_from_type(
                                            xdata[dvar].dtype.type)
                                    try:
                                        if np.isnan(fval):
                                            assert np.isnan(
                                                xdata[dvar].values).any()
                                        else:
                                            assert np.any(xdata[dvar].values
                                                          == fval)
                                    except TypeError:
                                        # This is a string or object
                                        estr = "".join([
                                            "Bad or missing fill values for ",
                                            dvar, ": ({:} not in {:})".format(
                                                fval, xdata[dvar].values)])
                                        if fval is None:
                                            assert fval in xdata[
                                                dvar].values, estr
                                        else:
                                            assert np.any(xdata[dvar].values
                                                          == fval), estr

        return

    @pytest.mark.parametrize('dims_equal', [True, False])
    @pytest.mark.parametrize('exclude_dims', [None, ['time']])
    def test_expand_xarray_dims(self, dims_equal, exclude_dims):
        """Test successful padding of dimensions for xarray data.

        Parameters
        ----------
        dims_equal : bool
            If True, the dimension variables for the data sets should be the
            same; if False they should have different dimensions apart from
            the 'time' dimension
        exclude_dims : list-like or NoneType
            A list of dimensions that have the same name, but can have different
            values or None if all the dimensions with the same name should
            have the same shape. (default=None)

        """

        # Set the input parameters
        self.set_data_meta(dims_equal)

        # Run the dimension expansion
        self.out = coords.expand_xarray_dims(self.data_list,
                                             dims_equal=dims_equal,
                                             exclude_dims=exclude_dims)

        # Test the results
        self.eval_dims(dims_equal, exclude_dims)

        return

    @pytest.mark.parametrize('new_data_type', [int, float, str, bool, None])
    def test_missing_meta(self, new_data_type):
        """Test success if variable is missing from meta.

        Parameters
        ----------
        new_data_type : type
            Data type for the new data that will be missing from `self.meta`

        """

        # Set the input parameters
        self.set_data_meta(True)

        # Add a data variable to one of the data sets
        self.data_list[1]['new_variable'] = self.data_list[1]['mlt'].astype(
            new_data_type)

        # Run the dimension expansion
        self.out = coords.expand_xarray_dims(self.data_list, dims_equal=True)

        # Test the results
        self.eval_dims(True)

        return


class TestGeodeticGeocentric(object):
    """Unit tests for geodetic to geocentric conversion methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.val = {'lat': 45.0, 'lon': 8.0, 'az': 52.0, 'el': 63.0}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [44.8075768, 8.0, 6367.48954386]),
                              ({'inverse': False},
                               [44.8075768, 8.0, 6367.48954386]),
                              ({'inverse': True},
                               [45.1924232, 8.0, 6367.3459085])])
    def test_geodetic_to_geocentric(self, kwargs, target):
        """Test conversion from geodetic to geocentric coordinates."""
        self.out = coords.geodetic_to_geocentric(self.val['lat'],
                                                 lon_in=self.val['lon'],
                                                 **kwargs)

        for i, self.loc in enumerate(self.out):
            assert np.all(abs(self.loc - target[i]) < 1.0e-6)
            if isinstance(self.loc, np.ndarray):
                assert self.loc.shape == self.val['lat'].shape, \
                    "mismatched output shape: {:} != {:}".format(
                        self.loc.shape, self.val['lat'].shape)
        return

    def test_geodetic_to_geocentric_and_back(self):
        """Test the reversibility of geodetic to geocentric conversions."""
        self.out = coords.geodetic_to_geocentric(self.val['lat'],
                                                 lon_in=self.val['lon'],
                                                 inverse=False)
        self.loc = coords.geodetic_to_geocentric(self.out[0],
                                                 lon_in=self.out[1],
                                                 inverse=True)
        assert np.all(abs(self.val['lat'] - self.loc[0]) < 1.0e-6), "bad lat"
        assert np.all(abs(self.val['lon'] - self.loc[1]) < 1.0e-6), "bad lon"
        return

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [44.8075768, 8.0, 6367.48954386,
                                    51.7037677, 62.8811403]),
                              ({'inverse': False},
                               [44.8075768, 8.0, 6367.48954386,
                                51.7037677, 62.8811403]),
                              ({'inverse': True},
                               [45.1924232, 8.0, 6367.3459085,
                                52.2989610, 63.1180720])])
    def test_geodetic_to_geocentric_horizontal(self, kwargs, target):
        """Test conversion from geodetic to geocentric coordinates."""
        self.out = coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                            self.val['lon'],
                                                            self.val['az'],
                                                            self.val['el'],
                                                            **kwargs)

        for i, self.loc in enumerate(self.out):
            assert np.all(abs(self.loc - target[i]) < 1.0e-6)
            if isinstance(self.loc, np.ndarray):
                assert self.loc.shape == self.val['lat'].shape, \
                    "mismatched output shape: {:} != {:}".format(
                        self.loc.shape, self.val['lat'].shape)
        return

    def test_geodetic_to_geocentric_horizontal_and_back(self):
        """Test the reversibility of geodetic to geocentric horiz conversions.

        Note
        ----
        Inverse of az and el angles currently non-functional

        """
        self.out = coords.geodetic_to_geocentric_horizontal(self.val['lat'],
                                                            self.val['lon'],
                                                            self.val['az'],
                                                            self.val['el'],
                                                            inverse=False)
        self.loc = coords.geodetic_to_geocentric_horizontal(self.out[0],
                                                            self.out[1],
                                                            self.out[3],
                                                            self.out[4],
                                                            inverse=True)

        assert np.all(abs(self.val['lat'] - self.loc[0]) < 1.0e-6), "bad lat"
        assert np.all(abs(self.val['lon'] - self.loc[1]) < 1.0e-6), "bad lon"
        assert np.all(abs(self.val['az'] - self.loc[3]) < 1.0e-6), "bad az"
        assert np.all(abs(self.val['el'] - self.loc[4]) < 1.0e-6), "bad el"
        return


class TestGeodeticGeocentricArray(TestGeodeticGeocentric):
    """Unit tests for geodetic to geocentric array conversion."""

    def setup_method(self):
        """Create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'lat': 45.0 * arr,
                    'lon': 8.0 * arr,
                    'az': 52.0 * arr,
                    'el': 63.0 * arr}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return


class TestSphereCartesian(object):
    """Unit tests for spherical/cartesian conversions."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.val = {'az': 45.0, 'el': 30.0, 'r': 1.0,
                    'x': 0.6123724356957946,
                    'y': 0.6123724356957946,
                    'z': 0.5}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return

    @pytest.mark.parametrize("kwargs,input,target",
                             [({}, ['az', 'el', 'r'],
                               ['x', 'y', 'z']),
                              ({'inverse': False}, ['az', 'el', 'r'],
                               ['x', 'y', 'z']),
                              ({'inverse': True}, ['x', 'y', 'z'],
                               ['az', 'el', 'r'])])
    def test_spherical_to_cartesian(self, kwargs, input, target):
        """Test conversion from spherical to cartesian coordinates."""
        self.out = coords.spherical_to_cartesian(self.val[input[0]],
                                                 self.val[input[1]],
                                                 self.val[input[2]],
                                                 **kwargs)

        for i, self.loc in enumerate(self.out):
            assert np.all(abs(self.loc - self.val[target[i]]) < 1.0e-6)
            if isinstance(self.loc, np.ndarray):
                assert self.loc.shape == self.val[input[0]].shape, \
                    "mismatched output shape: {:} != {:}".format(
                        self.loc.shape, self.val[input[0]].shape)
        return

    def test_spherical_to_cartesian_and_back(self):
        """Test the reversibility of spherical to cartesian conversions."""
        self.out = coords.spherical_to_cartesian(self.val['x'], self.val['y'],
                                                 self.val['z'], inverse=True)
        self.out = coords.spherical_to_cartesian(self.out[0], self.out[1],
                                                 self.out[2], inverse=False)

        assert np.all(abs(self.val['x'] - self.out[0]) < 1.0e-6), "bad x"
        assert np.all(abs(self.val['y'] - self.out[1]) < 1.0e-6), "bad y"
        assert np.all(abs(self.val['z'] - self.out[2]) < 1.0e-6), "bad z"
        return


class TestSphereCartesianArray(TestSphereCartesian):
    """Unit tests for spherical/cartesian coordinate conversion with arrays."""

    def setup_method(self):
        """Create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 45.0 * arr, 'el': 30.0 * arr, 'r': 1.0 * arr,
                    'x': 0.6123724356957946 * arr,
                    'y': 0.6123724356957946 * arr,
                    'z': 0.5 * arr}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return


class TestGlobalLocal(object):
    """Unit tests for global/local conversions."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.val = {'x': 7000.0, 'y': 8000.0, 'z': 9000.0,
                    'lat': 37.5, 'lon': 289.0, 'rad': 6380.0}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return

    @pytest.mark.parametrize("kwargs, target",
                             [({},
                               [9223.1752649, 10357.58863188, -5094.15562118]),
                              ({'inverse': False},
                               [9223.1752649, 10357.58863188, -5094.15562118]),
                              ({'inverse': True},
                               [9005.5925135, -4653.2653305, 15709.5775005])])
    def test_global_to_local_cartesian(self, kwargs, target):
        """Test conversion from global to local cartesian coordinates."""
        self.out = coords.global_to_local_cartesian(self.val['x'],
                                                    self.val['y'],
                                                    self.val['z'],
                                                    self.val['lat'],
                                                    self.val['lon'],
                                                    self.val['rad'],
                                                    **kwargs)

        for i, self.loc in enumerate(self.out):
            assert np.all(abs(self.loc - target[i]) < 1.0e-6)
            if isinstance(self.loc, np.ndarray):
                assert self.loc.shape == self.val['x'].shape, \
                    "shape mismatch: {:} != {:}".format(self.loc.shape,
                                                        self.val['x'].shape)
        return

    def test_global_to_local_cartesian_and_back(self):
        """Test the reversibility of the global to loc cartesian transform."""
        self.out = coords.global_to_local_cartesian(self.val['x'],
                                                    self.val['y'],
                                                    self.val['z'],
                                                    self.val['lat'],
                                                    self.val['lon'],
                                                    self.val['rad'],
                                                    inverse=False)
        self.out = coords.global_to_local_cartesian(self.out[0], self.out[1],
                                                    self.out[2],
                                                    self.val['lat'],
                                                    self.val['lon'],
                                                    self.val['rad'],
                                                    inverse=True)
        assert np.all(abs(self.val['x'] - self.out[0]) < 1.0e-6), "bad x"
        assert np.all(abs(self.val['y'] - self.out[1]) < 1.0e-6), "bad y"
        assert np.all(abs(self.val['z'] - self.out[2]) < 1.0e-6), "bad z"
        return


class TestGlobalLocalArray(TestGlobalLocal):
    """Unit tests for global/local conversion with arrays."""

    def setup_method(self):
        """Create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'x': 7000.0 * arr, 'y': 8000.0 * arr, 'z': 9000.0 * arr,
                    'lat': 37.5 * arr, 'lon': 289.0 * arr, 'rad': 6380.0 * arr}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return


class TestLocalHorizontalGlobal(object):
    """Tests for local horizontal to global geo and back."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.val = {'az': 30.0, 'el': 45.0, 'dist': 1000.0,
                    'lat': 45.0, 'lon': 0.0, 'alt': 400.0}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return

    @pytest.mark.parametrize("kwargs,target",
                             [({}, [49.62613564, 4.153673708, 7500.81015865]),
                              ({'geodetic': True},
                               [49.6261356, 4.153673708, 7500.81015865]),
                              ({'geodetic': False},
                               [49.60665778, 4.1652362, 7511.4633082])])
    def test_local_horizontal_to_global_geo(self, kwargs, target):
        """Tests the conversion of the local horizontal to global geo."""
        self.out = coords.local_horizontal_to_global_geo(self.val['az'],
                                                         self.val['el'],
                                                         self.val['dist'],
                                                         self.val['lat'],
                                                         self.val['lon'],
                                                         self.val['alt'],
                                                         **kwargs)

        for i, self.loc in enumerate(self.out):
            assert np.all(abs(self.loc - target[i]) < 1.0e-6)
            if isinstance(self.loc, np.ndarray):
                assert self.loc.shape == self.val['lat'].shape, \
                    "shape mismatch: {:} != {:}".format(self.loc.shape,
                                                        self.val['lat'].shape)
        return


class TestLocalHorizontalGlobalArray(TestLocalHorizontalGlobal):
    """Tests for local horizontal to global geo and back."""

    def setup_method(self):
        """Create a clean testing setup."""
        arr = np.ones(shape=(10,), dtype=float)
        self.val = {'az': 30.0 * arr, 'el': 45.0 * arr, 'dist': 1000.0 * arr,
                    'lat': 45.0 * arr, 'lon': 0.0 * arr, 'alt': 400.0 * arr}
        self.out = None
        self.loc = None
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.val, self.out, self.loc
        return
