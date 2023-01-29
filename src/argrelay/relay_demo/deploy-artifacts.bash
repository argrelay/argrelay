#!/usr/bin/env bash

# This script is not supposed to be run directly.
# It is a common part of two deployment methods (see `dev_env_and_target_env_diff.md`):
# *   `build-git-env.bash`
# *   `build-pip-env.bash`

# The high-level steps this script performs:
# *   Deploy user dot files - config for both server and client.
# *   Generate Python scripts to run server and client with current Python `venv` to use.

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

deployment_mode="${1}"

case "${deployment_mode}" in
    "git")
        # Use symlinks to modify files in Git repo:
        deployment_command="ln -snf"
    ;;
    "pip")
        # Use copies to avoid modifying package content:
        deployment_command="cp -p"
    ;;
    *)
        echo "ERROR: unknown deployment_mode=\"${deployment_mode}\"" 1>&1
        exit 1
    ;;
esac

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'PYTHON_GET_MODULE_PATH_EOF'
import argrelay
print(argrelay.__file__)
PYTHON_GET_MODULE_PATH_EOF
)" )"

# Test files to ensure it is the right place:
test -f "${argrelay_path}/relay_demo/argrelay.server.yaml"
test -f "${argrelay_path}/relay_demo/argrelay.client.json"

# Deploy sample config server and client files as user dot files:
if [[ ! -f ~/".argrelay.server.yaml" ]]
then
    eval "${deployment_command}" "${argrelay_path}/relay_demo/argrelay.server.yaml" ~/".argrelay.server.yaml"
fi
if [[ ! -f ~/".argrelay.client.json" ]]
then
    eval "${deployment_command}" "${argrelay_path}/relay_demo/argrelay.client.json" ~/".argrelay.client.json"
fi

# Generate `run_argrelay_server`:
cat << PYTHON_SERVER_EOF > ./run_argrelay_server
#!$(which python)

from argrelay.relay_server.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_SERVER_EOF

# Generate `run_argrelay_client`:
cat << PYTHON_CLIENT_EOF > ./run_argrelay_client
#!$(which python)

from argrelay.relay_client.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_CLIENT_EOF

# Make both executable:
chmod u+x run_argrelay_server
chmod u+x run_argrelay_client
