"""Imports for the Madrigal instrument methods."""

try:
    from GeospaceDataManagement.instruments.madrigal_methods import dmsp  # noqa F401
    from GeospaceDataManagement.instruments.madrigal_methods import general  # noqa F401
    from GeospaceDataManagement.instruments.madrigal_methods import gnss  # noqa F401
    from GeospaceDataManagement.instruments.madrigal_methods import jro  # noqa F401
except ImportError:
    raise ImportError('missing Madrigal dependencies')
