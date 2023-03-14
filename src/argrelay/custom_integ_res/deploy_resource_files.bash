#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# Deploy resource files.

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

deploy_files_conf_path="./deploy_resource_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`$(pwd)/${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of resources to be deployed." 1>&2
    echo "Provide \`$(pwd)/${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_resource_files_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This resource file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

# Tuples specifying resource files, format:
# module_name relative_dir_path resource_file_name
module_path_file_tuples=(
    argrelay custom_integ_res dev_shell.bash
    argrelay custom_integ_res init_shell_env.bash
    argrelay custom_integ_res init_python.bash
    argrelay custom_integ_res argrelay_rc.bash
)
########################################################################################################################
deploy_resource_files_conf_EOF
    exit 1
fi

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

"${argrelay_path}"/custom_integ_res/deploy_files.bash "${deploy_files_conf_path}" "symlink" "."

