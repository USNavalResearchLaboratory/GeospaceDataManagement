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
"""Integration and unit test suite for GFZ methods."""

import datetime as dt
import pytest
import tempfile

import GeospaceDataManagement as gdm
try:
    from GeospaceDataManagement.instruments.sw_methods import gfz
    no_sw = False
except ImportError:
    no_sw = True


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestGFZMethods(object):
    """Test class for GFZ methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Prepare for testing downloads
        self.tempdir = tempfile.TemporaryDirectory()
        self.saved_path = gdm.params['data_dirs']
        gdm.params._set_data_dirs(path=self.tempdir.name, store=False)
        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        # Clean up the GeospaceDataManagement parameter space
        gdm.params._set_data_dirs(self.saved_path, store=False)

        del self.tempdir, self.saved_path
        return

    def test_kp_ap_cp_download_bad_inst(self):
        """Test the download doesn't work for an incorrect Instrument."""
        with pytest.raises(ValueError) as verr:
            gfz.kp_ap_cp_download('platform', 'name', 'tag', 'inst_id',
                                  [dt.datetime.now(tz=dt.timezone.utc)],
                                  'data/path')

        assert str(verr).find('Unknown Instrument module') >= 0
        return
