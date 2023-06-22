#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This script sets up dev env (re-installs packages in Python `venv`, sets up symlinks, and so on).
# It is also sourced by `@/exe/init_shell_env.bash` to activate Python `venv`.

# This script should ALWAYS be called with project dir = current dir (see `argrelay_dir` below).

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

# Parse command line args:
for arg_i in "${@}"
do
    if [[ "${arg_i}" == "recursion_flag" ]]
    then
        # If not set, default is empty (no recursion):
        recursion_flag="recursion_flag"
    fi
    if [[ "${arg_i}" == "activate_venv_only_flag" ]]
    then
        # Used by `@/exe/dev_shell.bash` (by `@/exe/init_shell_env.bash`)
        # to activate Python venv only:
        activate_venv_only_flag="activate_venv_only_flag"
    fi
done

# Let some code know that it runs under `@/exe/bootstrap_dev_env.bash` (e.g to run some tests conditionally):
ARGRELAY_BOOTSTRAP_DEV_ENV="$(date)"
export ARGRELAY_BOOTSTRAP_DEV_ENV

# The dir of this script:
# shellcheck disable=SC2034
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Note: In case of `bootstrap_dev_env.bash`, `argrelay_dir` is not `script_dir`, but always the current directory
# (it is supposed to be started from the dir where project is being set up).
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "." )"

# There are several cases this script is called:
# *   (initial boostrap) directly: in that case `script_dir` is inside orig `argrelay` distrib package
# *   (`@/exe/dev_shell.bash`) indirectly: in that case `script_dir` is in `@/exe/` inside integration project dir
# *   (subsequent upgrade) directly: in that case `script_dir` is in `@/exe/` inside integration project dir

# Ensure it is called from project root which should contain `@/exe/` dir:
test -d "${argrelay_dir}/exe/"

# Bash does not allow `return` if the script is not sourced (`exit` must be used):
# https://stackoverflow.com/a/49857550/441652
if [[ "${0}" != "${BASH_SOURCE[0]}" ]]
then
    ret_command="return"
else
    ret_command="exit"
fi

