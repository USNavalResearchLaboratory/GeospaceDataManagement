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
"""Tests the parameter storage area."""

import copy
from importlib import reload
import os
import pytest
import shutil
import tempfile

# The first two imports are required for re-importing and eval statements
import GeospaceDataManagement as gdm
from GeospaceDataManagement._params import Parameters
from GeospaceDataManagement.tests.classes.cls_ci import CICleanSetup
from GeospaceDataManagement.utils import testing


class TestBasics(object):
    """Unit tests for accessing and changing `gdm._params`."""

    def setup_method(self):
        """Set up the unit test environment for each method."""
        # Store current GeospaceDataManagement directory
        self.stored_params = copy.deepcopy(gdm.params)

        # Set up default values
        gdm.params.restore_defaults()

        # Get a temporary directory
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.wd = os.getcwd()

    def teardown_method(self):
        """Clean up the unit test environment after each method."""
        gdm.params = copy.deepcopy(self.stored_params)
        gdm.params.store()
        reload(gdm)
        os.chdir(self.wd)
        self.tempdir.cleanup()

    @pytest.mark.parametrize("paths, check",
                             [('.', ['.']),
                              (os.path.join('.', 'hi'),
                               [os.path.join('.', 'hi')]),
                              (os.path.join('.', 'hi', ''),
                               [os.path.join('.', 'hi')]),
                              (os.path.join('.', ''), ['.']),
                              (['.', '.'], None)])
    def test_set_data_dirs(self, paths, check):
        """Test update of gdm directory via params."""
        if check is None:
            check = paths

        # Switch working directory to temp directory
        os.chdir(self.tempdir.name)

        # Assign path
        gdm.params['data_dirs'] = paths
        assert gdm.params['data_dirs'] == check

        # Check if next load of gdm remembers the change
        reload(gdm)
        assert gdm.params['data_dirs'] == check
        return

    @pytest.mark.parametrize("path", ['no_path', 'not_a_directory'])
    def test_set_data_dir_bad_directory(self, path):
        """Ensure you can't set data_dirs to a bad path.

        Parameters
        ----------
        path : str
            Bad path to a directory

        """
        with pytest.raises(ValueError) as verr:
            gdm.params['data_dirs'] = path

        assert str(verr).find("Invalid path") >= 0
        return

    def test_repr(self):
        """Test __repr__ method."""
        out = gdm.params.__repr__()
        assert out.find('Parameters(path=') >= 0
        return

    def test_str(self):
        """Ensure str method works."""

        # Include a user parameter
        gdm.params['gdm_user_test_str'] = 'We are here.'

        out = str(gdm.params)
        # Confirm start of str
        assert out.find('GeospaceDataParameters Parameters object') >= 0

        # Confirm that default, non-default, and user values present
        assert out.find('GeospaceDataParameters settings') > 0
        assert out.find('Standard parameters:') > 0

        assert out.find('settings (non-default)') > 0
        assert out.find('Standard parameters (no defaults):') > 0

        assert out.find('user values') > 0
        assert out.find('User parameters:') > 0
        return

    def test_restore_defaults(self):
        """Test restore_defaults works as intended."""

        # Get default value, as per setup
        default_val = gdm.params['update_files']

        # Change value to non-default
        gdm.params['update_files'] = not default_val

        # Restore defaults
        gdm.params.restore_defaults()

        # Ensure new value is the default
        assert gdm.params['update_files'] == default_val

        # Make sure that non-default values left as is
        assert gdm.params['data_dirs'] != []
        return

    def test_update_standard_value(self):
        """Test that update of a pre-existing standard value is stored."""

        # Get default value, as per setup
        default_val = gdm.params['update_files']

        # Change value to non-default
        gdm.params['update_files'] = not gdm.params['update_files']

        # Ensure it is in memory
        assert gdm.params['update_files'] is not default_val

        # Get a new parameters instance and verify information is retained.
        # Using eval to ensure all settings with current gdm.params retained.
        new_params = eval(gdm.params.__repr__())
        assert new_params['update_files'] == gdm.params['update_files']
        return

    def test_no_update_user_modules(self):
        """Ensure user_modules not modifiable via params."""

        # Attempt to change value
        with pytest.raises(ValueError) as err:
            gdm.params['user_modules'] = {}
        assert str(err).find('The gdm.utils.registry ') >= 0
        return

    def test_add_user_parameter(self):
        """Add custom parameter and ensure present."""

        gdm.params['hi_there'] = 'hello there!'
        assert gdm.params['hi_there'] == 'hello there!'

        # Get a new parameters instance and verify information is retained
        # Using eval to ensure all settings with current gdm.params retained.
        new_params = eval(gdm.params.__repr__())
        assert new_params['hi_there'] == gdm.params['hi_there']
        return

    def test_clear_and_restart(self):
        """Verify clear_and_restart method impacts all values."""

        gdm.params.clear_and_restart()

        # Check default value
        assert gdm.params['user_modules'] == {}

        # Check value without working default
        assert gdm.params['data_dirs'] == []

        return

    def test_bad_path_instantiation(self):
        """Ensure you can't use bad path when loading Parameters."""
        testing.eval_bad_input(Parameters, OSError,
                               "Supplied path does not exist",
                               input_kwargs={"path": './made_up_name'})

        return


class TestCIonly(CICleanSetup):
    """Tests where we mess with local settings.

    Notes
    -----
    These only run in CI environments to avoid breaking an end user's setup

    """

    def test_settings_file_must_be_present(self, capsys):
        """Ensure gdm_settings.json is present."""

        reload(gdm)

        captured = capsys.readouterr()
        # Ensure GeospaceDataParameters is running in 'first-time' mode
        assert captured.out.find("Hi there!") >= 0

        # Remove GeospaceDataParameters settings file
        shutil.move(os.path.join(self.root, 'gdm_settings.json'),
                    os.path.join(self.root, 'gdm_settings_moved.json'))

        # Ensure we can't create a parameters file without valid .json
        testing.eval_bad_input(
            Parameters, OSError,
            'GeospaceDataParameters is unable to locate a user settings')

        shutil.move(os.path.join(self.root, 'gdm_settings_moved.json'),
                    os.path.join(self.root, 'gdm_settings.json'))
        return

    def test_settings_file_cwd(self, capsys):
        """Test Parameters works when settings file in current working dir."""

        reload(gdm)

        captured = capsys.readouterr()
        # Ensure GeospaceDataManagement is running in 'first-time' mode
        assert captured.out.find("Hi there!") >= 0

        # Move GeospaceDataManagement settings file to cwd
        shutil.move(os.path.join(self.root, 'gdm_settings.json'),
                    os.path.join('.', 'gdm_settings.json'))

        # Try loading by supplying a specific path
        test_params = Parameters(path='.')

        # Supplying no path should yield the same result
        test_params2 = Parameters()

        # Confirm data is the same for both
        assert test_params.data == test_params2.data

        # Confirm path is the same for both
        assert test_params.file_path == test_params2.file_path

        # Ensure we didn't load a file in .gdm
        assert not os.path.isfile(os.path.join(self.root,
                                               'gdm_settings.json'))

        # Move GeospaceDataManagement settings file back to original
        shutil.move(os.path.join('.', 'gdm_settings.json'),
                    os.path.join(self.root, 'gdm_settings.json'))

        return
