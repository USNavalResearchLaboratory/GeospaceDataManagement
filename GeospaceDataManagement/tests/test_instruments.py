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
"""Unit and Integration Tests for each instrument module.

Notes
-----
Imports test methods from gdm.tests.classes.cls_instrument_library, all
Instruments must undergo this testing in a single class as the pytest markers
cannot be updated for that test class mid-test.

"""

import datetime as dt
import numpy as np
import os
import pandas as pds
import pathlib
import tempfile

import pytest

import GeospaceDataManagement as gdm
import GeospaceDataManagement.tests.classes.cls_instrument_library as clslib
from GeospaceDataManagement.utils import generate_instrument_list
from GeospaceDataManagement.utils.testing import eval_bad_input

# Optional code to pass through user and password info to test instruments
# dict, keyed by the Instrument, with a list of usernames and passwords
user_password = {'user': 'gdm_testing',
                 'password': 'angeline.g.burrell.civ@us.navy.mil'}
user_info = {'gdm_testing': user_password}

# Initialize tests for sources in gdm.instruments. Keep seperate lists for
# different optional installation structures to allow testing only the
# available instruments
test_instruments = generate_instrument_list(inst_loc=gdm.instruments,
                                            user_info=user_info, subset='test')
mad_instruments = generate_instrument_list(inst_loc=gdm.instruments,
                                           subset='madrigal')
sw_instruments = generate_instrument_list(inst_loc=gdm.instruments, subset='sw')

no_sw = False if len(sw_instruments['names']) > 0 else True
no_mad = False if len(mad_instruments['names']) > 0 else True

if not no_mad:
    # Need to update the user info to include the Madrigal Instruments as
    # they all require downloads
    user_info.update({module: user_password
                      for module in mad_instruments['names']})

instruments = clslib.InstLibTests.initialize_test_package(
    clslib.InstLibTests, inst_loc=gdm.instruments, user_info=user_info,
    inst_subset='all')


class TestInstruments(clslib.InstLibTests):
    """Main class for instrument tests.

    Notes
    -----
    All standard tests, setup, and teardown inherited from the core
    instrument test class. As the markers are custom and can only be set
    once, all groups of instruments must be tested in this class

    """

    # Tests specifically for the GeospaceDataMangement test instruments
    @pytest.mark.parametrize("inst_dict", test_instruments['download'])
    @pytest.mark.parametrize("kwarg,output", [(None, 0.0),
                                              (dt.timedelta(hours=1), 3600.0)])
    def test_inst_start_time(self, inst_dict, kwarg, output):
        """Test operation of start_time keyword, including default behavior.

        Parameters
        ----------
        inst_dict : dict
            One of the dictionaries returned from
            `InstLibTests.initialize_test_package` with instruments to test
        kwarg : dt.timedelta or NoneType
            Passed to `gdm.Instrument` as value for `start_time` keyword
        output : float
            Expected value for the first loaded value in variable `uts`

        """

        _, date = clslib.initialize_test_inst_and_date(inst_dict)
        if kwarg:
            self.test_inst = gdm.Instrument(
                inst_module=inst_dict['inst_module'], start_time=kwarg)
        else:
            self.test_inst = gdm.Instrument(
                inst_module=inst_dict['inst_module'])

        self.test_inst.load(date=date)

        assert self.test_inst[0, 'uts'] == output
        return

    @pytest.mark.parametrize("inst_dict", test_instruments['download'])
    def test_inst_num_samples(self, inst_dict):
        """Test operation of num_samples keyword.

        Parameters
        ----------
        inst_dict : dict
            One of the dictionaries returned from
            `InstLibTests.initialize_test_package` with instruments to test

        """

        # Number of samples needs to be <96 because freq is not settable.
        # Different test instruments have different default number of points.
        num = 10
        _, date = clslib.initialize_test_inst_and_date(inst_dict)
        self.test_inst = gdm.Instrument(inst_module=inst_dict['inst_module'],
                                        num_samples=num)
        self.test_inst.load(date=date)

        assert len(self.test_inst['uts']) == num
        return

    @pytest.mark.parametrize("inst_dict", test_instruments['download'])
    def test_inst_file_date_range(self, inst_dict):
        """Test operation of file_date_range keyword.

        Parameters
        ----------
        inst_dict : dict
            One of the dictionaries returned from
            `InstLibTests.initialize_test_package` with instruments to test

        """

        file_date_range = pds.date_range(dt.datetime(2021, 1, 1),
                                         dt.datetime(2021, 12, 31))
        _, date = clslib.initialize_test_inst_and_date(inst_dict)
        self.test_inst = gdm.Instrument(inst_module=inst_dict['inst_module'],
                                        file_date_range=file_date_range,
                                        update_files=True)
        file_list = self.test_inst.files.files

        assert all(file_date_range == file_list.index)
        return

    @pytest.mark.parametrize("inst_dict", test_instruments['download'])
    def test_inst_max_latitude(self, inst_dict):
        """Test operation of max_latitude keyword.

        Parameters
        ----------
        inst_dict : dict
            One of the dictionaries returned from
            `InstLibTests.initialize_test_package` with instruments to test

        """

        _, date = clslib.initialize_test_inst_and_date(inst_dict)
        self.test_inst = gdm.Instrument(inst_module=inst_dict['inst_module'])
        if self.test_inst.name != 'testmodel':
            self.test_inst.load(date=date, max_latitude=10.)
            assert np.all(np.abs(self.test_inst['latitude']) <= 10.)
        else:
            # Skipping testmodel Instrument
            pytest.skip("kwarg not implemented in testmodel")

        return

    @pytest.mark.second
    @pytest.mark.parametrize("clean_level", ['clean', 'dusty', 'dirty'])
    @pytest.mark.parametrize("change", [True, False])
    @pytest.mark.parametrize('warn_type', ['logger', 'warning', 'error',
                                           'mult'])
    @pytest.mark.parametrize("inst_dict", test_instruments['download'])
    def test_clean_with_warnings(self, clean_level, change, warn_type,
                                 inst_dict, caplog):
        """Run `test_clean_warn` with different warning behaviours.

        Parameters
        ----------
        clean_level : str
            Cleanliness level for loaded instrument data; must run the clean
            routine (not include 'none').
        change : bool
            Specify whether or not clean level should change.
        warn_type : str
            Desired type of warning or error to be raised.
        inst_dict : dict
            One of the dictionaries returned from
            `InstLibTests.initialize_test_package` with instruments to test.

        """
        # Set the default values
        warn_level = {'logger': 'WARN', 'warning': UserWarning,
                      'error': ValueError}
        warn_msg = 'Default warning message'
        if change:
            final_level = 'none' if clean_level == 'clean' else 'clean'
        else:
            final_level = clean_level

        # Construct the expected warnings
        if warn_type == 'mult':
            # Note that we cannot test errors along with other warnings
            inst_dict['inst_module']._clean_warn = {
                inst_dict['inst_id']: {inst_dict['tag']: {clean_level: [
                    ('warning', warn_level['warning'], warn_msg, final_level),
                    ('logger', warn_level['logger'], warn_msg, final_level)]}}}
        else:
            inst_dict['inst_module']._clean_warn = {
                inst_dict['inst_id']: {inst_dict['tag']: {clean_level: [
                    (warn_type, warn_level[warn_type], warn_msg,
                     final_level)]}}}

        # Set the additional Instrument kwargs
        if 'kwargs' in inst_dict.keys():
            # Ensure the test instrument cleaning kwarg is reset
            inst_dict['kwargs']['test_clean_kwarg'] = {'change': final_level}
        else:
            inst_dict['kwargs'] = {'test_clean_kwarg': {'change': final_level}}

        if warn_type == 'mult':
            inst_dict['kwargs']['test_clean_kwarg']['logger'] = warn_msg
            inst_dict['kwargs']['test_clean_kwarg']['warning'] = warn_msg
        else:
            inst_dict['kwargs']['test_clean_kwarg'][warn_type] = warn_msg

        # Run the test
        self.test_clean_warn(clean_level, inst_dict, caplog)

        return

    # Tests specifically for the Space Weather instruments
    @pytest.mark.skipif(no_sw, reason="Space Weather test only")
    @pytest.mark.second
    def test_45day_forecast_data_length(self):
        """Test that the downloaded 45-day forecasts load 45 days of data."""
        # Initalize the desired instrument parameters
        inst_dict = {'inst_module': gdm.instruments.sw_f107,
                     'tag': '45day', 'inst_id': ''}
        _, date = clslib.initialize_test_inst_and_date(inst_dict)

        # Load the downloaded data
        self.test_inst = gdm.Instrument(**inst_dict)
        self.test_inst.load(date=date)

        # Test that 45 days of F10.7 data are available
        assert len(self.test_inst['f107']) == 45
        return


