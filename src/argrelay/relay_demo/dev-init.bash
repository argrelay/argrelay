#!/usr/bin/env bash

# This script is NOT supposed to be run or sourced directly.
# Instead, run `dev-shell.bash`.

# The steps this script:
# *   Runs `build-git-env.bash` first.
# *   Configures Bash auto-completion for command name `relay_demo`.
#     This is what normally done to `~/.bashrc` to make Bash auto-completion permanent.
#     However, the `relay_demo` binding is temporarily (while `dev-shell.bash` is running).

# Note that enabling exit on error (like `set -e` below) will exit parent
# `dev-shell.bash` script (as this one is sourced) - that is intentional.

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

# Switch to the dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1

# Create dev env:
./build-git-env.bash

# Use prepared `venv/relay_demo`:
source venv/relay_demo/bin/activate

# Enable auto-completion:
source ./argrelay-rc.bash

# Show what would be done for `relay_demo` auto-completion:
complete -p relay_demo

# Disable exit on errors and any extra debug info for interactive shell
# (see enabling them for the duration of this script above):
set +o pipefail
set +e
set +u
set +v
set +x
