.. _inst:


Installation
============

Python and associated packages for science are freely available. Convenient
science python package setups are available from `<https://www.python.org/>`_,
`Anaconda <https://www.anaconda.com/download/>`_, and other locations
(some platform specific). Core science packages such as numpy, scipy,
matplotlib, pandas and many others may also be installed directly via the
python package installer "pip" or your favorite package manager.

.. _inst-standard:

Standard installation
---------------------

GeospaceDataManagement itself may be installed from a terminal command line::

   pip install GeospaceDataManagement


.. _inst-dev:

Development Installation
------------------------

GeospaceDataManagement may also be installed directly from the source
repository on GitHub::

   git clone https://github.com/USNavalResearchLaboratory/GeospaceDataManagement.git
   cd GeospaceDataManagement
   python -m build .
   pip install --user .

An advantage to installing through github is access to the development branches.
The latest bugfixes can be found in the ``develop`` branch. However, this
branch is not stable (as the name implies). We recommend using this branch in a
virtual environment and using::

   git clone https://github.com/USNavalResearchLaboratory/GeospaceDataManagement.git
   cd GeospaceDataManagement
   git checkout develop
   python -m build .
   pip install -e .

The use of `-e` in the setup command installs the code 'in-place', so any
changes to the software do not have to be reinstalled to take effect. It is not
related to changing the pysat working branch from ``main`` to ``develop`` in the
preceeding line.
