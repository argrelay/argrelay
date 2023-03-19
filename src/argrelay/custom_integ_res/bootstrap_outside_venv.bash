#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script sets up a dev env for `git clone` deployment method (see `dev_env_and_target_env_diff.md`).
# Implements FS_66_29_28_85 `git_deployment`.

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

# There are two ways this script is called:
# *   (initial boostrap) directly: in that case `script_dir` is inside orig `argrelay` distrib package
# *   (`dev_shell.bash`) indirectly: in that case `script_dir` is inside integration project dir
#     (and this script started via symlink from there)
# The curr dir is not change into `script_dir` to deploy files in the (curr) integration project directory.

# This is why the script has to be symlinked to the project dir:
"${script_dir}"/init_python.bash

# Activate pre-configured Python `venv`:
source ./python_conf.bash
# shellcheck disable=SC2154
source "${path_to_venvX}"/bin/activate

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

"${argrelay_path}"/custom_integ_res/deploy_config_files.bash "symlink"
"${argrelay_path}"/custom_integ_res/deploy_resource_files.bash "symlink"
"${argrelay_path}"/custom_integ_res/generate_artifacts.bash
"${argrelay_path}"/custom_integ_res/run_project_build.bash
