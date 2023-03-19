#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# TODO: Is it possible to run bootstrap_inside_venv.bash from Python on pip install?

# This script sets up a dev env for `pip install` deployment method (see `dev_env_and_target_env_diff.md`).
# Implements FS_90_56_42_04 `pip_deployment`.

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

# Python `venv` is supposed to be pre-configured:
# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

"${argrelay_path}"/custom_integ_res/deploy_config_files.bash "copy"
"${argrelay_path}"/custom_integ_res/deploy_resource_files.bash "symlink"
"${argrelay_path}"/custom_integ_res/generate_artifacts.bash
"${argrelay_path}"/custom_integ_res/run_project_build.bash
