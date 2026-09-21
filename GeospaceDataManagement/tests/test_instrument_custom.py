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
"""Unit tests for the `custom_attach` methods for `gdm.Instrument`."""

import copy
import logging
import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import testing


def mult_data(inst, mult, dkey="mlt"):
    """Add a multiplied data value to an Instrument.

    Parameters
    ----------
    inst : gdm.Instrument
        Instrument object
    mult : float or int
        Multiplicative value
    dkey : str
        Key for data that will be multiplied (default='mlt')

    Notes
    -----
    Adds multiplied data to Instrument using a key name with the format
    {mult}x{dkey}

    """
    # Construct the new data key
    out_key = '{:.0f}x{:s}'.format(mult, dkey)

    # Add the new data to the instrument
    inst.data[out_key] = mult * inst.data[dkey]

    return


class TestLogging(object):
    """Unit tests for logging interface with custom functions."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.testInst = gdm.Instrument('gdm', 'testing', num_samples=10,
                                       clean_level='clean', update_files=False)
        self.out = ''
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.testInst, self.out
        return

    def test_custom_pos_warning(self, caplog):
        """Test for logging warning if inappropriate position specified."""

        with caplog.at_level(logging.WARNING, logger='GeospaceDataManagement'):
            self.testInst.custom_attach(lambda inst: inst.data['mlt'] * 2.0,
                                        at_pos=3)
        self.out = caplog.text

        assert self.out.find(
            "unknown position specified, including function at end") >= 0
        return


class TestBasics(object):
    """Unit tests for `gdm.instrument.custom_attach` with pandas data."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.testInst = gdm.Instrument('gdm', 'testing', num_samples=10,
                                       clean_level='clean', update_files=True)
        self.load_date = gdm.instruments.gdm_testing._test_dates['']['']
        self.testInst.load(date=self.load_date)
        self.custom_args = [2]
        self.out = None
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.testInst, self.out, self.custom_args
        return

    def test_basic_str(self):
        """Check for lines from each decision point in str."""

        self.out = self.testInst.__str__()
        assert isinstance(self.out, str)

        # No custom functions
        assert self.out.find('0 applied') > 0
        return

    def test_basic_repr(self):
        """Test `__repr__` with a custom method."""

        self.testInst.custom_attach(mult_data, args=self.custom_args)
        self.testInst.custom_attach(mult_data, args=self.custom_args)
        self.out = self.testInst.__repr__()
        assert isinstance(self.out, str)
        assert self.out.find("'function'") >= 0
        return

    def test_basic_str_w_function(self):
        """Check for lines from each decision point in str."""

        self.testInst.custom_attach(mult_data, args=self.custom_args,
                                    kwargs={'dkey': 'mlt'})

        # Execute custom method
        self.testInst.load(date=self.load_date)

        # Store output to be tested
        self.out = self.testInst.__str__()
        assert isinstance(self.out, str)

        # No custom functions
        assert self.out.find('1 applied') > 0
        assert self.out.find('mult_data') > 0
        assert self.out.find('Args') > 0
        assert self.out.find('Kwargs') > 0
        return

    def test_single_custom_function_error(self):
        """Test for error if custom function returns a value."""

        def custom_with_return_data(inst):
            inst.data['doubleMLT'] = 2.0 * inst.data.mlt
            return 5.0 * inst.data['mlt']

        estr = 'Custom functions should not return any information via return'
        self.testInst.custom_attach(custom_with_return_data)

        testing.eval_bad_input(self.testInst.load, ValueError, estr,
                               input_kwargs={'date': self.load_date})
        return

    def test_custom_keyword_instantiation(self):
        """Test adding custom methods at Instrument instantiation."""

        self.testInst.custom_attach(mult_data, args=self.custom_args,
                                    kwargs={'dkey': 'mlt'})
        self.testInst.custom_attach(mult_data, args=self.custom_args)

        # Create another instance of gdm.Instrument and add custom
        # via the input keyword
        custom = [{'function': mult_data, 'args': self.custom_args,
                   'kwargs': {'dkey': 'mlt'}},
                  {'function': mult_data, 'args': self.custom_args}]
        testInst2 = gdm.Instrument('gdm', 'testing', custom=custom)

        # Ensure both instruments have the same custom_* attributes
        assert self.testInst.custom_functions == testInst2.custom_functions
        assert self.testInst.custom_args == testInst2.custom_args
        assert self.testInst.custom_kwargs == testInst2.custom_kwargs
        return

    def test_custom_positioning(self):
        """Test custom method ordering specification."""

        self.testInst.custom_attach(mult_data, args=[3],
                                    kwargs={'dkey': '2xmlt'})
        self.testInst.custom_attach(mult_data, at_pos=0, args=self.custom_args)

        # Create another instance of gdm.Instrument and add custom
        # via the input keyword
        custom = [{'function': mult_data, 'args': [3],
                   'kwargs': {'dkey': '2xmlt'}},
                  {'function': mult_data, 'at_pos': 0,
                   'args': self.custom_args}]
        testInst2 = gdm.Instrument('gdm', 'testing', custom=custom)

        # Ensure both Instruments have the same custom_* attributes
        assert self.testInst.custom_functions == testInst2.custom_functions
        assert self.testInst.custom_args == testInst2.custom_args
        assert self.testInst.custom_kwargs == testInst2.custom_kwargs

        # Ensure the run order was correct
        assert self.testInst.custom_args[0] == self.custom_args
        assert self.testInst.custom_args[1] == [3]
        return

    def test_custom_keyword_instantiation_poor_format(self):
        """Test for error when custom missing keywords at instantiation."""

        req_words = ['function']
        real_custom = [{'function': 1, 'args': [0, 1],
                        'kwargs': {'kwarg1': True, 'kwarg2': False}}]
        for i, word in enumerate(req_words):
            custom = copy.deepcopy(real_custom)
            custom[0].pop(word)

            # Ensure that any of the missing required words raises an error
            with pytest.raises(ValueError) as err:
                gdm.Instrument('gdm', 'testing', custom=custom)

            # Ensure correct error for the missing parameter (word)
            assert str(err).find(word) >= 0
            assert str(err).find('Input dict to custom is missing') >= 0

        return

    def test_clear_functions(self):
        """Test successful clearance of custom functions."""

        self.testInst.custom_attach(lambda inst, imult, out_units='h':
                                    {'data': (inst.data.mlt * imult).values,
                                     'long_name': 'doubleMLTlong',
                                     'units': out_units, 'name': 'doubleMLT'},
                                    args=[2], kwargs={"out_units": "hours1"})

        # Test to see that the custom function was attached
        assert len(self.testInst.custom_functions) == 1
        assert len(self.testInst.custom_args) == 1
        assert len(self.testInst.custom_kwargs) == 1

        self.testInst.custom_clear()
        # Test to see that the custom function was cleared
        assert self.testInst.custom_functions == []
        assert self.testInst.custom_args == []
        assert self.testInst.custom_kwargs == []
        return


class TestBasicsXarray(TestBasics):
    """Unit tests for `gdm.instrument.custom_attach` with an xarray inst."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.testInst = gdm.Instrument('gdm', 'ndtesting',
                                       num_samples=10, clean_level='clean')
        self.load_date = gdm.instruments.gdm_ndtesting._test_dates
        self.load_date = self.load_date['']['']
        self.testInst.load(date=self.load_date)
        self.custom_args = [2]
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.testInst, self.load_date, self.custom_args
        return
