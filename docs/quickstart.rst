.. _quickstart:

Quick-Start
===========

Helpful programs should not be hard to figure out!  Hopefully this guide will
get you to the important aspects of your scientific analysis quickly.  If you
haven't installed :py:mod:`GeospaceDataManagement` yet, the :ref:`inst` section
can help you with that.


.. _quickstart-datadir:

Set the Data Directory
----------------------

:py:mod:`GeospaceDataManagement` will maintain organization of data from various
platforms. When you import :py:mod:`GeospaceDataManagement` for the first time,
it will remind you that you need to set this variable for your system.

.. code::

   import GeospaceDataManagement

   Hi there!  GeospaceDataManagement will nominally store data in the 'gdmData'
   directory at the user's home directory level. Set
   `GeospaceDataManagement.params['data_dirs']` equal to a
   path that specifies a top-level directory to store science data.

Most people are fine setting a single path for all of their data, but other
people have a LOT of data and need to store it on multiple disks.
GeospaceDataManagement supports setting the :py:attr:`data_dirs` parameter
equal to either a string or a list of strings, as illustrated in the example
below.

.. code:: python

   # Set a single directory to store all data
   path = '/path/to/your/data/directory/that/may/or/may/not/exist'
   GeospaceDataManagement.params['data_dirs'] = path

   # Alternately, multiple paths may be registered. For a given Instrument,
   # GeospaceDataManagement will iterate through the available options until
   # data files are found. The search will terminate at the first directory
   # with data. If no files are found, the first path is selected by default.
   GeospaceDataManagement.params['data_dirs'] = [path_1, path_2, ..., path_n]

To check the currently set data directory,

.. code:: python

    print(GeospaceDataManagement.params['data_dirs'])


.. _quickstart-load:

Load an Instrument
------------------

The best way to see if :py:mod:`GeospaceDataManagement` is working is to load a
test instrument. The test instrument will simulate data when it is asked to load
data. Loading a day of data will ensure there is no problem with the underlying
installations.

.. code:: python

    # Testing out the 1D data in xarray
    inst = GeospaceDataManagement.Instrument('gdm', 'testing')
    inst.load(2009, 1)
    print(inst.data)

    # Testing out the ND data in xarray
    inst = GeospaceDataManagement.Instrument('gdm', 'ndtesting')
    inst.load(2009, 1)
    print(inst.data)

.. note:: :py:mod:`GeospaceDataManagement` will not allow any
	  :py:class:`Instruments` to be instantiated without a data directory
	  being specified.

.. note:: Test instruments have a limited date range over which they will
	  simulate data.


.. _quickstart-explore:

Explore the Possibilities
-------------------------

At this point, you are set up to start exploring the tools and methods
:py:mod:`GeospaceDataManagement` provides. For a more detailed
dive into :py:mod:`GeospaceDataManagement`, check out the :ref:`tutorial`.
