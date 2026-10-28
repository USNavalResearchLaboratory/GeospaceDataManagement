Change Log
==========
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

[0.0.3] - 2026-10-XX
--------------------
* ENH:
  - Added the ability to turn GFZ download certificate verification on and off
  - Added a warning if some of the requested download days were not retrieved
* BUG:
  - Fixed F10.7 data concatonation (default index name, assigning meta data)
  - Ensure Kp meta data exists before attempting access
* DOC:
  - Updated redirecting links

[0.0.2] - 2026-10-02
--------------------
* ENH:
  - Added Space Weather instruments as an optional installation
  - Allow `generate_instrument_list` to include only a subset of the instruments
* BUG:
  - Fixed assignment issue in Instrument, where meta data could not be added if
    a variable did not exist
  - Fixed assignment issue in Instrument, where xarray behaviour changed in
    more recent versions of Python
* DOC:
  - Added missing sections to docstrings
  - Added information about space weather instruments and methods

[0.0.1] - 2026-09-25
--------------------
Initial Release
