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
"""Integration and unit test suite for ACE methods."""

import numpy as np
import pytest

import GeospaceDataManagement as gdm
try:
    from GeospaceDataManagement.instruments.sw_methods import general
    no_sw = False
except ImportError:
    no_sw = True


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestGeneralMethods(object):
    """Test class for general methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.inst = gdm.Instrument('gdm', 'testing')
        self.inst.load(date=self.inst.inst_module._test_dates[''][''])
        self.var = self.inst.variables[0]
        self.fill_label = 'fill_val'
        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        del self.inst, self.var, self.fill_label
        return

    def test_preprocess(self):
        """Test the preprocessing routine updates all fill values to be NaN."""

        # Make sure at least one fill value is not already NaN
        self.inst[self.var].attrs['fill_val'] = 0.0

        # Update the meta data using the general preprocess routine
        general.preprocess_fill(self.inst, fill_label=self.fill_label)

        # Test the output
        assert np.isnan(self.inst[self.var].attrs[self.fill_label])
        return
