#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# Deploy config files.

# This script is NOT supposed to be run directly.
# It is a common part of two deployment methods (see `dev_env_and_target_env_diff.md`):
# *   `bootstrap_outside_venv.bash` FS_66_29_28_85
# *   `bootstrap_inside_venv.bash` FS_90_56_42_04

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

deploy_files_conf_path="./deploy_config_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`$(pwd)/${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of configs to be deployed." 1>&2
    echo "Provide \`$(pwd)/${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    cat << 'deploy_config_files_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).

    # For example (see `deploy_config_files.bash` from `argrelay` repo):
    # project_module argrelay.conf.d argrelay.server.yaml
    # project_module argrelay.conf.d argrelay.client.json
)
########################################################################################################################
deploy_config_files_conf_EOF
    exit 1
fi

# Path `~/.argrelay.conf.d` should be a directory or symlink to directory.
argrelay_conf_dir_path=~/".argrelay.conf.d"
if [[ -e "${argrelay_conf_dir_path}" ]]
then
    if [[ ! -d "${argrelay_conf_dir_path}" ]]
    then
        echo "ERROR: path must be a dir or a symlink to dir: ${argrelay_conf_dir_path}" 1>&2
        exit 1
    fi
else
    mkdir "${argrelay_conf_dir_path}"
fi

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

"${argrelay_path}"/custom_integ_res/deploy_files.bash "${deploy_files_conf_path}" "${deployment_mode}" "${argrelay_conf_dir_path}"

