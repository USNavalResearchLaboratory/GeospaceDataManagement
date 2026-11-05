.. _tutorial-params:

Parameters
==========

The :py:class:`GeospaceDataMangement.params` class provides a central location
for storing a variety of parameters used by :py:mod:`GeospaceDataMangement`, as
well as custom user provided settings. An overview of currently stored
parameters may be found using:

.. code:: python

   import GeospaceDataManagement as gdm
   print(gdm.params)

   Out[]:
   GeospaceDataManagement Parameters object
   ----------------------------------------
   Tracking 7 GeospaceDataManagement Parameters settings
   Tracking 1 settings (non-default)
   Tracking 0 user values

   Standard parameters:
   clean_level : clean
   directory_format : {platform}/{name}/{tag}/{inst_id}
   ignore_empty_files : False
   file_timeout : 10
   update_files : True
   user_modules : {'gdm': {'ndtesting': 'GeospaceDataManagement.instruments.gdm_ndtesting', 'netcdf': 'GeospaceDataManagement.instruments.gdm_netcdf', 'testing': 'GeospaceDataManagement.instruments.gdm_testing', 'testmodel': 'GeospaceDataManagement.instruments.gdm_testmodel'}}
   warn_empty_file_list : False

   Standard parameters (no defaults):
   data_dirs : ['~/AllMyData/gdmData']

   User parameters:

Most parameters may be assigned or updated via standard assignment and are
stored to disk automatically in a thread-safe manner.

.. code:: python

   # Update existing file_timeout parameter
   gd,.params['file_timeout'] = 15

   # Add new user parameter
   gdm.params[user_param_str] = user_param_value

All of the standard parameters above may be restored to defaults using:

.. code:: python

   gdm.params.restore_defaults()

but this command leaves parameters with no working defaults, like
:py:data:`data_dirs`, unchanged. To clear all parameters:

.. code:: python

   gdm.params.clear_and_restart()

A description of each of the parameters and its use in
:py:mod:`GeospaceDataManagement` may be found using:

.. code::

   help(gdm.params)

   Default parameters and values tracked by this class:
       Values that map to the corresponding keywords on gdm.Instrument.
            'clean_level' : 'clean'
            'directory_format' : os.path.join('{platform}', '{name}',
                                              '{tag}', '{inst_id}')
            'ignore_empty_files': False
            'update_files': True

       Values that map to internal gdm settings:
            'file_timeout': 10; Window in time (seconds) that gdm will wait
                to load/write a file while another thread uses that file
                before giving up.
            'user_modules' : {}; Stores information on modules registered within
                gdm. Used by `gdm.utils.registry`
            'warn_empty_file_list' : False; Raises a warning if no files are
                found for a given gdm.Instrument.

       Stored gdm parameters without a working default value:
            'data_dirs': Stores locations of top-level directories gdm uses to
                store and load data.



The :py:data:`data_dirs` setting is required to successfully instantiate a
:py:class:`~GeospaceDataManagement._instrumet.Instrument` object.

The :py:data:`user_modules` parameter is used by the
:py:mod:`GeospaceDataMangement.utils.registry` module and may not be modified
through direct assignment.
