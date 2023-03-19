#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# Deploy files.

# This script is NOT supposed to be run directly - see other scripts invoking this one.

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

deploy_files_conf_path="${1}"
deployment_mode="${2}"
target_dir="${3}"

# Load user config for env vars:
# *   module_path_file_tuples
# shellcheck disable=SC1090
source "${deploy_files_conf_path}"

case "${deployment_mode}" in
    "symlink")
        # Use symlinks (e.g. to modify files when they are part of Git repo):
        file_deployment_command="ln -snf"
    ;;
    "copy")
        # Use copies (e.g. to avoid modifying orig package content):
        file_deployment_command="cp -p"
    ;;
    *)
        echo "ERROR: unknown deployment_mode: \"${deployment_mode}\"" 1>&2
        exit 1
    ;;
esac

# Verify number of items in `module_path_file_tuples` is divisible by 3:
# shellcheck disable=SC2154
if [[ "$((${#module_path_file_tuples[@]}%3))" != "0" ]]
then
    echo "ERROR: Number of items in \`module_path_file_tuples\` is not divisible by 3" 1>&2
    exit 1
fi

for i in "${!module_path_file_tuples[@]}"
do
    if [[ "$((i%3))" == "0" ]]
    then
        module_name="${module_path_file_tuples[i+0]}"
        relative_dir_path="${module_path_file_tuples[i+1]}"
        file_name="${module_path_file_tuples[i+2]}"

        # Python `venv` has to be activated.
        # Get path of `argrelay` module:
        module_path="$( dirname "$(
python << python_module_path_EOF
import ${module_name}
print(${module_name}.__file__)
python_module_path_EOF
            )" )"

        # Test file:
        config_file_path="${module_path}/${relative_dir_path}/${file_name}"
        test -f "${config_file_path}"

        # Deploy sample config server and client files as user dot files:
        if [[ ! -e "${target_dir}/${file_name}" ]]
        then
            eval "${file_deployment_command}" "${config_file_path}" "${target_dir}/${file_name}"
        fi
    fi
done

