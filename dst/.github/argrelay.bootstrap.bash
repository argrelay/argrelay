#!/usr/bin/env bash

# GitHub job script to run `@/exe/bootstrap_dev_env.bash`
# Steps:
# *   Configure `@/conf` dir to point to `@/dst/.github/`.
# *   Run bootstrap.

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

# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Note that this script expects no `@/conf/` config,
# so the location it knows is not through `@/conf/` but the direct one via `@/dst/`:
# FS_29_54_67_86 dir_structure: `@/dst/.github/` -> `@/`:
argrelay_dir="$( dirname "$( dirname "${script_dir}" )" )"

# There should be no `conf` in the repo
# (it is supposed to be configured locally e.g. to point somewhere under `@/dst/`):
test ! -d "${argrelay_dir}/conf"

# Bootstrap should be run from the target dir:
cd "${argrelay_dir}"
ln -sn "dst/.github" "conf"
./exe/bootstrap_dev_env.bash

# TODO: verify there is no local changes
