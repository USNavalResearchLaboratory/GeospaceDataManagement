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
"""Integration and unit test suite for AE methods."""

import pytest

try:
    from GeospaceDataManagement.instruments.sw_methods import auroral_electrojet
    no_sw = False
except ImportError:
    no_sw = True


@pytest.mark.skipif(no_sw, reason="Space Weather test only")
class TestAEMethods(object):
    """Test class for the auroral electrojet methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.out = None
        return

    def teardown_method(self):
        """Clean up previous testing setup."""
        del self.out
        return

    @pytest.mark.parametrize('name', ['ae', 'al', 'au'])
    def test_acknowledgements(self, name):
        """Test the auroral electrojet acknowledgements.

        Parameters
        ----------
        name : str
            Instrument name

        """
        self.out = auroral_electrojet.acknowledgements(name, 'lasp')
        assert self.out.find(name.upper()) >= 0
        return

    @pytest.mark.parametrize('name', ['ae', 'al', 'au'])
    def test_references(self, name):
        """Test the references for an AE instrument.

        Parameters
        ----------
        name : str
            Instrument name

        """
        self.out = auroral_electrojet.references(name, 'lasp')
        assert self.out.find('Davis, T. N.') >= 0
        return
