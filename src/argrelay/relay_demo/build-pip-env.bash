#!/usr/bin/env bash

# This script sets up a dev env for `pip install` deployment method (see `dev_env_and_target_env_diff.md`).
# It does NOT configure Bash for auto-completion - for that, either/or:
# *   Configure auto-completion permanently - follow instructions in `argrelay-rc.bash`.
# *   Create a shell script similar to `dev-shel.bash` for this project where `argrelay` is `pip`-installed.

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

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'PYTHON_GET_MODULE_PATH_EOF'
import argrelay
print(argrelay.__file__)
PYTHON_GET_MODULE_PATH_EOF
)" )"

# Run common part for "git" and "pip" deployment modes:
"${argrelay_path}"/relay_demo/deploy-artifacts.bash "pip"

function copy_artifact {
    artifact_basename="${1}"
    if [[ ! -f "${artifact_basename}" ]]
    then
        cp -p "${argrelay_path}/relay_demo/${artifact_basename}" "${artifact_basename}"
    fi
}

copy_artifact "build-pip-env.bash"
copy_artifact "argrelay-rc.bash"
