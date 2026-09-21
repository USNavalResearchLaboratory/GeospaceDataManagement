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
"""Unit tests for the `gdm.Instrument.index` attribute."""

from importlib import reload

import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import testing


class TestIndex(object):
    """Unit tests for pandas `gdm.Instrument` index checks."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        reload(gdm.instruments.gdm_testing)
        self.name = 'testing'
        self.ref_time = gdm.instruments.gdm_testing._test_dates['']['']
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.ref_time, self.name
        return

    @pytest.mark.parametrize("kwargs,msg",
                             [({'non_monotonic_index': True},
                               'Loaded data is not monotonic'),
                              ({'non_unique_index': True},
                               'Loaded data is not unique')])
    def test_index_error_messages(self, kwargs, msg):
        """Ensure that a bad Instrument index will raise correct error.

        Parameters
        ----------
        kwargs : dict
            Keywords and arguments to pass through for instrument instantiation.
            Kwargs should trigger an error message when used on a test
            instrument.
        msg : str
            Excerpt of expected error message.

        """

        test_inst = gdm.Instrument(platform='gdm', name=self.name,
                                   num_samples=10, clean_level='clean',
                                   update_files=True, strict_time_flag=True,
                                   **kwargs)
        year, doy = gdm.utils.time.getyrdoy(self.ref_time)
        testing.eval_bad_input(test_inst.load, ValueError, msg,
                               input_args=[year, doy])
        return


class TestIndexXArray(TestIndex):
    """Unit tests for xarray `gdm.Instrument` index checks."""

    def setup_method(self):
        """Set up the unit test environment for each method."""

        self.name = 'ndtesting'
        self.ref_time = gdm.instruments.gdm_testing._test_dates['']['']
        return

    def teardown_method(self):
        """Clean up the unit test environment after each method."""

        del self.ref_time, self.name
        return
