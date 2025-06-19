#!/usr/bin/env python3
import os
import sys

# TODO: replace it by normal relative import and call to `main`, default `proj_conf` and extra bootstrappers:
os.execv(
    sys.executable,
    [
        sys.executable,
        # Path to `proto_code.py` relative to the project root (which must be the current directory):
        "lib/proto_code.py",
        # Pass the rest of the args intact:
        *sys.argv[1:],
    ],
)
