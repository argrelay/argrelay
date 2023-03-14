#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This is a custom build script sourced by `init_python.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the build scripts like this for all integration projects should
# pip-install the project in the editable mode, build it and test it.

# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Error on undefined variables:
set -u
# Debug: Print commands after reading from a script:
#set -v
# Debug: Print commands before execution:
#set -x

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r requirements.txt
fi

# It is fine to run tox on every start of `dev_shell` because
# this `git_deployment` (FS_66_29_28_85) is only used by `argrelay` devs:
# Build and test:
python -m tox

