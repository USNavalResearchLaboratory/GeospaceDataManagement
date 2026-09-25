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

import datetime as dt
import numpy as np
import pandas as pds
import pytest

import GeospaceDataManagement as gdm
from GeospaceDataManagement.utils import meta
from GeospaceDataManagement.utils import testing


class TestUpdateFill(object):
    """Tests for the meta utility `update_fill_values`."""

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
        # TODO(#1) Remove try/except after numpy >= 1.25
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


class TestDefaultFillType(object):
    """Tests for the core utility `default_fill_values_from_type`."""

    def setup_method(self):
        """Set up the test enviroment."""
        self.default_fill_vals = {'str': '', 'int': -1, 'obj': None,
                                  'float': np.nan}
        return

    def teardown_method(self):
        """Clean up the test environment."""
        del self.default_fill_vals
        return

    @pytest.mark.parametrize("obj", [dt.datetime(1981, 1, 1), None, True])
    def test_default_fill_values_from_type_obj(self, obj):
        """Test `default_vill_values_from_type` for object defaults.

        Parameters
        ----------
        obj : any object
            Values for whose type a default will be determined

        """
        # Get the fill value and check the output
        assert meta.default_fill_values_from_type(
            type(obj)) is self.default_fill_vals['obj']

        return

    @pytest.mark.parametrize("int_type", [int, np.int16, np.int32, np.int64,
                                          np.short, np.ushort, np.longlong,
                                          np.ulonglong, np.int8])
    def test_default_fill_values_from_type_int(self, int_type):
        """Test `default_vill_values_from_type` for object defaults.

        Parameters
        ----------
        int_type : type
            Various types for integer data

        """
        # Get the fill value and check the output
        assert meta.default_fill_values_from_type(
            int_type) == self.default_fill_vals['int']

        return

    @pytest.mark.parametrize("flt_type", [float, np.single, np.float32,
                                          np.float64, np.float128, np.float16])
    def test_default_fill_values_from_type_float(self, flt_type):
        """Test `default_vill_values_from_type` for object defaults.

        Parameters
        ----------
        flt_type : type
            Various types for integer data

        """
        # Get the fill value and check the output
        assert testing.nan_equal(meta.default_fill_values_from_type(flt_type),
                                 self.default_fill_vals['float'])

        return

    @pytest.mark.parametrize("str_type", [str, np.str_])
    def test_default_fill_values_from_type_string(self, str_type):
        """Test `default_vill_values_from_type` for object defaults.

        Parameters
        ----------
        str_type : type
            Various types for integer data

        """
        # Get the fill value and check the output
        assert meta.default_fill_values_from_type(
            str_type) == self.default_fill_vals['str']

        return


class TestDefaultMetaDict(object):
    """Tests for the core utility `get_meta_dict`."""

    def setup_method(self):
        """Set up the test enviroment."""
        # Float is NaN, can't use equality
        self.default_out = {'units': '', 'name': '', 'min_val': -np.inf,
                            'max_val': np.inf, 'fill_val': np.nan, 'desc': '',
                            'notes': ''}
        return

    def teardown_method(self):
        """Clean up the test environment."""
        del self.default_out
        return

    def test_get_meta_dict_default(self):
        """Test the default output for `get_meta_dict`."""

        out = meta.get_meta_dict()
        testing.assert_lists_equal(list(out.keys()),
                                   list(self.default_out.keys()))
        testing.assert_lists_equal(list(out.values()),
                                   list(self.default_out.values()))
        return

    def test_get_meta_dict_extra(self):
        """Test the default output for `get_meta_dict` with additional data."""

        out = meta.get_meta_dict(**{'extra': 'value'})
        testing.assert_list_contains(list(self.default_out.keys()),
                                     list(out.keys()))
        testing.assert_list_contains(list(self.default_out.values()),
                                     list(out.values()))
        assert 'extra' in out.keys()
        assert 'value' == out['extra']
        return

    def test_get_meta_dict_replacement(self):
        """Test the default output for `get_meta_dict` with replacement data."""

        out = meta.get_meta_dict(**{'notes': 'actual note'})
        testing.assert_lists_equal(list(self.default_out.keys()),
                                   list(out.keys()))

        for dkey in self.default_out.keys():
            if dkey == 'notes':
                assert 'actual note' in out[dkey]
            elif dkey in ['desc', 'units']:
                assert self.default_out[dkey] == out[dkey]
            else:
                assert testing.nan_equal(self.default_out[dkey], out[dkey])
        return


class TestStandardizeMeta(object):
    """Tests for the meta utility `standardize_meta_attrs`."""

    def setup_method(self):
        """Set up the test enviroment."""
        self.ref_time = gdm.instruments.gdm_testing._test_dates['']['']
        self.default_meta = meta.get_meta_dict()
        self.fill_label = [dkey for dkey in self.default_meta.keys()
                           if dkey.find('fill') == 0][0]
        self.inst = None
        return

    def teardown_method(self):
        """Clean up the test environment."""
        del self.ref_time, self.default_meta, self.inst, self.fill_label
        return

    @pytest.mark.parametrize("name", ["ndtesting", "testing", "testmodel"])
    @pytest.mark.parametrize("include_time", [True, False])
    @pytest.mark.parametrize("default_dict", [None, {'extra': 'value'}])
    def test_standardize_inst(self, name, include_time, default_dict):
        """Test the standardization of meta data across an instrument.

        Parameters
        ----------
        name : str
            Instrument name
        include_time : bool
            Include the time variable in the metadata update
        default_dict : dict or NoneType
            Include extra metadata in the update

        """
        # Initalize the instrument
        self.inst = gdm.Instrument('gdm', name)
        self.inst.load(date=self.ref_time)

        # Verify that metadata is not uniform
        len_check = [len(self.inst.meta_labels) == len(self.inst[var].attrs)
                     for var in self.inst.variables]
        assert not np.all(len_check)

        # Update the meta data
        meta.standardize_meta_attrs(self.inst, include_time=include_time,
                                    default_dict=default_dict,
                                    fill_label=self.fill_label)

        # Verify that the metadata is uniform across the desired variables
        vlist = self.inst.variables if include_time else self.inst.vars_no_time

        len_check = [len(self.inst.meta_labels) == len(self.inst[var].attrs)
                     for var in vlist]
        assert np.all(len_check)

        if default_dict is not None:
            testing.assert_list_contains(list(default_dict.keys()),
                                         self.inst.meta_labels)
        return
