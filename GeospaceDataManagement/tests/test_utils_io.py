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
"""Tests the utility I/O routines."""
import copy
import datetime as dt
import logging
import numpy as np
import os
import tempfile

import pandas as pds
import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import io
from GeospaceDataManagement.utils import testing

# Define `epoch_name` and `decode_times` for future changes in default values
default_epoch_name = 'time'
default_decode_times = False
decode_times = {'decode_times': default_decode_times}


class TestLoadNetCDF(object):
    """Unit tests for `utils.io.load_netcdf` and `utils.io.inst_to_netcdf`."""

    def setup_method(self):
        """Set up the test environment."""

        # Create temporary directory
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.saved_path = gdm.params['data_dirs']
        gdm.params['data_dirs'] = self.tempdir.name

        self.testInst = gdm.Instrument(platform='gdm', name='testing',
                                       num_samples=100, update_files=True)
        self.stime = gdm.instruments.gdm_testing._test_dates['']['']
        self.epoch_name = 'time'
        self.name_label = 'long_name'
        self.unit_label = 'units'

        # Initialize the loaded data
        self.loaded_inst = None
        return

    def teardown_method(self):
        """Clean up the test environment."""

        gdm.params['data_dirs'] = self.saved_path

        # Clear the attributes with data in them
        del self.loaded_inst, self.testInst, self.stime, self.epoch_name
        del self.name_label, self.unit_label

        # Remove the temporary directory
        self.tempdir.cleanup()

        # Clear the directory attributes
        del self.tempdir, self.saved_path
        return

    def eval_loaded_data(self, test_case=True):
        """Evaluate loaded test data.

        Parameters
        ----------
        test_case : bool
            Test the case of the data variable names (default=True)

        """
        # Test that the written and loaded data matches the initial data
        keys = [key for key in self.testInst.data.variables]
        new_keys = [key for key in self.loaded_inst.variables]

        # Test the data values for each variable
        for dkey in keys:
            assert np.all(self.testInst[dkey] == self.loaded_inst[dkey])

        # Check that names are lower case when written
        gdm.utils.testing.assert_lists_equal(keys, new_keys, test_case=False)
        return

    def test_basic_write_and_read_netcdf_mixed_case_data_format(self):
        """Test basic netCDF4 read/write with mixed case data variables."""
        # Create a bunch of files by year and doy
        outfile = os.path.join(self.tempdir.name, 'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)

        # Modify data names in data and don't apply to 'time'
        xarr_vars = io.xarray_vars_no_time(self.testInst.data)
        map_keys = {dkey: dkey.upper() for dkey in xarr_vars}
        self.testInst.data = self.testInst.data.rename(map_keys)

        # Write and read the output
        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        self.loaded_inst = io.load_netcdf(
            outfile, epoch_name=default_epoch_name, **decode_times)

        # Revert data names to meta case
        new_map_keys = {map_keys[mkey]: mkey
                        for mkey in self.testInst.meta_labels
                        if mkey in map_keys.keys()}
        self.testInst.data = self.testInst.data.rename(new_map_keys)

        # Test the loaded data
        self.eval_loaded_data(test_case=False)

        return

    @pytest.mark.parametrize("kwargs,target",
                             [({}, True),
                              ({'export_gdm_info': True}, True),
                              ({'export_gdm_info': False}, False)])
    def test_basic_write_and_read_netcdf_export_gdm_info(self, kwargs, target):
        """Test basic netCDF4 read/write with optional gdm info export.

        Parameters
        ----------
        kwargs : dict
            Specify value of `export_gdm_info`. An empty dict sets to
            default value.
        target : bool
            True indicates that gdm info should be written to the file.

        """
        # Create a bunch of files by year and doy
        outfile = os.path.join(self.tempdir.name, 'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)
        base_inst = gdm.Instrument()
        base_inst.references = ''
        base_inst.acknowledgements = ''

        io.inst_to_netcdf(self.testInst, base_instrument=base_inst,
                          fname=outfile, name_label=self.name_label,
                          unit_label=self.unit_label, **kwargs)

        self.loaded_inst = io.load_netcdf(
            outfile, epoch_name=default_epoch_name, **decode_times)

        for key in ['platform', 'name', 'tag', 'inst_id', 'acknowledgements',
                    'references']:
            assert (key in self.loaded_inst.attrs.keys()) == target, \
                "{:s}{:s} in {:}".format(
                    key, " not" if target else "",
                    repr(list(self.loaded_inst.attrs.keys())))

        return

    @pytest.mark.parametrize("add_path", [(''), ('unknown_dir')])
    def test_inst_write_and_read_netcdf(self, add_path):
        """Test Instrument netCDF4 read/write, including non-existent paths.

        Parameters
        ----------
        add_path : str
            Additional component to add to path to write to.

        """

        # Set the output file information
        file_root = 'gdm_test_ncdf_{year:04}{day:03}.nc'
        file_path = os.path.join(self.tempdir.name, add_path)
        outfile = self.stime.strftime(os.path.join(file_path,
                                                   'gdm_test_ncdf_%Y%j.nc'))

        # Load and write the test instrument data
        self.testInst.load(date=self.stime)
        self.testInst.to_netcdf4(fname=outfile, name_label=self.name_label,
                                 unit_label=self.unit_label)

        # Load the written file directly into an Instrument
        netcdf_inst = gdm.Instrument(
            'gdm', 'netcdf', data_dir=file_path, update_files=True,
            file_format=file_root, **decode_times)

        # Confirm data path is correct
        assert os.path.normpath(netcdf_inst.files.data_path) \
               == os.path.normpath(os.path.join(self.tempdir.name, add_path))

        # Deleting the test file here via os.remove(...) does work

        # Load data
        netcdf_inst.load(date=self.stime)

        # Test the loaded Instrument data
        self.loaded_inst = netcdf_inst.data
        self.eval_loaded_data()

        # Test the Instrument self-description
        for attr in ["platform", "name", "tag", "inst_id", "acknowledgements",
                     "references"]:
            assert getattr(self.testInst, attr) == getattr(netcdf_inst, attr), \
                "mismatched {:s} Instrument attribute".format(attr)

        # Test the metadata. The Instrument loaded from file will have
        # metadata for every variable with (possibly) different metadata types.
        # Do not test the attributes whose metadata are often changed by the
        # writing routine.
        tvars = [var for var in self.testInst.vars_no_time
                 if len(self.testInst[var].attrs) > 0]
        fvars = [var for var in netcdf_inst.vars_no_time
                 if len(netcdf_inst[var].attrs) > 0]

        testing.assert_list_contains(tvars, fvars)

        # Examine the meta data
        for var in tvars:
            # Not every variable is required to have every meta label
            assert len(netcdf_inst[var].attrs) == len(
                self.testInst[var].attrs), "".join([
                    "unequal amount of meta data for :", var])

            for attr in self.testInst[var].attrs:
                ival = self.testInst[var].attrs[attr]

                # If there is meta data, ensure it is the same
                assert attr in netcdf_inst[var].attrs, "".join([
                    "missing meta data [", attr, "=", repr(ival),
                    " not written to file for ", var])

                try:
                    assert ival == netcdf_inst[var].attrs[attr], \
                        "mismatched {:s} {:s} meta data".format(var, attr)
                except AssertionError:
                    try:
                        assert np.isnan(ival) and np.isnan(
                            netcdf_inst[var].attrs[attr]), \
                            "mismatched {:s} {:s} meta data".format(var, attr)
                    except TypeError:
                        raise AssertionError(
                            "mismatched {:s} {:s} meta data {:} != {:}".format(
                                var, attr, repr(ival),
                                repr(netcdf_inst[var].attrs[attr])))

        del netcdf_inst.data, netcdf_inst

        return

    @pytest.mark.parametrize("swap_time,err_msg,err_type",
                             [(True, 'not found in loaded', KeyError),
                              (False, "'time' already present", ValueError)])
    def test_read_netcdf4_bad_epoch_name(self, swap_time, err_msg, err_type):
        """Test netCDF4 load with bad epoch name/or 'time' already present.

        Parameters
        ----------
        swap_time : bool
            Change the output name of the time/epoch variable
        err_msg : str
            Error message to test for.
        err_type : Error
            Type of error eg. ValueError

        """
        # Load data
        outfile = os.path.join(self.tempdir.name, 'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)
        if swap_time:
            self.testInst.rename({'time': 'epoch'})

        # Write file
        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        # Pandas doesn't have 'time' error
        decode_times = default_decode_times

        # Evaluate the expected error and message
        testing.eval_bad_input(
            io.load_netcdf, err_type, err_msg,
            input_args=[outfile],
            input_kwargs={'epoch_name': 'whoosthat',
                          'decode_times': decode_times})
        return

    @pytest.mark.parametrize("write_epoch,war_msg", [('epoch',
                                                      'is not a dimension.')])
    @pytest.mark.parametrize("strict_dim_check", [True, False])
    def test_read_netcdf4_epoch_not_xarray_dimension(self, caplog, write_epoch,
                                                     war_msg, strict_dim_check):
        """Test netCDF4 load `epoch_name` not a dimension.

        Parameters
        ----------
        write_epoch : str
            Label used for datetime data when writing file.
        war_msg : str
            Warning message to test for.
        strict_dim_check : bool
            If True, raises warning. If False, does not raise warning.

        """
        # Load data
        outfile = os.path.join(self.tempdir.name, 'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)
        self.testInst.rename({"time": "epoch"})

        # Write file
        io.inst_to_netcdf(self.testInst, outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        # Evaluate the expected warning
        with caplog.at_level(logging.WARNING,
                             logger='GeospaceDataManagement'):
            io.load_netcdf(outfile, epoch_name='slt',
                           strict_dim_check=strict_dim_check,
                           **decode_times)

        self.out = caplog.text
        if strict_dim_check:
            assert self.out.find(war_msg) >= 0
        else:
            assert self.out.find(war_msg) < 0
        return

    @pytest.mark.parametrize("wkwargs, lkwargs", [
        ({"zlib": True}, {}), ({}, {}), ({"unlimited_time": False}, {})])
    def test_write_and_read_netcdf4_w_kwargs(self, wkwargs, lkwargs):
        """Test success of writing and reading a netCDF4 file.

        Parameters
        ----------
        wkargs : dict
            Keyword arguments passed to `inst_to_netcdf`.
        lwkargs : dict
            Keyword arguments passed to `io.load_netcdf`.

        """

        # Create a new file based on loaded test data
        outfile = os.path.join(self.tempdir.name,
                               'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)
        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label, **wkwargs)

        # Load the data that was created
        if 'epoch_name' not in lkwargs.keys():
            lkwargs['epoch_name'] = default_epoch_name

        self.loaded_inst = io.load_netcdf(outfile, **lkwargs, **decode_times)

        # Test the loaded data
        self.eval_loaded_data()
        return

    @pytest.mark.parametrize("kwargs, target", [
        ({}, dt.timedelta(seconds=1)),
        ({'epoch_unit': 'ns'}, dt.timedelta(microseconds=1)),
        ({'epoch_origin': dt.datetime(1980, 1, 6)}, dt.timedelta(seconds=1)),
        ({'epoch_unit': 'ns', 'epoch_origin': dt.datetime(1980, 1, 6)},
         dt.timedelta(microseconds=1))])
    def test_read_netcdf4_w_epoch_kwargs(self, kwargs, target):
        """Test success of writing and reading a netCDF4 file.

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to input into `load_netcdf`. Allows the epoch
            calculation to use custom origin and units.
        target : dt.timedelta
            Expected interpretation of 1 sec of time in loaded data when a given
            epoch unit is specified.  Default unit for pds.to_datetime is 1 ms.

        """

        # Create a bunch of files by year and doy
        outfile = os.path.join(self.tempdir.name,
                               'gdm_{:}_ncdf.nc'.format(self.testInst.name))
        self.testInst.load(date=self.stime)

        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        # Load the data that was created
        kwargs['epoch_name'] = default_epoch_name

        self.loaded_inst = io.load_netcdf(outfile, **decode_times, **kwargs)

        # Check that the step size is expected
        default_delta = np.diff(self.testInst[self.epoch_name][:2])

        # Average over 4 deltas to prevent rounding errors
        loaded_delta = np.diff(self.loaded_inst[self.epoch_name][:5]).mean()

        # Ratio of step_sizes should equal ratio of interpreted units
        assert ((default_delta / loaded_delta)
                == (dt.timedelta(seconds=1) / target))

        unix_origin = dt.datetime(1970, 1, 1)
        if 'epoch_origin' in kwargs.keys():
            file_origin = kwargs['epoch_origin']
        else:
            # Use unix origin as default
            file_origin = unix_origin

        # Find distance from origin
        def_uts = pds.to_datetime(self.testInst[self.epoch_name][0].values)
        load_uts = pds.to_datetime(
            self.loaded_inst[self.epoch_name][0].values)
        default_start = (def_uts - unix_origin)
        loaded_start = (load_uts - file_origin)

        # Ratio of distances should equal ratio of interpreted units
        assert (default_start.total_seconds() / loaded_start.total_seconds()
                == (dt.timedelta(seconds=1) / target))
        return

    @pytest.mark.parametrize("decode_times", [False, True])
    def test_decode_times(self, decode_times):
        """Test `decode_times` keyword in `load_netcdf_xarray`.

        Parameters
        ----------
        decode_times : bool
            Passed along to `io.load_netcdf`.

        """
        # Create a file
        outfile = os.path.join(self.tempdir.name,
                               'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)
        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        # Load the written data
        input_kwargs = {"decode_times": decode_times,
                        "epoch_origin": dt.datetime(1980, 1, 1),
                        "epoch_name": default_epoch_name}

        # Apply to xarray instruments
        self.loaded_inst = io.load_netcdf(outfile, **input_kwargs)

        if decode_times:
            # Times will be as in self.testInst
            assert np.all(self.testInst[self.epoch_name]
                          == self.loaded_inst[self.epoch_name])
        else:
            # Later epoch means loaded data in relative future
            assert np.all(self.testInst[self.epoch_name]
                          <= self.loaded_inst[self.epoch_name])

        return


class TestLoadNetCDFXArray(TestLoadNetCDF):
    """Unit tests for `load_netcdf` using xarray data."""

    def setup_method(self):
        """Set up the test environment."""

        # Create temporary directory
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

        self.saved_path = gdm.params['data_dirs']
        gdm.params['data_dirs'] = self.tempdir.name

        self.testInst = gdm.Instrument(platform='gdm', name='ndtesting',
                                       update_files=True, num_samples=100)
        self.stime = gdm.instruments.gdm_ndtesting._test_dates['']['']
        self.epoch_name = 'time'
        self.name_label = 'long_name'
        self.unit_label = 'units'

        # Initalize the loaded data
        self.loaded_inst = None
        return

    def teardown_method(self):
        """Clean up the test environment."""

        gdm.params['data_dirs'] = self.saved_path

        # Clear the attributes with data in them
        del self.loaded_inst, self.testInst, self.stime, self.epoch_name

        # Remove the temporary directory.
        self.tempdir.cleanup()

        # Clear the directory attributes
        del self.tempdir, self.saved_path
        return

    @pytest.mark.parametrize("kwargs,target", [({}, False),
                                               ({'decode_timedelta': False},
                                                False),
                                               ({'decode_timedelta': True},
                                                True)])
    def test_read_netcdf4_with_time_meta_labels(self, kwargs, target):
        """Test that `read_netcdf` correctly interprets time labels in meta.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments passed to `io.load_netcdf`.
        target : bool
            Target boolean value for testing.

        """
        # Prepare output test data
        outfile = os.path.join(self.tempdir.name,
                               'gdm_test_ncdf.nc')
        self.testInst.load(date=self.stime)

        # Modify the variable attributes directly before writing to file
        self.testInst['uts'].attrs['units'] = 'seconds'
        self.testInst['mlt'].attrs['units'] = 'minutes'
        self.testInst['slt'].attrs['units'] = 'hours'

        # Write output test data
        io.inst_to_netcdf(self.testInst, fname=outfile,
                          name_label=self.name_label,
                          unit_label=self.unit_label)

        # Load the written data
        self.loaded_inst = io.load_netcdf(outfile, **kwargs, **decode_times)

        # Check that labels pass through as correct type
        vars = ['uts', 'mlt', 'slt']
        for var in vars:
            val = self.loaded_inst[var].values[0]
            assert isinstance(val, np.timedelta64) == target, \
                "Variable {:} not loaded correctly".format(var)
        return


class TestNetCDF4Integration(object):
    """Integration tests for the netCDF4 I/O utils."""

    def setup_class(self):
        """Initialize the testing setup once before all tests are run."""

        # Use a temporary directory so that the user's setup is not altered.
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        return

    def teardown_class(self):
        """Clean up downloaded files and parameters from tests."""

        self.tempdir.cleanup()
        del self.tempdir
        return

    def setup_method(self):
        """Create a testing environment."""

        # Create an instrument object that has a meta with some
        # variables allowed to be nan within metadata when exporting.
        self.testInst = gdm.Instrument('gdm', 'testing', num_samples=5)
        self.testInst.load(date=self.testInst.inst_module._test_dates[''][''])

        return

    def teardown_method(self):
        """Clean up the test environment."""

        del self.testInst
        return


class TestNetCDF4IntegrationXarrayModels(TestNetCDF4Integration):
    """Integration tests for the netCDF4 I/O utils using models Instrument."""

    def setup_method(self):
        """Create a testing environment."""

        # Create an instrument object that has a meta with some
        # variables allowed to be nan within metadata when exporting.
        self.testInst = gdm.Instrument('gdm', 'testmodel', num_samples=5)
        self.testInst.load(date=self.testInst.inst_module._test_dates[''][''])

        return


class TestXarrayIO(object):
    """Unit tests for the Xarray I/O utilities."""

    def setup_method(self):
        """Create a testing environment."""

        # Create an instrument object that has a meta with some
        # variables allowed to be nan within metadata when exporting.
        self.testInst = gdm.Instrument('gdm', 'ndtesting', num_samples=5)
        self.testInst.load(date=self.testInst.inst_module._test_dates[''][''])
        self.epoch_name = 'time'

        return

    def teardown_method(self):
        """Clean up the test environment."""

        del self.testInst, self.epoch_name
        return

    @pytest.mark.parametrize('time_label', ['time', 'wrong_time'])
    def test_xarray_vars_no_time(self, time_label):
        """Test `xarray_vars_no_time`.

        Parameters
        ----------
        time_label : str
            Label for datetime data.

        """

        if time_label == 'time':
            vars = io.xarray_vars_no_time(self.testInst.data,
                                          time_label=time_label)
        else:
            with pytest.raises(ValueError) as verr:
                vars = io.xarray_vars_no_time(self.testInst.data,
                                              time_label=time_label)
            estr = ''.join(["Didn't find time dimension ", time_label])
            assert str(verr).find(estr)
            return

        xarray_vars = self.testInst.data.variables
        for var in vars:
            assert var in xarray_vars

        # Confirm 'time' not present
        assert 'time' not in vars

        assert len(xarray_vars) == len(vars) + 1

        return

    def test_xarray_all_vars(self):
        """Test `xarray_all_vars`."""

        # Get all variables
        vars = io.xarray_all_vars(self.testInst.data)

        # Get data variables
        xvars = list(self.testInst.data.data_vars.keys())
        testing.assert_list_contains(xvars, vars)

        # Get/test coordinate variables
        xcoords = list(self.testInst.data.coords.keys())
        testing.assert_list_contains(xcoords, vars)

        # Get/test dimension variables
        xdims = list(self.testInst.data.sizes.keys())
        testing.assert_list_contains(xdims, vars)

        # Test uniqueness
        vars_copy = copy.deepcopy(vars)
        for var in vars:
            vars_copy.pop(0)
            assert var not in vars_copy, 'List not unique.'

        return
