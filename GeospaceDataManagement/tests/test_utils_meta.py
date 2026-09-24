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
"""Tests the GeospaceDataManagement utils meta functions."""

import numpy as np
import pandas as pds
import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import meta


class TestUpdateFill(object):
    """Tests for the core utility `update_fill_values`."""

    def setup_method(self):
        """Set up the test enviroment."""
        self.ref_time = gdm.instruments.gdm_testing._test_dates['']['']
        self.new_fill_val = -47.0
        self.fill_label = 'fill_val'
        return

    def teardown_method(self):
        """Clean up the test environment."""
        del self.ref_time, self.new_fill_val, self.fill_label
        return

    @pytest.mark.parametrize("name", ["ndtesting", "testing", "testmodel"])
    @pytest.mark.parametrize("variables", [('mlt'), (['mlt'])])
    def test_update_fill_values_numbers(self, name, variables):
        """Test `update_fill_values` for the desired behaviour.

        Parameters
        ----------
        name : str
            Instrument name
        variables : str or list-like
            Variables to update (should be int or float type)

        """

        # Initalize the instrument
        inst = gdm.Instrument('gdm', name)
        inst.load(date=self.ref_time)

        # Ensure there are fill values to check
        test_vars = gdm.utils.listify(variables)
        for var in test_vars:
            if self.fill_label not in inst[var].attrs:
                inst[var].attrs[self.fill_label] = np.nan
            inst[0, var] = inst[var].attrs[self.fill_label]

        # Update the fill values
        meta.update_fill_values(inst, variables, self.fill_label,
                                self.new_fill_val)

        # Ensure the fill values are updated
        for var in test_vars:
            assert inst[var].attrs['fill_val'] == self.new_fill_val, \
                "meta fill value not updated for {:}".format(var)
            assert np.all(inst[0, var] == self.new_fill_val), \
                "filled data values not updated for {:}".format(var)
        return

    @pytest.mark.parametrize("name", ["ndtesting", "testing", "testmodel"])
    def test_update_fill_values_by_type(self, name):
        """Test `update_fill_values` for the desired behaviour.

        Parameters
        ----------
        name : str
            Instrument name

        """

        # Initialize the instrument
        inst = gdm.Instrument('gdm', name)
        inst.load(date=self.ref_time)

        # Ensure there are fill values to check for strings and numbers
        # TODO(#XX) Remove try/except after numpy >= 1.25
        try:
            str_types = [str, np.str_, np.bytes_, np.dtypes.StrDType,
                         np.dtypes.StringDType, np.dtypes.BytesDType,
                         pds.StringDtype]
        except AttributeError:
            str_types = [str, np.str_, np.bytes_, pds.StringDtype]

        str_vars = [var for var in inst.variables
                    if self.fill_label in inst[var].attrs
                    and type(inst[var].dtype) in str_types
                    and inst[var].attrs[self.fill_label] is not None]

        num_vars = [var for var in inst.variables
                    if self.fill_label in inst[var].attrs
                    and var not in inst.data.coords.keys()
                    and inst._get_var_type_code(inst[var].dtype)[0]
                    in ['i', 'u', 'f']
                    and inst[var].attrs[self.fill_label] is not None]

        for var in num_vars:
            inst[0, var] = inst[var].attrs[self.fill_label]

        for var in str_vars:
            inst[0, var] = str(inst[var].attrs[self.fill_label])

        # Update and check the numeric fill values
        meta.update_fill_values(inst, num_vars, self.fill_label,
                                self.new_fill_val)

        for var in num_vars:
            assert inst[var].attrs[self.fill_label] == self.new_fill_val, \
                "meta fill value not updated for {:}".format(var)
            assert np.all(inst[var].values[0] == self.new_fill_val), \
                "filled data values not updated for {:}".format(var)

        # Update and check the string fill values
        self.new_fill_val = 'fill'
        meta.update_fill_values(inst, str_vars, self.fill_label,
                                self.new_fill_val)

        for var in str_vars:
            assert inst[var].attrs[self.fill_label] == self.new_fill_val, \
                "meta fill value not updated for {:}".format(var)
            assert np.all(inst[var].values[0] == self.new_fill_val), \
                "filled data values not updated for {:}".format(var)
        return
