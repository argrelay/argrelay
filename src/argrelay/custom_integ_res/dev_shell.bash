#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This is just a wrapper to start a new shell with special config and stay in that shell.
# Implements FS_58_61_77_69 dev_shell.

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

# Switch to dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1

# Let some code know that it runs under `dev_shell.bash`:
ARGRELAY_DEV_SHELL="$(date)"
export ARGRELAY_DEV_SHELL

# The new shell executes `init_shell_env.bash` script as its init file:
# https://serverfault.com/questions/368054
bash --init-file <(echo "source ~/.bashrc && source ./init_shell_env.bash")