function detect_file_deployment_command {
    # Detect file deployment method based on path of the source (if copy) or the target (if symlink):
    # *   If the path contains path to `venv` (file is from orig package), copy.
    # *   If the path does not contain path to `venv` (file is from sources), symlink.

    # This is the source (if copy) or the target (if symlink):
    primary_path="$( realpath "${1}" )"
    # This is the target (if copy) or the link (if symlink):
    secondary_path="$( realpath "${2}" )"
    # `venv` path from `@/conf/python_conf.bash`:
    # shellcheck disable=SC2154
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

# See `FS_16_07_78_84.conf_dir_priority.md`:
function print_argrelay_conf_dir {

    if [[ -n "${ARGRELAY_CONF_BASE_DIR:-whatever}" ]]
    then
        # If ARGRELAY_CONF_BASE_DIR env var is not defined, use path to user home:
        argrelay_conf_base_dir=~"/.argrelay.conf.d/"

        # Path should be a directory or symlink to directory, otherwise default is `@/conf/`:
        if [[ ! -e "${argrelay_conf_base_dir}" ]]
        then
            argrelay_conf_dir_path="${argrelay_dir}/conf/"
        fi
    else
        argrelay_conf_base_dir="${ARGRELAY_CONF_BASE_DIR}"
    fi

    echo "${argrelay_conf_dir_path}"
}

########################################################################################################################
# Phase 1: init Python

if [[ ! -f "${argrelay_dir}/conf/python_conf.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/conf/python_conf.bash\` does not exists" 1>&2
    echo "It is required to init \`venv\` with specific base Python interpreter." 1>&2
    echo "Provide \`${argrelay_dir}/conf/python_conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be provided by target environment (containing project integrated with `argrelay`).
# It is NOT supposed to be version-controlled per project as it differs per environment.
# It should rather be added to `.gitignore`.

# Path to `venv` to create or reuse:
# shellcheck disable=SC2034
path_to_venvX="venv"
# Path to specific Python interpreter (to override any default in the `PATH`):
# shellcheck disable=SC2034
path_to_pythonX="/usr/local/bin/python3.7"
# Custom prompt prefix - see:
# https://docs.python.org/3/library/venv.html
# --prompt PROMPT Provides an alternative prompt prefix for this environment.
# shellcheck disable=SC2034
venv_prompt_prefix="@"
########################################################################################################################
deploy_project_EOF
    exit 1
fi

# Load user config for env vars:
# *   path_to_pythonX
# *   path_to_venvX
source "${argrelay_dir}/conf/python_conf.bash"
# shellcheck disable=SC2154
echo "path_to_venvX: ${path_to_venvX}"
# shellcheck disable=SC2154
echo "path_to_pythonX: ${path_to_pythonX}"
# shellcheck disable=SC2154
echo "venv_prompt_prefix: ${venv_prompt_prefix:-@}"

if [ ! -e "${path_to_venvX}" ]
then
    pythonX_basename="$(basename "${path_to_pythonX}")"
    pythonX_dirname="$(dirname "${path_to_pythonX}")"

    # Make `pythonX_basename` accessible throughout this script (until `venv` activation overrides it):
    # shellcheck disable=SC2154 # `path_to_pythonX` is assigned in `@/conf/python_conf.bash`:
    export PATH="${pythonX_dirname}:${PATH}"

    # Test python:
    # shellcheck disable=SC2154 # `pythonX_basename` is assigned in `@/conf/python_conf.bash`:
    which "${pythonX_basename}"
    if ! "${pythonX_basename}" -c 'print("'"${pythonX_basename}"' from '"${pythonX_dirname}"' works")'
    then
        echo "ERROR: \`${pythonX_basename}\` from \`${pythonX_dirname}\` does not work" 1>&2
        echo "Update \`${argrelay_dir}/conf/python_conf.bash\` to continue." 1>&2
        exit 1
    fi

    # Start with Python of specific version to prepare `"${path_to_venvX}"`:
    "${pythonX_basename}" -m venv --prompt "${venv_prompt_prefix:-@}" "${path_to_venvX}"
fi

source "${path_to_venvX}"/bin/activate

if [[ -n "${activate_venv_only_flag:-}" ]]
then
    # Ths script is being run by `@/exe/dev_shell.bash` (sourced by `@/exe/init_shell_env.bash`).
    # If bootstrap procedure is required, call `@/exe/bootstrap_dev_env.bash` itself without `activate_venv_only_flag`.
    # Python `venv` has already been activated - return, ignore the rest:
    "${ret_command}" 0
fi

# Continue with Python from `"${path_to_pythonX}"`:
python -m pip install --upgrade pip

########################################################################################################################
# Phase 2: deploy project

if [[ ! -f "${argrelay_dir}/exe/deploy_project.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/exe/deploy_project.bash\` does not exists" 1>&2
    echo "It is required to install packages to extract artifacts from them." 1>&2
    echo "Provide \`${argrelay_dir}/exe/deploy_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the deploy scripts like this should pip-install itself (in the editable mode).

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r "${argrelay_dir}/conf/dev_env_packages.txt"
fi
########################################################################################################################
deploy_project_EOF
    exit 1
fi

source "${argrelay_dir}/exe/deploy_project.bash"

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

if [[ -z "${recursion_flag:-}" ]]
then
    # Overwrite itself:
    cp -p "${argrelay_module_dir_path}/custom_integ_res/bootstrap_dev_env.bash" "${argrelay_dir}/exe/"
    # Recursively call itself again (now with `recursion_flag`:
    "${argrelay_dir}/exe/bootstrap_dev_env.bash" "recursion_flag"
    # Recursive call should have executed the rest of file:
    exit 0
fi

########################################################################################################################
# Phase 4: prepare artifacts: deploy configs (conditionally copies or symlinks)

deploy_files_conf_path="${argrelay_dir}/exe/deploy_config_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of configs to be deployed." 1>&2
    echo "Provide \`${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_config_files_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_dev_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).
    #       Integration assumes different plugins, their configs, etc.

    # For example:
    # project_module sample_conf argrelay.server.yaml
    # project_module sample_conf argrelay.client.json
    # project_module sample_conf dev_env_packages.txt
)
########################################################################################################################
deploy_config_files_conf_EOF
    exit 1
fi

argrelay_conf_dir_path="$( print_argrelay_conf_dir )"
if [[ -e "${argrelay_conf_dir_path}" ]]
then
    if [[ ! -d "${argrelay_conf_dir_path}" ]]
    then
        echo "ERROR: (see FS_16_07_78_84.conf_dir_priority.md) path must be a dir or a symlink to dir: ${argrelay_conf_dir_path}" 1>&2
        exit 1
    fi
fi

deploy_files_procedure "${deploy_files_conf_path}" "detect" "${argrelay_conf_dir_path}"

########################################################################################################################
# Phase 5: prepare artifacts: deploy resources (symlinks)

deploy_files_conf_path="${argrelay_dir}/exe/deploy_resource_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of resources to be deployed." 1>&2
    echo "Provide \`${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_resource_files_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This resource file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_dev_env.bash` to configure `module_path_file_tuples` below.

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

deploy_files_procedure "${deploy_files_conf_path}" "symlink" "${argrelay_dir}/exe/"

########################################################################################################################
# Phase 6: prepare artifacts: generate resources

# Generate `@/bin/run_argrelay_server`:
cat << PYTHON_SERVER_EOF > "${argrelay_dir}/bin/run_argrelay_server"
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/argrelay/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

import os

from argrelay import misc_helper

# FS_29_54_67_86 dir_structure: \`@/bin/run_argrelay_server\` -> \`@/\`:
misc_helper.set_argrelay_dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argrelay.relay_server.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_SERVER_EOF

# Generate `@/bin/run_argrelay_client`:
cat << PYTHON_CLIENT_EOF > "${argrelay_dir}/bin/run_argrelay_client"
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/argrelay/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

import os

from argrelay import misc_helper

# FS_29_54_67_86 dir_structure: \`@/bin/run_argrelay_client\` -> \`@/\`:
misc_helper.set_argrelay_dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argrelay.relay_client.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_CLIENT_EOF

# Make both executable:
chmod u+x "${argrelay_dir}/bin/run_argrelay_client"
chmod u+x "${argrelay_dir}/bin/run_argrelay_server"

########################################################################################################################
# Phase 7: build project

if [[ ! -f "${argrelay_dir}/exe/build_project.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/exe/build_project.bash\` does not exists" 1>&2
    echo "It is required as custom build step for integration project, but can do nothing." 1>&2
    echo "Provide \`${argrelay_dir}/exe/build_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: Why not to consolidate all commit-able `*_conf.bash` files into one?
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'build_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the build scripts like this for integration project should build it and test it.

# It is fine to run tox on every start of FS_58_61_77_69 `dev_shell` because it is only used by `argrelay` devs:
# Build and test:
python -m tox
########################################################################################################################
build_project_EOF
    exit 1
fi

# Provide project-specific build script:
source "${argrelay_dir}/exe/build_project.bash"

########################################################################################################################
# EOF
########################################################################################################################
