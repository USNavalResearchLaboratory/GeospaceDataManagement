"""GeospaceDataManagement (a.k.a. gdm).

A package providing a simple and flexible interface for
downloading, loading, cleaning, and managing scientific measurements.

"""
# ----------------------------------------------------------------------------
# Original Authors: pysat development team (c) 2016, Russell Stoneback
#
# Modified 2026+
# This is a U.S. government work and not under copyright protection in the U.S.
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------

from importlib import metadata
from importlib import resources

import logging
import os

# Logger needs to be initialized before other modules are imported.
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

# Import statements after this point require a noqa statement for flake8

# Import and set user and GeospaceDataManagement parameters object
from GeospaceDataManagement import _params  # noqa: E402 F401

# Set version
__version__ = metadata.version('GeospaceDataManagement')

# Get home directory
home_dir = os.path.expanduser('~')

# Set GeospaceDataManagement directory path in home directory
gdm_dir = os.path.join(home_dir, '.gdm')

# Set directory for test data
if resources is None:
    test_data_path = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                  'tests', 'test_data')
    citation = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                            'citation.txt')
else:
    test_data_path = str(resources.files(__package__).joinpath('tests',
                                                               'test_data'))
    citation = str(resources.files(__package__).joinpath('citation.txt'))

# Create a .gdm directory or parameters file if one doesn't exist.
settings_file = os.path.join(gdm_dir, 'gdm_settings.json')
if not os.path.isdir(gdm_dir) or not os.path.isfile(settings_file):

    # Make a .gdm directory if not already present
    if not os.path.isdir(gdm_dir):
        os.mkdir(gdm_dir)
        ostr = ''.join(('Created .gdm directory in home directory to store ',
                        'settings.'))
        logger.info(ostr)

    # Make additional internal directories
    if not os.path.isdir(os.path.join(gdm_dir, 'instruments')):
        os.mkdir(os.path.join(gdm_dir, 'instruments'))

    if not os.path.isdir(os.path.join(gdm_dir, 'instruments', 'archive')):
        os.mkdir(os.path.join(gdm_dir, 'instruments', 'archive'))

    # Create parameters file
    if not os.path.isfile(settings_file):
        params = _params.Parameters(path=gdm_dir, create_new=True)

    print(''.join(("\nHi there!  GeospaceDataManagement will nominally store ",
                   "data in a 'gdmData' directory which needs to be assigned. ",
                   "Please run `GeospaceDataManagement.params['data_dirs'] = ",
                   "path` where path specifies one or more existing top-level",
                   " directories that may be used to store science data. ",
                   "`path` may either be a single string or a list of ",
                   "strings.")))
else:
    # Load up existing parameters file
    params = _params.Parameters()

# Modules used by other imports needs to be imported here first.
from GeospaceDataManagement import utils  # noqa: E402 F401

# Import the remainder of the modules.
from GeospaceDataManagement._files import Files  # noqa: E402 F401
from GeospaceDataManagement._instrument import Instrument  # noqa: E402 F401
from GeospaceDataManagement import instruments  # noqa: E402 F401

__all__ = ['instruments', 'utils']

# Clean up
del settings_file, resources
