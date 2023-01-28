#!/usr/bin/env bash

# This is just a wrapper to start a new shell with special config and stay in that shell.

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

# Switch to dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1

# Let some code know that it runs under `dev-shell.bash`:
ARGRELAY_DEV_SHELL="$(date)"
export ARGRELAY_DEV_SHELL

# The new shell executes `dev-init.bash` script interactively as its init file:
# https://serverfault.com/questions/368054
bash --init-file <(echo "source ~/.bashrc && source ./dev-init.bash")
