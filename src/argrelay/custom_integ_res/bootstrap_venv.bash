#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script sets up Python and `venv`.

# This script should ALWAYS be called with project dir = current dir.

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

# If not set, default is empty (no recursion):
recursion_flag="${1:-}"

# Let some code think as if it runs under `dev_shell.bash` (to disable some tests):
ARGRELAY_DEV_SHELL="$(date)"
export ARGRELAY_DEV_SHELL

# The dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# There are two ways this script is called:
# *   (initial boostrap) directly: in that case `script_dir` is inside orig `argrelay` distrib package
# *   (`dev_shell.bash`) indirectly: in that case `script_dir` is inside integration project dir
# The curr dir is not change into `script_dir` to deploy files in the (curr) integration project directory.

function detect_file_deployment_command {
    # Detect file deployment method based on path of the source (if copy) or the target (if symlink):
    # *   If the path contains path to `venv` (file is from orig package), copy.
    # *   If the path does not contain path to `venv` (file is from sources), symlink.

    # This is the source (if copy) or the target (if symlink):
    primary_path="$( realpath "${1}" )"
    # This is the target (if copy) or the link (if symlink):
    secondary_path="$( realpath "${2}" )"
    # `venv` path from `python_conf.bash`:
    abs_path_to_venvX="$( realpath "${path_to_venvX}")"

    if [[ "${primary_path}" == "${abs_path_to_venvX}"* ]]
    then
        file_deployment_command="cp -p"
    else
        file_deployment_command="ln -sn"
    fi

    eval "${file_deployment_command}" "${primary_path}" "${secondary_path}"
}

function deploy_files_procedure {

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
            file_deployment_command="ln -sn"
        ;;
        "copy")
            # Use copies (e.g. to avoid modifying orig package content):
            file_deployment_command="cp -p"
        ;;
        "detect")
            file_deployment_command="detect_file_deployment_command"
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

            if [[ -z "${module_path}" ]]
            then
                return 1
            fi

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
}

########################################################################################################################
# Phase 1: init Python

if [[ ! -f "./python_conf.bash" ]]
then
    echo "ERROR: \`$(pwd)/python_conf.bash\` does not exists" 1>&2
    echo "It is required to init \`venv\` with specific base Python interpreter." 1>&2
    echo "Provide \`$(pwd)/python_conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This config file is supposed to be provided by target environment (containing project integrated with `argrelay`).
# It is NOT supposed to be version-controlled per project as it differs per environment.
# It should rather be added to `.gitignore`.

# Path to `venv` to create or reuse:
path_to_venvX="venv"
# Path to specific Python interpreter (to override any default in the `PATH`):
path_to_pythonX="/usr/local/bin/python3.7"
########################################################################################################################
deploy_project_EOF
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

########################################################################################################################
# Phase 2: deploy project

if [[ ! -f "./deploy_project.bash" ]]
then
    echo "ERROR: \`$(pwd)/deploy_project.bash\` does not exists" 1>&2
    echo "It is required to install packages to extract artifacts from them." 1>&2
    echo "Provide \`$(pwd)/deploy_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This is a custom build script *sourced* by `bootstrap_venv.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the deploy scripts like this for integration project should pip-install it (in the editable mode).

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r requirements.txt
fi
########################################################################################################################
deploy_project_EOF
    exit 1
fi

# TODO: source all *_conf files (make them non-executable) and remove all set -e in them:
source ./deploy_project.bash

# Get path of `argrelay` module:
argrelay_module_file_path="$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)"
argrelay_module_dir_path="$( dirname "${argrelay_module_file_path}" )"

########################################################################################################################
# Phase 3: recurse into fresh copy of itself

if [[ -z "${recursion_flag}" ]]
then
    # Overwrite itself:
    cp -p "${argrelay_module_dir_path}"/custom_integ_res/bootstrap_venv.bash "."
    # Recursively call itself again (now with `recursion_flag`:
    ./bootstrap_venv.bash "recursion_flag"
    # Recursive call should have executed the rest of file:
    exit 0
fi

########################################################################################################################
# Phase 4: prepare artifacts: deploy configs (conditionally copies or symlinks)

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
# It is *sourced* by `bootstrap_venv.bash` to configure `module_path_file_tuples` below.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).
    #       Integration assumes different plugins, their configs, etc.

    # For example (see `deploy_config_files.bash` from `argrelay` repo):
    # project_module argrelay.conf.d argrelay.server.yaml
    # project_module argrelay.conf.d argrelay.client.json
)
########################################################################################################################
deploy_config_files_conf_EOF
    exit 1
fi

# If ARGRELAY_CONF_BASE_DIR is exported env var, argrelay_conf_base_dir is local:
argrelay_conf_base_dir="${ARGRELAY_CONF_BASE_DIR:-$(eval echo ~)}"

# Path `~/.argrelay.conf.d` should be a directory or symlink to directory.
argrelay_conf_dir_path="${argrelay_conf_base_dir}/.argrelay.conf.d"
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

deploy_files_procedure "${deploy_files_conf_path}" "detect" "${argrelay_conf_dir_path}"

########################################################################################################################
# Phase 5: prepare artifacts: deploy resources (symlinks)

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
# It is *sourced* by `bootstrap_venv.bash` to configure `module_path_file_tuples` below.

# Tuples specifying resource files, format:
# module_name relative_dir_path resource_file_name
module_path_file_tuples=(
    argrelay custom_integ_res dev_shell.bash
    argrelay custom_integ_res init_shell_env.bash
    argrelay custom_integ_res argrelay_rc.bash
)
########################################################################################################################
deploy_resource_files_conf_EOF
    exit 1
fi

deploy_files_procedure "${deploy_files_conf_path}" "symlink" "."

########################################################################################################################
# Phase 6: prepare artifacts: deploy resources (symlinks)

# Generate `run_argrelay_server`:
cat << PYTHON_SERVER_EOF > ./run_argrelay_server
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/uvsmtid/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

from argrelay.relay_server.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_SERVER_EOF

# Generate `run_argrelay_client`:
cat << PYTHON_CLIENT_EOF > ./run_argrelay_client
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/uvsmtid/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

from argrelay.relay_client.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_CLIENT_EOF

# Make both executable:
chmod u+x run_argrelay_server
chmod u+x run_argrelay_client

########################################################################################################################
# Phase 7: build project

if [[ ! -f "./build_project.bash" ]]
then
    echo "ERROR: \`$(pwd)/build_project.bash\` does not exists" 1>&2
    echo "It is required as custom build step for integration project, but can do nothing." 1>&2
    echo "Provide \`$(pwd)/build_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'build_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This is a custom build script *sourced* by `bootstrap_venv.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the build scripts like this for integration project should build it and test it.

# It is fine to run tox on every start of `dev_shell` because
# this `git_deployment` (FS_66_29_28_85) is only used by `argrelay` devs:
# Build and test:
python -m tox
########################################################################################################################
build_project_EOF
    exit 1
fi

# Provide project-specific build script:
source ./build_project.bash

########################################################################################################################
# EOF
########################################################################################################################
