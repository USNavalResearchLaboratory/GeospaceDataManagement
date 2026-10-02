"""Imports for the Space Weather instrument methods."""

try:
    from GeospaceDataManagement.instruments.sw_methods import ace  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import auroral_electrojet  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import dst  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import f107  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import general  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import gfz  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import norp  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import kp_ap  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import lasp  # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import lisird # noqa F401
    from GeospaceDataManagement.instruments.sw_methods import swpc  # noqa F401
except ImportError:
    raise ImportError('missing Space Weather dependencies')
