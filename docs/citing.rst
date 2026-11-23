Citations
=========

When referring to this software package, please cite the package using the
example below. 

Example for citation in BibTex for a generalized version:

.. code::

  @misc{gdm_code,
    author       = {Burrell, A.G.},
    title        = {GeospaceDataManagement vX.Y.Z},
    year         = 2026,
    url          = {https://github.com/USNavalResearchLaboratory/GeospaceDataManagement}
  }

To aid in scientific reproducibility, please include the version number in
publications that use this code.  This can be found by invoking
:py:attr:`GeospaceDataManagement.__version__`.

Information for appropriately acknowledging and citing the different instruments
accessed through GeospaceDataManagement is available as Instrument attributes
:py:attr:`inst.acknowledgements` and :py:attr:`inst.references`.  If this
information is missing or out of date, please consider submitting an issue or
adding the information yourself through a pull request.


MadrigalWeb
-----------

If you are accessing Madrigal data, GeospaceDataManagement uses
`MadrigalWeb <https://pypi.org/project/madrigalWeb/>`_ to access this database.
This package is described in the following journal article.

* Burrell A. G., et al. (2018). Snakes on a Spaceship - An Overview of Python in
  Heliophysics. Journal of Geophysical Research: Space Physics, 123,
  doi:10.1029/2018ja025877.
