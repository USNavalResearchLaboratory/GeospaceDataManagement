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
"""Test suite for Kp and Ap methods."""

import datetime as dt
import numpy as np
import pandas as pds
import pytest

import GeospaceDataManagement as gdm
try:
    from GeospaceDataManagement.instruments import sw_kp
    from GeospaceDataManagement.instruments.sw_methods import kp_ap
    no_sw = False
except ImportError:
    no_sw = True


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestKpInitMetadata(object):
    """Test class for Kp metadata initialization methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.test_function = kp_ap.get_kp_metadata

        # Set the default values
        self.units = ''
        self.desc = 'Planetary K-index'
        self.min_val = 0
        self.max_val = 9
        self.fill_val = -1
        self.out_dict = {}

        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        del self.test_function, self.units, self.desc
        del self.min_val, self.max_val, self.fill_val, self.out_dict
        return

    def eval_defaults(self):
        """Evaluate the outputs of the metadata."""

        assert self.out_dict['units'] == self.units
        assert self.out_dict['desc'] == self.desc
        assert self.out_dict['min_val'] == self.min_val
        assert self.out_dict['max_val'] == self.max_val
        assert self.out_dict['fill_val'] == self.fill_val
        return

    def test_get_metadata_defaults(self):
        """Test default metadata initialization."""

        self.out_dict = self.test_function()
        self.eval_defaults()

        return

    def test_fill_metadata(self):
        """Test metadata initialization with user-specified fill value."""
        self.out_dict = self.test_function(fill_val=666)

        self.fill_val = 666
        self.eval_defaults()
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestApInitMetadata(TestKpInitMetadata):
    """Test class for Ap metadata initialization methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.test_function = kp_ap.get_ap_metadata

        # Set the default values
        self.units = ''
        self.desc = 'ap (equivalent range) index'
        self.min_val = 0
        self.max_val = 400
        self.fill_val = -1
        self.out_dict = {}
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestBartelInitMetadata(object):
    """Test class for Bartel metadata initialization methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.test_function = kp_ap.get_bartel_metadata

        # Set the default values
        self.units = ''
        self.desc = ''.join(['A sequence of 27-day intervals counted from ',
                             'February 8, 1832'])
        self.min_val = 1
        self.max_val = np.inf
        self.fill_val = -1
        self.out_dict = {}
        return

    def eval_defaults(self, data_key):
        """Evaluate the outputs of the metadata.

        Parameters
        ----------
        data_key : str
            Name of the desired variable

        """
        if data_key.find('day_within') >= 0:
            self.units = 'day'
            name = 'Days within Bartels solar rotation'
            self.desc = 'Number of days within the Bartels solar rotation'
            self.max_val = 27
        else:
            name = 'Bartels solar rotation number'

        assert self.out_dict['units'] == self.units
        assert self.out_dict['name'] == name
        assert self.out_dict['desc'] == self.desc
        assert self.out_dict['max_val'] == self.max_val
        assert self.out_dict['min_val'] == self.min_val
        assert self.out_dict['fill_val'] == self.fill_val

        return

    @pytest.mark.parametrize("data_key", ["solar_rotation_num",
                                          "day_within_solar_rotation"])
    def test_get_metadata_defaults(self, data_key):
        """Test default metadata initialization.

        Parameters
        ----------
        data_key : str
            String denoting the data key

        """
        self.out_dict = self.test_function(data_key)
        self.eval_defaults(data_key)

        return

    @pytest.mark.parametrize("data_key", ["solar_rotation_num",
                                          "day_within_solar_rotation"])
    def test_fill_metadata(self, data_key):
        """Test metadata initialization with user-specified fill value.

        Parameters
        ----------
        data_key : str
            String denoting the data key

        """
        self.out_dict = self.test_function(data_key, fill_val=666)

        self.fill_val = 666
        self.eval_defaults(data_key)
        return

    def test_bad_data_variable(self):
        """Test metadata initialization doesn't work with the wrong variable."""
        data_key = 'Kp'

        with pytest.raises(ValueError) as verr:
            self.test_function(data_key)

        assert str(verr).find('unknown data key') >= 0
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestSWKp(object):
    """Test class for Kp methods."""

    def setup_method(self):
        """Create a clean testing setup."""

        # Load a test instrument
        inst_dict = {'num_samples': 12}
        self.inst = gdm.Instrument('gdm', 'testing', **inst_dict)
        test_time = gdm.instruments.gdm_testing._test_dates['']['']

        load_kwargs = {'date': test_time}
        self.inst.load(**load_kwargs)

        # Create Kp data
        self.inst.data[self.inst.index.name] = pds.DatetimeIndex(data=[
            test_time + dt.timedelta(hours=3 * i) for i in range(12)])
        self.inst['Kp'] = np.arange(0, 4, 1.0 / 3.0)
        self.inst['ap_nan'] = np.full(shape=12, fill_value=np.nan)
        self.inst['ap_inf'] = np.full(shape=12, fill_value=np.inf)
        self.inst['Kp'].attrs.update({'fill_val': np.nan})
        self.inst['ap_nan'].attrs.update({'fill_val': np.nan})
        self.inst['ap_inf'].attrs.update({'fill_val': np.inf})
        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        del self.inst
        return

    def test_convert_kp_to_ap(self):
        """Test conversion of Kp to ap."""

        kp_ap.convert_3hr_kp_to_ap(self.inst)

        assert '3hr_ap' in self.inst.variables
        assert len(self.inst['3hr_ap'].attrs) > 0
        assert self.inst['3hr_ap'].min() >= self.inst['3hr_ap'].attrs['min_val']
        assert self.inst['3hr_ap'].max() <= self.inst['3hr_ap'].attrs['max_val']
        return

    def test_convert_kp_to_ap_fill_val(self):
        """Test conversion of Kp to ap with fill values."""

        # Set the first value to a fill value, then calculate ap
        fill_label = 'fill_val'
        fill_value = self.inst['Kp'].attrs[fill_label]
        self.inst[self.inst.index[0], 'Kp'] = fill_value
        kp_ap.convert_3hr_kp_to_ap(self.inst)

        # Test non-fill ap values
        assert '3hr_ap' in self.inst.variables
        assert len(self.inst['3hr_ap'].attrs.keys()) > 0
        assert self.inst['3hr_ap'][1:].min() >= self.inst[
            '3hr_ap'].attrs['min_val']
        assert self.inst['3hr_ap'][1:].max() <= self.inst[
            '3hr_ap'].attrs['max_val']

        # Test the fill value in the data and metadata
        assert np.isnan(self.inst['3hr_ap'][0])
        assert np.isnan(self.inst['3hr_ap'].attrs[fill_label])

        return

    def test_convert_kp_to_ap_bad_input(self):
        """Test conversion of Kp to ap with bad input."""
        # Rename the desired data variable to something that won't work
        self.inst.rename({"Kp": "bad"})

        with pytest.raises(ValueError) as verr:
            kp_ap.convert_3hr_kp_to_ap(self.inst)

        assert str(verr).find("Variable name for Kp data is missing") >= 0
        return

    def test_convert_ap_to_kp(self):
        """Test conversion of ap to Kp."""

        kp_ap.convert_3hr_kp_to_ap(self.inst)
        kp_out, kp_meta = kp_ap.convert_ap_to_kp(self.inst['3hr_ap'])

        # Assert original and coverted there and back Kp are equal
        assert all(abs(kp_out - self.inst['Kp']) < 1.0e-4)

        # Assert the converted Kp meta data exists and is reasonable
        assert kp_meta['fill_val'] == -1

        del kp_out, kp_meta
        return

    def test_convert_ap_to_kp_middle(self):
        """Test conversion of ap to Kp where ap is not an exact Kp value."""

        kp_ap.convert_3hr_kp_to_ap(self.inst)
        new_val = self.inst[self.inst.index[8], '3hr_ap'] + 1
        self.inst[self.inst.index[8], '3hr_ap'] = new_val
        kp_out, kp_meta = kp_ap.convert_ap_to_kp(self.inst['3hr_ap'])

        # Assert original and coverted there and back Kp are equal
        assert all(abs(kp_out - self.inst.data['Kp']) < 1.0e-4)

        # Assert the converted Kp meta data exists and is reasonable
        assert kp_meta['fill_val'] == -1

        return

    def test_convert_ap_to_kp_nan_input(self):
        """Test conversion of ap to Kp where ap is NaN."""

        kp_out, kp_meta = kp_ap.convert_ap_to_kp(self.inst['ap_nan'])

        # Assert original and coverted there and back Kp are equal
        assert all(kp_out == -1)

        # Assert the converted Kp meta data exists and is reasonable
        assert kp_meta['fill_val'] == -1

        del kp_out, kp_meta
        return

    def test_convert_ap_to_kp_inf_input(self):
        """Test conversion of ap to Kp where ap is Inf."""

        kp_out, kp_meta = kp_ap.convert_ap_to_kp(self.inst['ap_inf'])

        # Assert original and coverted there and back Kp are equal
        assert all(kp_out[1:] == -1)

        # Assert the converted Kp meta data exists and is reasonable
        assert kp_meta['fill_val'] == -1

        del kp_out, kp_meta
        return

    def test_convert_ap_to_kp_fill_val(self):
        """Test conversion of ap to Kp with fill values."""

        # Set the first Kp value to a fill value
        fill_label = 'fill_val'
        fill_value = self.inst['Kp'].attrs[fill_label]
        self.inst[self.inst.index[0], 'Kp'] = fill_value

        # Calculate ap
        kp_ap.convert_3hr_kp_to_ap(self.inst)

        # Recalculate Kp from ap
        kp_out, kp_meta = kp_ap.convert_ap_to_kp(self.inst['3hr_ap'],
                                                 fill_val=fill_value)

        # Test non-fill ap values
        assert all(abs(kp_out[1:] - self.inst['Kp'][1:]) < 1.0e-4)

        # Test the fill value in the data and metadata
        assert np.isnan(kp_out[0])
        assert np.isnan(kp_meta[fill_label])

        return

    @pytest.mark.parametrize("filter_kwargs,ngood", [
        ({"min_kp": 2, 'filter_time': 0}, 6),
        ({"max_kp": 2, 'filter_time': 0}, 7),
        ({"min_kp": 2, "filter_time": 12}, 2),
        ({"min_kp": 2, "max_kp": 3, 'filter_time': 0}, 4)])
    def test_filter_geomag(self, filter_kwargs, ngood):
        """Test geomag_filter success for different limits.

        Parameters
        ----------
        filter_kwargs : dict
            Dict with kwarg input for `filter_geomag`
        ngood : int
            Expected number of good samples

        """

        kp_ap.filter_geomag(self.inst, kp_inst=self.inst,
                            **filter_kwargs)
        assert len(self.inst.index) == ngood, \
            'Incorrect filtering using {:} of {:}'.format(filter_kwargs,
                                                          self.inst['Kp'])
        return

    def test_filter_geomag_load_kp(self):
        """Test geomag_filter loading the Kp instrument."""
        try:
            kp_ap.filter_geomag(self.inst)
            assert len(self.inst.index) == 12  # No filtering with defaults
        except IOError as ierr:
            assert str(ierr).find('unable to load') >= 0  # No data to load
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestSWKpCombine(object):
    """Tests for the `combine_kp` method."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Switch to test_data directory
        self.saved_path = gdm.params['data_dirs']
        gdm.params.data['data_dirs'] = [gdm.test_data_path]

        # Set combination testing input
        test_day = dt.datetime(2019, 3, 18)
        idict = {'inst_module': sw_kp, 'update_files': True}

        self.combine = {"standard_inst": gdm.Instrument(tag="def", **idict),
                        "recent_inst": gdm.Instrument(tag="recent", **idict),
                        "forecast_inst": gdm.Instrument(tag="forecast",
                                                        **idict),
                        "start": test_day - dt.timedelta(days=30),
                        "stop": test_day + dt.timedelta(days=3),
                        "fill_val": -1}
        self.load_kwargs = {"date": test_day}

        return

    def teardown_method(self):
        """Clean up previous testing."""
        gdm.params.data['data_dirs'] = self.saved_path
        del self.combine, self.saved_path, self.load_kwargs
        return

    def test_combine_kp_none(self):
        """Test combine_kp failure when no input is provided."""

        with pytest.raises(ValueError) as verr:
            kp_ap.combine_kp()

        assert str(verr).find("need at two Kp Instrument objects to") >= 0
        return

    def test_combine_kp_one(self):
        """Test combine_kp raises ValueError with only one instrument."""

        # Load a test instrument
        test_inst = gdm.Instrument()
        test_inst.data = pds.DataFrame({'Kp': np.arange(0, 4, 1.0 / 3.0)},
                                       index=[dt.datetime(2009, 1, 1)
                                              + pds.DateOffset(hours=3 * i)
                                              for i in range(12)])
        test_inst['Kp'].attrs.update({'fill_val': np.nan})

        with pytest.raises(ValueError) as verr:
            kp_ap.combine_kp(standard_inst=test_inst)

        assert str(verr).find("need at two Kp Instrument objects to") >= 0

        return

    def test_combine_kp_no_time(self):
        """Test combine_kp raises ValueError when no times are provided."""

        # Remove the start times from the input dict
        del self.combine['start'], self.combine['stop']

        # Raise a value error
        with pytest.raises(ValueError) as verr:
            kp_ap.combine_kp(**self.combine)

        # Test the error message
        assert str(verr).find("must either load in Instrument objects or") >= 0

        return

    def test_combine_kp_no_data(self):
        """Test combine_kp when no data is present for specified times."""

        combo_in = {kk: self.combine['forecast_inst'] for kk in
                    ['standard_inst', 'recent_inst', 'forecast_inst']}
        combo_in['start'] = dt.datetime(2014, 2, 19)
        combo_in['stop'] = dt.datetime(2014, 2, 24)
        kp_inst = kp_ap.combine_kp(**combo_in)

        assert kp_inst.data.isnull().all()["Kp"]

        del combo_in, kp_inst
        return

    def test_combine_kp_no_data_no_files(self):
        """Test combine_kp without data or files for the specified times."""

        # Unset the file list for the instrument
        self.combine['forecast_inst'].files.files = pds.Series([])

        # Set the function inputs
        combo_in = {kk: self.combine['forecast_inst'] for kk in
                    ['standard_inst', 'recent_inst', 'forecast_inst']}
        combo_in['start'] = dt.datetime(2014, 2, 19)
        combo_in['stop'] = dt.datetime(2014, 2, 24)

        # Run the method
        kp_inst = kp_ap.combine_kp(**combo_in)

        # Test the output
        assert kp_inst.data.isnull().all()["Kp"]

        del combo_in, kp_inst
        return

    def test_combine_kp_inst_time(self):
        """Test combine_kp when times are provided through the instruments."""

        combo_in = {kk: self.combine[kk] for kk in
                    ['standard_inst', 'recent_inst', 'forecast_inst']}

        for ikey in combo_in.keys():
            combo_in[ikey].load(**self.load_kwargs)

        kp_inst = kp_ap.combine_kp(**combo_in)

        assert kp_inst.index[0] >= self.combine['start']

        # kp_inst contains times up to 21:00:00, coombine['stop'] is midnight
        assert kp_inst.index[-1].date() <= self.combine['stop'].date()
        assert len(kp_inst.vars_no_time) == 1
        assert 'Kp' in kp_inst.variables

        assert np.isnan(kp_inst['Kp'].attrs['fill_val'])
        assert len(kp_inst['Kp'][np.isnan(kp_inst['Kp'])]) == 0

        del combo_in, kp_inst
        return

    def test_combine_kp_all(self):
        """Test combine_kp when all input is provided."""

        kp_inst = kp_ap.combine_kp(**self.combine)

        assert kp_inst.index[0] >= self.combine['start']
        assert kp_inst.index[-1] < self.combine['stop']
        assert len(kp_inst.vars_no_time) == 1
        assert kp_inst.variables[0] == 'Kp'

        # Fill value is defined by combine
        assert (kp_inst['Kp'].attrs['fill_val'] == self.combine['fill_val'])
        assert (kp_inst['Kp'] != self.combine['fill_val']).all()

        del kp_inst
        return

    def test_combine_kp_no_forecast(self):
        """Test combine_kp when forecasted data is not provided."""

        combo_in = {kk: self.combine[kk] for kk in self.combine.keys()
                    if kk != 'forecast_inst'}
        kp_inst = kp_ap.combine_kp(**combo_in)

        assert kp_inst.index[0] >= self.combine['start']
        assert kp_inst.index[-1] < self.combine['stop']
        assert len(kp_inst.vars_no_time) == 1
        assert 'Kp' in kp_inst.variables
        assert (kp_inst['Kp'].attrs['fill_val'] == self.combine['fill_val'])
        assert (kp_inst['Kp'] == self.combine['fill_val']).any()

        del kp_inst, combo_in
        return

    def test_combine_kp_no_recent(self):
        """Test combine_kp when recent data is not provided."""

        combo_in = {kk: self.combine[kk] for kk in self.combine.keys()
                    if kk != 'recent_inst'}
        kp_inst = kp_ap.combine_kp(**combo_in)

        assert kp_inst.index[0] >= self.combine['start']
        assert kp_inst.index[-1] < self.combine['stop']
        assert len(kp_inst.vars_no_time) == 1
        assert 'Kp' in kp_inst.variables
        assert kp_inst['Kp'].attrs['fill_val'] == self.combine['fill_val']
        assert (kp_inst['Kp'] == self.combine['fill_val']).any()

        del kp_inst, combo_in
        return

    def test_combine_kp_no_standard(self):
        """Test combine_kp when standard data is not provided."""

        combo_in = {kk: self.combine[kk] for kk in self.combine.keys()
                    if kk != 'standard_inst'}
        kp_inst = kp_ap.combine_kp(**combo_in)

        assert kp_inst.index[0] >= self.combine['start']
        assert kp_inst.index[-1] < self.combine['stop']
        assert len(kp_inst.vars_no_time) == 1
        assert 'Kp' in kp_inst.variables
        assert kp_inst['Kp'].attrs['fill_val'] == self.combine['fill_val']
        assert self.combine['fill_val'] in kp_inst['Kp'].values

        del kp_inst, combo_in
        return


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestSWAp(object):
    """Test class for Ap methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        inst_dict = {'num_samples': 10}
        self.test_inst = gdm.Instrument('gdm', 'testing', **inst_dict)
        test_time = gdm.instruments.gdm_testing._test_dates['']['']

        load_kwargs = {'date': test_time}
        self.test_inst.load(**load_kwargs)

        # Create 3 hr Ap data
        self.test_inst[self.test_inst.index.name] = pds.DatetimeIndex(data=[
            test_time + pds.DateOffset(hours=3 * i) for i in range(10)])
        self.test_inst['3hr_ap'] = np.array([0, 2, 3, 4, 5, 6, 7, 9, 12, 15])
        self.test_inst['3hr_ap'].attrs.update({
            'units': '', 'name': 'ap',
            'desc': "3-hour ap (equivalent range) index", 'min_val': 0,
            'max_val': 400, 'fill_val': np.nan, 'notes': 'test ap'})
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.test_inst
        return

    def test_calc_daily_Ap(self):
        """Test daily Ap calculation."""

        kp_ap.calc_daily_Ap(self.test_inst)

        assert 'Ap' in self.test_inst.variables
        assert len(self.test_inst['Ap'].attrs.keys()) > 0

        # Test unfilled values (full days)
        assert np.all(self.test_inst['Ap'][:8].min() == 4.5)

        # Test fill values (partial days)
        assert np.all(np.isnan(self.test_inst['Ap'][8:]))
        return

    def test_calc_daily_Ap_w_running(self):
        """Test daily Ap calculation with running mean."""

        kp_ap.calc_daily_Ap(self.test_inst, running_name="running_ap")

        assert 'Ap' in self.test_inst.variables
        assert len(self.test_inst['Ap'].attrs.keys()) > 0
        assert 'running_ap' in self.test_inst.variables
        assert len(self.test_inst['running_ap'].attrs.keys()) > 0

        # Test unfilled values (full days)
        assert np.all(self.test_inst['Ap'][:8].min() == 4.5)
        assert np.all(self.test_inst['running_ap'][6:].min() == 4.5)

        # Test fill values (partial days)
        assert np.all(np.isnan(self.test_inst['Ap'][8:]))
        assert np.all(np.isnan(self.test_inst['running_ap'][:6]))
        return

    @pytest.mark.parametrize("inargs,vmsg", [
        (["no"], "bad 3-hourly ap variable name"),
        (["3hr_ap", "3hr_ap"], "daily Ap variable name already exists")])
    def test_calc_daily_Ap_bad_3hr(self, inargs, vmsg):
        """Test bad inputs raise ValueError for daily Ap calculation.

        Parameters
        ----------
        inargs : list
            Input arguements that should raise a ValueError
        vmsg : str
            Expected ValueError message

        """

        with pytest.raises(ValueError) as verr:
            kp_ap.calc_daily_Ap(self.test_inst, *inargs)

        assert str(verr).find(vmsg) >= 0
        return

    @pytest.mark.parametrize("ap,out", [(0, 0), (1, 0), (153, 7), (-1, None),
                                        (460, None), (np.nan, None),
                                        (np.inf, None), (-np.inf, None)])
    def test_round_ap(self, ap, out):
        """Test `round_ap` returns expected value for successes and failures.

        Parameters
        ----------
        ap : float
            Input ap
        out : float or NoneType
            Expected output kp or None to use fill_value

        """

        fill_value = -47.0
        if out is None:
            out = fill_value

        assert out == kp_ap.round_ap(ap, fill_val=fill_value)
        return
