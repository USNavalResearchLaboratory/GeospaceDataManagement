#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in CITATION.cff
#
# ----------------------------------------------------------------------------
# Original Authors: pysat development team (c) 2020, pysat
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Test methods for the Madrigal GNSS instrument methods."""

import datetime as dt
import logging
import pytest

from GeospaceDataManagement.utils.testing import eval_bad_input
try:
    from GeospaceDataManagement.instruments.madrigal_methods import gnss
    no_mad = False
except ImportError:
    no_mad = True


@pytest.mark.skipif(no_mad, reason="Madrigal test only")
class TestGNSSRefs(object):
    """Test the acknowledgements and references for the GNSS instruments."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.out
        return

    @pytest.mark.parametrize("func, comp_str, in_args", [
        ('acknowledgements', 'GPS TEC data products', ['tec']),
        ('references', 'Rideout and Coster', ['tec'])])
    def test_ref_output(self, func, comp_str, in_args):
        """Test the GNSS acknowledgements and references."""
        self.out = getattr(gnss, func)(*in_args)
        assert self.out.find(comp_str) >= 0
        return


@pytest.mark.skipif(no_mad, reason="Madrigal test only")
class TestGNSSBadLoad(object):
    """Test GNSS load warnings and errors."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.bad_fnames = ['los_20230101.simple.gz', 'los_20230102.netCDF4']
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.bad_fnames
        return

    def test_bad_file_type_warning(self, caplog):
        """Test logger warning for unsupported file types loading LoS data."""

        # Get the output and raise the logging warning
        with caplog.at_level(logging.WARN, logger='GeospaceDataManagement'):
            gnss.load_los(self.bad_fnames, "site", "zzon")

        # Test the logger warning
        assert len(caplog.records) == 2, "unexpected number of warnings"

        for record in caplog.records:
            assert record.levelname == "WARNING"
            assert record.message.find("unable to load non-HDF5 slant TEC") >= 0
        return

    def test_bad_sel_type(self):
        """Test ValueError raised for an unknown LoS down-selection type."""

        eval_bad_input(gnss.load_los, ValueError, "unsupported selection type",
                       input_args=[self.bad_fnames, "bad_sel", "bad_val"])
        return

    def test_empty_los_load(self):
        """Test the returned dataset is empty for a LoS load."""
        data, lats, lons = gnss.load_los(self.bad_fnames, "time",
                                         dt.datetime(2023, 1, 1))

        assert len(data.sizes.keys()) == 0
        assert len(lats) == 2
        assert len(lons) == 2
        return