# Tests specifically for the Madrigal instruments
@pytest.mark.skipif(no_mad, reason="Madrigal test only")
class TestInstrumentLoadError(object):
    """Class for unit testing errors raised when loading data."""

    def setup_class(self):
        """Initialize the testing setup once before all tests are run."""

        # Use a temporary directory so that the user's setup is not altered.
        self.tempdir = tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True)
        self.saved_path = gdm.params['data_dirs']
        gdm.params._set_data_dirs(path=self.tempdir.name, store=False)
        return

    def teardown_class(self):
        """Clean up downloaded files and parameters from tests."""

        gdm.params._set_data_dirs(self.saved_path, store=False)
        # Remove the temporary directory. In Windows, this occasionally fails
        # by raising a wide variety of different error messages. Python 3.10+
        # can handle this, but lower Python versions cannot.
        self.tempdir.cleanup()

        del self.saved_path, self.tempdir
        return

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.inst_kwargs = [{'inst_module': gdm.instruments.gnss_tec,
                             'tag': 'los', 'los_method': 'site'}]
        self.load_time = dt.datetime(2001, 1, 1)
        self.fake_file = ''
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        if os.path.isfile(self.fake_file):
            os.remove(self.fake_file)

        del self.inst_kwargs, self.load_time, self.fake_file
        return

    def test_bad_los_value(self):
        """Test ValueError when the `los_value` is omitted."""
        inst = gdm.Instrument(**self.inst_kwargs[0])

        # Ensure a file is available
        if self.load_time not in inst.files.files.keys():
            self.fake_file = os.path.join(
                inst.files.data_path,
                self.inst_kwargs[0]['inst_module'].supported_tags[inst.inst_id][
                    inst.tag].format(file_type='hdf5').format(
                        year=self.load_time.year, month=self.load_time.month,
                        day=self.load_time.day, version=1))
            gdm.utils.files.check_and_make_path(inst.files.data_path)
            pathlib.Path(self.fake_file).touch()
            inst = gdm.Instrument(**self.inst_kwargs[0])

        eval_bad_input(inst.load, ValueError, "must specify a valid",
                       input_kwargs={'date': self.load_time})
        return
