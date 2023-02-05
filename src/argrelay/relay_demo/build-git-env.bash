#!/usr/bin/env bash

# This script sets up a dev env for `git clone` deployment method (see `dev_env_and_target_env_diff.md`).
# It does NOT configure Bash for auto-completion - for that,
# see `dev-shell.bash` instead (which calls `dev-init.bash` to do that).

# The high-level steps this script performs:
# *   Configure Python and set up `venv/relay_demo`.
# *   Build `argrelay` and pip-install it in the editable mode.
# *   Run `deploy-artifacts.bash`.

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

# Ensure it is the right dir:
test -f "$(pwd)/src/argrelay/relay_demo/deploy-artifacts.bash"

if [[ ! -f "./python-conf.bash" ]]
then
    echo "ERROR: \`$(pwd)/python-conf.bash\` does not exists" 1>&2
    echo "It is required to init \`venv\` with specific base Python interpreter." 1>&2
    echo "Provide \`$(pwd)/python-conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    cat << 'PYTHON_ENV_CONFIG_EOF'
# Python interpreter command name:
pythonX_command="python3.7"
# Path to Python installation (to override any default in the `PATH`):
path_to_pythonX="/usr/local/bin/"
PYTHON_ENV_CONFIG_EOF
    exit 1
fi

source ./python-conf.bash

# Make `pythonX_command` accessible throughout this script (until `venv` activation overrides it):
# shellcheck disable=SC2154 # `path_to_pythonX` is assigned in `python-conf.bash`:
export PATH="${path_to_pythonX}:${PATH}"

# Test python:
# shellcheck disable=SC2154 # `pythonX_command` is assigned in `python-conf.bash`:
which "${pythonX_command}"
if ! "${pythonX_command}" -c 'print("'"${pythonX_command}"' works")'
then
    echo "ERROR: \`${pythonX_command}\` in \`${path_to_pythonX}\` does not work" 1>&2
    echo "Update \`$(pwd)/python-conf.bash\` to continue." 1>&2
    exit 1
fi

# Prepare `venv/relay_demo` - start with python of specific version:
"${pythonX_command}" -m venv venv/relay_demo
source venv/relay_demo/bin/activate

# Continue with python from `venv/relay_demo`:
python -m pip install --upgrade pip

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r requirements.txt
fi

# Build and test:
python -m tox

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'PYTHON_GET_MODULE_PATH_EOF'
import argrelay
print(argrelay.__file__)
PYTHON_GET_MODULE_PATH_EOF
)" )"

# Run common part for "git" and "pip" deployment modes:
"${argrelay_path}"/relay_demo/deploy-artifacts.bash "git"
