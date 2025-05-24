#!/usr/bin/env bash

# Install `pre-commit` hooks.

# It is expected to be run from started `@/exe/dev_shell.bash`.

# It must be run from repo root:
#     ./exe/install_pre_commit.bash

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

# Debug: Print commands before execution:
#set -x
# Debug: Print commands after reading from a script:
#set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

# Switch to `@/` to avoid creating temporary dirs somewhere else:
cd "${argrelay_dir}" || exit 1

pip install pre-commit

pre-commit run --all-files
