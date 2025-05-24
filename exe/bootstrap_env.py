#!/usr/bin/env python

########################################################################################################################
# This section should be executable by Python 2.

import sys

if sys.version_info[0] < 3:
    print(sys.executable)
    raise AssertionError(
        "the major version[" +
        str(sys.version_info[0]) +
        "] of python [" +
        sys.executable +
        "] is too old"
    )

########################################################################################################################

