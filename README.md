GeospaceDataManagement provides a simple and flexible interface for robust data
analysis from beginning to end - with a focus on downloading, loading, cleaning
and managing scientific data.  The project's plug-in design allows analysis
support for any data, including user provided data sets.

# Installation

The following instructions provide a guide for installing GeospaceDataManagement
and give some examples on how to use the routines.

## Prerequisites

GeospaceDataManagement uses common Python modules, as well as modules developed
by and for the Space Physics community.

| Common modules | Community modules |
| -------------- | ----------------- |
| dask           | netCDF4           |
| numpy          |                   |
| pandas         |                   |
| portalocker    |                   |
| pytest         |                   |
| scipy          |                   |
| toolz          |                   |
| xarray         |                   |


## GitHub Installation
```
git clone https://github.com/USNavalResearchLaboratory/GeospaceDataManagement.git
```

Change directories into the repository folder and run the pyproject.toml or
setup.py file.  For a local install use the "--user" flag after "install".

```
cd GeospaceDataManagement/
python -m build .
pip install .
```

# Using GeospaceDataManagement

* The first time this package is run, you will need to specify a directory to
  store the data. In Python, run:
```
import GeospaceDataManagement as gdm
gdm.params['data_dirs'] = 'path/to/directory/that/may/or/may/not/exist'
```
  * Nominal organization of data is top_dir/platform/name/tag/inst_id/files

Detailed examples and tutorials for using GeospaceDataManagement are available
in the documentation (docs directory)
