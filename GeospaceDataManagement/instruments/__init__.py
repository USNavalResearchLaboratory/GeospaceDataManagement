# -*- coding: utf-8 -*-
"""Collection of test instruments for the core GeospaceDataManagement routines.

Each instrument is contained within a subpackage of this set.
"""

__test__ = ['gdm_ndtesting', 'gdm_netcdf', 'gdm_testing',
            'gdm_testmodel']
__all__ = list(__test__)

from GeospaceDataManagement.instruments import methods  # noqa 401
try:
    from GeospaceDataManagement.instruments import sw_methods  # noqa 401
    __sw__ = ['ace_epam', 'ace_mag', 'ace_sis', 'ace_swepam', 'norp_rf',
              'sw_ae', 'sw_al', 'sw_ap', 'sw_apo', 'sw_au', 'sw_cp',
              'sw_dst', 'sw_f107', 'sw_flare', 'sw_hpo', 'sw_kp',
              'sw_mgii', 'sw_polarcap', 'sw_sbfield', 'sw_ssn',
              'sw_stormprob']
    __all__.extend(__sw__)
except ImportError as ierr:
    import GeospaceDataManagement
    GeospaceDataManagement.logger.info(ierr)

for inst in __all__:
    exec("from GeospaceDataManagement.instruments import {x}".format(x=inst))

del inst
