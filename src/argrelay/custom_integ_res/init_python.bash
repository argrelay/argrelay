#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script sets up Python and `venv`.

# This script should ALWAYS be called with project dir = current dir.

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

if [[ ! -f "./python_conf.bash" ]]
then
    echo "ERROR: \`$(pwd)/python_conf.bash\` does not exists" 1>&2
    echo "It is required to init \`venv\` with specific base Python interpreter." 1>&2
    echo "Provide \`$(pwd)/python_conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'python_env_config_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This config file is supposed to be provided by target environment using `argrelay`.
# It is NOT supposed to be version-controlled per project as it differs per environment.
# It should rather be added to `.gitignore`.

# Path to `venv` to create or reuse:
path_to_venvX="venv"
# Path to specific Python interpreter (to override any default in the `PATH`):
path_to_pythonX="/usr/local/bin/python3.7"
########################################################################################################################
python_env_config_EOF
    exit 1
fi

# Load user config for env vars:
# *   path_to_pythonX
# *   path_to_venvX
source ./python_conf.bash
# shellcheck disable=SC2154
echo "path_to_venvX: ${path_to_venvX}"
# shellcheck disable=SC2154
echo "path_to_pythonX: ${path_to_pythonX}"

if [ ! -e "${path_to_venvX}" ]
then
    pythonX_basename="$(basename "${path_to_pythonX}")"
    pythonX_dirname="$(dirname "${path_to_pythonX}")"

    # Make `pythonX_basename` accessible throughout this script (until `venv` activation overrides it):
    # shellcheck disable=SC2154 # `path_to_pythonX` is assigned in `python_conf.bash`:
    export PATH="${pythonX_dirname}:${PATH}"

    # Test python:
    # shellcheck disable=SC2154 # `pythonX_basename` is assigned in `python_conf.bash`:
    which "${pythonX_basename}"
    if ! "${pythonX_basename}" -c 'print("'"${pythonX_basename}"' from '"${pythonX_dirname}"' works")'
    then
        echo "ERROR: \`${pythonX_basename}\` from \`${pythonX_dirname}\` does not work" 1>&2
        echo "Update \`$(pwd)/python_conf.bash\` to continue." 1>&2
        exit 1
    fi

    # Prepare `"${path_to_venvX}"` - start with Python of specific version:
    "${pythonX_basename}" -m venv "${path_to_venvX}"
fi
source "${path_to_venvX}"/bin/activate

# Continue with Python from `"${path_to_pythonX}"`:
python -m pip install --upgrade pip

