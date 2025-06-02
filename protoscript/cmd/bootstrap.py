#!/usr/bin/env python3
import os
import sys

os.execv(
    sys.executable,
    [
        sys.executable,
        # Path to `boot_env.py` relative to the project root (which must be the current directory):
        "lib/boot_env.py",
        # Pass the rest of the args intact:
        *sys.argv[1:],
        # Set the config file path according to the project:
        "--proj_conf",
        # The path is relative to the project root (which must be the current directory):
        "conf_proj/boot_env.man.proj.json",
    ],
)
