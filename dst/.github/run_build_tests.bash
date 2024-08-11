#!/usr/bin/env bash

# This script executes sub-set of tests suitable for CI.

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

# Not running `tox` as it expects all Python versions present
# within the environment while CI environments may have only one of
# the Python versions per runner (each runner runs with its own
# Python version, not all) and we are not selecting them
# for `tox` conditionally.
# Instead, run some selected tests which do not need extra dependencies
# (e.g. do not run `gui_tests`):
# TODO: TODO_04_84_79_11: Re-group tests to
#       exclude truly online (going to Internet, but do not exclude end to end, for example):
for test_group in \
offline_tests \
release_tests \
slow_tests \

do
    ./exe/dev_shell.bash ./exe/run_max_tests.bash ./tests/"${test_group}"
done
