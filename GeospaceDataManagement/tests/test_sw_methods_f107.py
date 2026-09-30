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
"""Test suite for F10.7 methods."""

import datetime as dt
import numpy as np
import pandas as pds
import pytest
import xarray as xr

import GeospaceDataManagement as gdm

try:
    from GeospaceDataManagement.instruments.sw_methods import f107 as mm_f107
    from GeospaceDataManagement.instruments import sw_f107
    no_sw = False
except ImportError:
    no_sw = True


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestSWF107(object):
    """Test class for F10.7 methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Load a test instrument
        self.testInst = gdm.Instrument()
        self.testInst.data = xr.Dataset({
            'f107': (('time'), np.linspace(70, 200, 160)),
            'time': (('time'), [dt.datetime(2009, 1, 1) + dt.timedelta(days=i)
                                for i in range(160)])})
        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        del self.testInst
        return

    def eval_f107a(self, nan_check=False):
        """Evaluate the test instrument for F10.7a data.

        Parameters
        ----------
        nan_check : bool
            Check min and max values are NaN insensitive if True (default=False)

        """
        # Assert that new data and metadata exist
        assert 'f107a' in self.testInst.variables
        assert len(self.testInst['f107a'].attrs) > 0

        # Assert the values are finite and realistic means
        if nan_check:
            assert (np.nanmin(self.testInst['f107a'])
                    > np.nanmin(self.testInst['f107']))
            assert (np.nanmax(self.testInst['f107a'])
                    < np.nanmax(self.testInst['f107']))
        else:
            assert np.all(np.isfinite(self.testInst['f107a']))
            assert self.testInst['f107a'].min() > self.testInst['f107'].min()
            assert self.testInst['f107a'].max() < self.testInst['f107'].max()
        return

    @pytest.mark.parametrize("inargs,vmsg", [
        (["bad"], "unknown input data variable"),
        (['f107', 'f107'], "output data variable already exists")])
    def test_calc_f107a_bad_inputs(self, inargs, vmsg):
        """Test the calc_f107a with a bad inputs.

        Parameters
        ----------
        inargs : list
            List of input arguements that should raise a ValueError
        vmsg : str
            Expected ValueError message

        """

        with pytest.raises(ValueError) as verr:
            mm_f107.calc_f107a(self.testInst, *inargs)

        assert str(verr).find(vmsg) >= 0
        return

    def test_calc_f107a_daily(self):
        """Test the calc_f107a routine with daily data."""

        mm_f107.calc_f107a(self.testInst, f107_name='f107', f107a_name='f107a')
        self.eval_f107a()
        return

    def test_calc_f107a_high_rate(self):
        """Test the calc_f107a routine with sub-daily data."""
        self.testInst.data = xr.Dataset(
            {'f107': (('time'), np.linspace(70, 200, 3840)),
             'time': (('time'), [dt.datetime(2009, 1, 1) + dt.timedelta(hours=i)
                                 for i in range(3840)])})
        mm_f107.calc_f107a(self.testInst, f107_name='f107', f107a_name='f107a')
        self.eval_f107a()

        # Assert the same mean value is used for a day
        assert len(np.unique(self.testInst['f107a'][:24])) == 1
        return

    def test_calc_f107a_daily_missing(self):
        """Test the calc_f107a routine with some daily data missing."""

        self.testInst.data = xr.Dataset(
            {'f107': (('time'), np.linspace(70, 200, 160)),
             'time': (('time'), [dt.datetime(2009, 1, 1) + dt.timedelta(
                 days=(2 * i + 1)) for i in range(160)])})
        mm_f107.calc_f107a(self.testInst, f107_name='f107', f107a_name='f107a')

        # Assert that new data and metadata exist
        self.eval_f107a(nan_check=True)

        # Assert the expected number of fill values
        assert (len(self.testInst['f107a'][np.isnan(self.testInst['f107a'])])
                == 40)
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestSWF107Combine(object):
    """Test class for the `combine_f107` method."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Switch to test_data directory
        self.saved_path = gdm.params['data_dirs']
        gdm.params.data['data_dirs'] = [gdm.test_data_path]

        # Set combination testing input
        self.test_day = dt.datetime(2019, 3, 16)
        inst_id = {tag: '' for tag in sw_f107.tags.keys()}
        inst_id['now'] = 'obs'
        self.combine_inst = {tag: gdm.Instrument(inst_module=sw_f107, tag=tag,
                                                 inst_id=inst_id[tag],
                                                 update_files=True)
                             for tag in sw_f107.tags.keys()}
        self.combine_times = {"start": self.test_day - dt.timedelta(days=30),
                              "stop": self.test_day + dt.timedelta(days=3)}

        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        gdm.params.data['data_dirs'] = self.saved_path
        del self.combine_inst, self.test_day, self.combine_times
        return

    def test_combine_f107_none(self):
        """Test `combine_f107` failure when no input is provided."""

        with pytest.raises(TypeError) as terr:
            mm_f107.combine_f107()

        assert str(terr).find("missing 2 required positional arguments") >= 0
        return

    def test_combine_f107_no_time(self):
        """Test `combine_f107` failure when no times are provided."""

        with pytest.raises(ValueError) as verr:
            mm_f107.combine_f107(self.combine_inst['historic'],
                                 self.combine_inst['forecast'])

        assert str(verr).find("must either load in Instrument objects") >= 0
        return

    def test_combine_f107_bad_time(self):
        """Test `combine_f107` failure when bad times are provided."""

        with pytest.raises(ValueError) as verr:
            mm_f107.combine_f107(self.combine_inst['historic'],
                                 self.combine_inst['forecast'],
                                 start=self.combine_times['stop'],
                                 stop=self.combine_times['start'])

        assert str(verr).find("date range is zero or negative") >= 0
        return

    def test_combine_f107_no_data(self):
        """Test `combine_f107` when no data is present for specified times."""

        combo_in = {kk: self.combine_inst['forecast'] for kk in
                    ['standard_inst', 'forecast_inst']}
        combo_in['start'] = dt.datetime(2014, 2, 19)
        combo_in['stop'] = dt.datetime(2014, 2, 24)
        f107_inst = mm_f107.combine_f107(**combo_in)

        assert f107_inst.data.isnull().all()["f107"]

        del combo_in, f107_inst
        return

    def test_combine_f107_no_data_no_files(self):
        """Test `combine_f107` without data or files for the specified times."""

        # Unset the file list for the instrument
        self.combine_inst['forecast'].files.files = pds.Series([])

        # Set the function inputs
        combo_in = {kk: self.combine_inst['forecast'] for kk in
                    ['standard_inst', 'forecast_inst']}
        combo_in['start'] = dt.datetime(2014, 2, 19)
        combo_in['stop'] = dt.datetime(2014, 2, 24)

        # Run the method
        f107_inst = mm_f107.combine_f107(**combo_in)

        # Test the output
        assert np.isnan(f107_inst.data["f107"]).all()

        del combo_in, f107_inst
        return

    def test_combine_f107_inst_time(self):
        """Test `combine_f107` with times provided through datasets."""

        self.combine_inst['historic'].load(
            date=self.combine_inst['historic'].lasp_stime,
            end_date=self.combine_times['start'])
        self.combine_inst['forecast'].load(date=self.test_day)

        f107_inst = mm_f107.combine_f107(self.combine_inst['historic'],
                                         self.combine_inst['forecast'])

        assert f107_inst.index[0] == self.combine_inst['historic'].lasp_stime
        assert f107_inst.index[-1] <= self.combine_times['stop']
        assert len(f107_inst.vars_no_time) == 1
        assert 'f107' in f107_inst.variables

        del f107_inst
        return

    def test_combine_f107_all(self):
        """Test `combine_f107` with 'historic' and '45day' input."""

        f107_inst = mm_f107.combine_f107(self.combine_inst['historic'],
                                         self.combine_inst['45day'],
                                         **self.combine_times)

        assert f107_inst.index[0] >= self.combine_times['start']
        assert f107_inst.index[-1] < self.combine_times['stop']
        assert len(f107_inst.vars_no_time) == 1
        assert 'f107' in f107_inst.variables

        del f107_inst
        return
