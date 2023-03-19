#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script is a wrapper to call `build_project.bash` (project-specific build script).

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

if [[ ! -f "./build_project.bash" ]]
then
    echo "ERROR: \`$(pwd)/build_project.bash\` does not exists" 1>&2
    echo "It is required as custom build step for integration project, but can do nothing." 1>&2
    echo "Provide \`$(pwd)/build_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    cat << 'python_env_config_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# The file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# See also `build_project.bash` in `argrelay` repo.

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

if false
then
    # Use editable install:
    # https://pip.pypa.io/en/latest/topics/local-project-installs/
    python -m pip install -e .
fi

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r requirements.txt
fi

if false
then
    # Optionally build and test:
    python -m tox
fi
########################################################################################################################
python_env_config_EOF
    exit 1
fi

# Provide project-specific build script:
source ./build_project.bash
