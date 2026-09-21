# -*- coding: utf-8 -*-
"""Collection of test instruments for the core GeospaceDataManagement routines.

Each instrument is contained within a subpackage of this set.
"""

__all__ = ['gdm_ndtesting', 'gdm_netcdf', 'gdm_testing',
           'gdm_testmodel']

for inst in __all__:
    exec("from GeospaceDataManagement.instruments import {x}".format(x=inst))

del inst
