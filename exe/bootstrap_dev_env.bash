#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This script should ALWAYS be called with current dir = project dir `@/` (see `argrelay_dir` below).

# This script sets up dev env (re-installs packages in Python `venv`, sets up symlinks, and so on).
# It is also sourced by `@/exe/init_shell_env.bash` to activate Python `venv`.

# These are the flags recognized by this script (in command line args):
# *   `recursion_flag`
#     called as sub-shell
# *   `activate_venv_only_flag`
#     called by sourcing
# The first unrecognized arg is treated as `config_path` (see usage).

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

if [[ -n "${bootstrap_dev_env_old_opts+x}" ]] ; then exit 1 ; fi

# Save `set`-able options to restore them at the end of this source-able script:
# https://unix.stackexchange.com/a/383581/23886
# Not saving history because:
# *   it is not modified within `argrelay` scripts
# *   it should not be restored in non-interactive files (disabled by default)
bootstrap_dev_env_old_opts="$( set +o | grep -v "[[:space:]]history$" )"
case "${-}" in
    *e*) bootstrap_dev_env_old_opts="${bootstrap_dev_env_old_opts}; set -e" ;;
      *) bootstrap_dev_env_old_opts="${bootstrap_dev_env_old_opts}; set +e" ;;
esac

########################################################################################################################

# Keep output-related `set`-able options same when this script is sourced
# (otherwise, full debug output for bootstrap is adequate as it runs in hardly predictable target environment):
if [[ "${0}" == "${BASH_SOURCE[0]}" ]] ; then

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v

fi

# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

########################################################################################################################

if [[ "${0}" != "${BASH_SOURCE[0]}" ]]
then
    # sourced from another script:
    is_script_sourced="true"
else
    # executed directly in its own shell:
    is_script_sourced="false"
fi

########################################################################################################################

# Bash does not allow `return` if the script is not sourced (`exit` must be used):
# https://stackoverflow.com/a/49857550/441652
# But using `exit` would exit the caller script (which sources this bootstrap).
# Using `return` outside of func would exit the caller script as well, but this is manageable -
# to avoid that, the caller should wrap calling bootstrap into a func.
# Pick the command conditionally:
if [[ "${is_script_sourced}" == "true" ]]
then
    ret_command="return"
else
    ret_command="exit"
fi

########################################################################################################################

success_color="\e[42m"
failure_color="\e[41m"
reset_color="\e[0m"

# Indicate success|failure by color:
function color_failure_and_success_bootstrap_env {
    exit_code="${?}"
    if [[ "${exit_code}" == "0" ]]
    then
        # Only if this script is NOT sourced by another:
        if [[ "${0}" == "${BASH_SOURCE[0]}" ]]
        then
            echo -e "${success_color}SUCCESS:${reset_color} ${BASH_SOURCE[0]}" 1>&2
        fi
    else
        echo -e "${failure_color}FAILURE:${reset_color} ${BASH_SOURCE[0]}: exit_code: ${exit_code}" 1>&2
        "${ret_command}" "${exit_code}"
    fi
}

trap color_failure_and_success_bootstrap_env EXIT

# Let some code know that it runs under `@/exe/bootstrap_dev_env.bash` (e.g to run some tests conditionally):
ARGRELAY_BOOTSTRAP_DEV_ENV="$(date)"
export ARGRELAY_BOOTSTRAP_DEV_ENV

script_source="${BASH_SOURCE[0]}"
# shellcheck disable=SC2034
script_name="$( basename -- "${script_source}" )"
# The dir of this script:
# shellcheck disable=SC2034
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# Note: In case of `bootstrap_dev_env.bash`, `argrelay_dir` is not `script_dir`, but always the current directory
# (it is supposed to be started from the dir where project is being set up).
# FS_29_54_67_86 dir_structure: current dir = `@/`:
argrelay_dir="$( dirname "." )"

# There are several cases this script is called:
# *   (initial bootstrap) directly: in that case `script_dir` is inside orig `argrelay` distrib package
# *   (`@/exe/dev_shell.bash`) indirectly: in that case `script_dir` is in `@/exe/` inside integration project dir
# *   (subsequent upgrade) directly: in that case `script_dir` is in `@/exe/` inside integration project dir

# Ensure it is called from project root (which should contain `@/exe/` dir):
test -d "${argrelay_dir}/exe/"

# Collect flags from command line args:
unused_input_args=()
for arg_i in "${@}"
do

    if [[ "${arg_i}" == "recursion_flag" ]]
    then
        # If not set, default is empty (no recursion):
        recursion_flag="recursion_flag"
        continue
    fi

    if [[ "${arg_i}" == "activate_venv_only_flag" ]]
    then
        # Used by `@/exe/dev_shell.bash` (by `@/exe/init_shell_env.bash`)
        # to activate Python venv only:
        activate_venv_only_flag="activate_venv_only_flag"
        continue
    fi

    unused_input_args+=( "${arg_i}" )
done

########################################################################################################################
# Bootstrap with `path/to/config` arg (if any) triggers this special logic:
# *   if `@/conf/` is missing:
#     *   set `@/conf/` symlink to the specified config dir (e.g. one of `@/dst/*`)
#     *   continue running bootstrap
# *   if `@/conf/` already exists:
#     *   assume bootstrap is already completed
#     *   ensures the target matches the one specified and does nothing (fails if not)
#     *   skip running bootstrap
if [[ "${#unused_input_args[@]}" -gt "0" ]]
then

    # Ensure dir exists:
    config_path="${unused_input_args[0]}"
    test -d "${config_path}"

    if [[ -d "${argrelay_dir}/conf" ]]
    then
        # Ensure `@/conf/` points to the specified `config_path`
        # (if `@/conf/` points to something else - remove it to reset manually):
        readlink "${argrelay_dir}/conf" || echo "WARN: \`readlink\` failed" 1>&2 && true
        test "${argrelay_dir}/conf" -ef "${config_path}"

        # The `@/conf/` has already been init-ed before:
        echo "INFO: \"${argrelay_dir}/conf\" with the same path exists - skip running bootstrap" 1>&2

        "${ret_command}" 0
    elif [[ ! -e "${argrelay_dir}/conf" ]]
    then
        # Setting symlink `@/conf/` to the selected config
        # (convert to relative path first):
        config_path="$( realpath --relative-to="${argrelay_dir}" "${config_path}" )"
        ln -snf "${config_path}" "${argrelay_dir}/conf"

        # Load Python config to reset its `venv`:
        source "${argrelay_dir}/conf/python_conf.bash"

        # Careful: instead of `rm -rf` (in case of misconfig), move `venv` to `/tmp/`:
        run_timestamp="$( date -u "+%Y-%m-%dT%H-%M-%SZ" )"
        # shellcheck disable=SC2154
        if [[ -e "${path_to_venvX}" ]]
        then
            backup_dst_path="/tmp/$( basename "${path_to_venvX}" ).backup.${run_timestamp}"
            mv "${path_to_venvX}" "${backup_dst_path}"
        fi

        # Next: continue with bootstrap...
    else
        echo "ERROR: \"${argrelay_dir}/conf\" exists but it does not point to dir: (re-)move it manually" 1>&2
        "${ret_command}" 1
    fi
fi

# Ensure `@/conf/` exists:
test -d "${argrelay_dir}/conf/"

########################################################################################################################
# Init Python.

if [[ ! -f "${argrelay_dir}/conf/python_conf.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/conf/python_conf.bash\` does not exists" 1>&2
    echo "It is required to init \`venv\` with specific base Python interpreter." 1>&2
    echo "Provide \`${argrelay_dir}/conf/python_conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

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
    "${ret_command}" 1
fi

# Load user config for env vars:
# *   path_to_pythonX
# *   path_to_venvX
source "${argrelay_dir}/conf/python_conf.bash"

# Cut out Python version number chars (from first digit until first space):
# shellcheck disable=SC2154
curr_python_version="$( "${path_to_pythonX}" --version 2>&1 | sed 's/^[^[:digit:]]*\([^[:space:]]*\).*$/\1/g' )"
# Ensure Python version is not old:
min_required_version="3.7"
if [[ "${curr_python_version}" != "${min_required_version}" ]]
then
    if ( echo "${curr_python_version}"; echo "${min_required_version}"; ) | sort --version-sort --check 2> /dev/null
    then
        # versions sorted = curr Python version is older:
        "${ret_command}" 1
    fi
fi

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
        "${ret_command}" 1
    fi

    # Start with Python of specific version to prepare `"${path_to_venvX}"`:
    "${pythonX_basename}" -m venv --prompt "${venv_prompt_prefix:-@}" "${path_to_venvX}"
fi

# Activate `venv` with reduced output:
# Save `set`-able options to restore them at the end of this source-able script:
# https://unix.stackexchange.com/a/383581/23886
# See above regarding `history`:
venv_activation_old_opts="$( set +o | grep -v "[[:space:]]history$" )"
case "${-}" in
    *e*) venv_activation_old_opts="${venv_activation_old_opts}; set -e" ;;
      *) venv_activation_old_opts="${venv_activation_old_opts}; set +e" ;;
esac
source "${path_to_venvX}"/bin/activate
eval "${venv_activation_old_opts}"
unset venv_activation_old_opts

# Convert `path_to_venvX` to `abs_path_to_venvX`:
if [[ "${path_to_venvX:0:1}" == "/" ]]
then
    abs_path_to_venvX="${path_to_venvX}"
else
    abs_path_to_venvX="$(pwd)/${path_to_venvX}"
fi

# Verify that Python versions for `path_to_pythonX` and `abs_path_to_venvX/bin/python` match:
python_version_a="$( "${path_to_pythonX}" --version )"
python_version_b="$( "${abs_path_to_venvX}/bin/python" --version )"
if [[ "${python_version_a}" != "${python_version_b}" ]]
then
    # One way to attempt to resolve this is to remove `venv` and re-run `@/exe/bootstrap_dev_env.bash`:
    echo "ERROR: version mismatch for Python to init \`venv\` and Python in existing \`venv\`: ${python_version_a} ${python_version_b}" 1>&2
    "${ret_command}" 1
fi

# Verify that `/path/to/python` after activation is the same file pointed to by `path_to_pythonX`.
# If not, it is likely that chain of `python` symlinks within the new `venv` is broken
# (leads to non-existing `python` binary) which should fail fast (otherwise, partially working state is confusing):
full_path_to_python="$( command which python )"
if [[ ! "${full_path_to_python}" -ef "${path_to_pythonX}" ]]
then
    # One way to attempt to resolve this is to remove `venv` and re-run `@/exe/bootstrap_dev_env.bash`:
    echo "ERROR: path to \`python\` binary = \`${full_path_to_python}\` after activation of \`venv\` = \`${abs_path_to_venvX}\` is not linked to \`python\` binary = \`${path_to_pythonX}\` used to create this \`venv\`" 1>&2
    "${ret_command}" 1
fi

# Verify shebang using `/path/to/python` does not exceed the limit
# (otherwise, shebang for client and server scripts will not work):
# https://stackoverflow.com/a/10813634/441652
# Applying conservative limit for the first line including both the first two chars `#!` and `${full_path_to_python}`
# (which may be higher or lower but can always be fixed for bootstrap script copy temporarily if blocking):
if [[ "${#full_path_to_python}" -gt "125" ]]
then
    echo "ERROR: path to \`python\` binary = \`${full_path_to_python}\` after activation of \`venv\` = \`${abs_path_to_venvX}\` exceeds 127 chars" 1>&2
    "${ret_command}" 1
fi

if [[ -n "${activate_venv_only_flag:-}" ]]
then
    # Ths script is being run by `@/exe/dev_shell.bash` (sourced by `@/exe/init_shell_env.bash`).
    # If bootstrap procedure is required, call `@/exe/bootstrap_dev_env.bash` itself without `activate_venv_only_flag`.
    # Python `venv` has already been activated - return, ignore the rest:
    "${ret_command}" 0
fi

# Continue with Python from `"${path_to_pythonX}"`:
# - Use latest `pip`:
python -m pip install --upgrade pip
# - This avoids error on `import pkg_resources`:
#   ModuleNotFoundError: No module named 'pkg_resources'
python -m pip install --upgrade setuptools

# Ensure `@/conf/dev_env_packages.txt` exists:
touch "${argrelay_dir}/conf/dev_env_packages.txt"

########################################################################################################################
# Deploy project dependencies.

if [[ ! -f "${argrelay_dir}/exe/deploy_project.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/exe/deploy_project.bash\` does not exists" 1>&2
    echo "It is required to install packages to extract artifacts from them." 1>&2
    echo "Provide \`${argrelay_dir}/exe/deploy_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom deployment script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the deploy scripts like this should pip-install itself (in the editable mode).

# Saved dev dependencies (if clean deployment is required, make `@/conf/dev_env_packages.txt` file empty):
python -m pip install -r "${argrelay_dir}/conf/dev_env_packages.txt"

# Use editable mode:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]
########################################################################################################################
deploy_project_EOF
    "${ret_command}" 1
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
# Recurse into fresh copy of bootstrap.

if [[ -z "${recursion_flag:-}" ]]
then
    # Overwrite itself:
    cp -p "${argrelay_module_dir_path}/custom_integ_res/bootstrap_dev_env.bash" "${argrelay_dir}/exe/"
    # Recursively call itself again (now with `recursion_flag`):
    "${argrelay_dir}/exe/bootstrap_dev_env.bash" "recursion_flag"
    # Recursive call should have executed the rest of file:
    "${ret_command}" 0
fi

########################################################################################################################
# Define common deployment functions.

function detect_file_deployment_command {
    # This func is used for the editable install mode cases.
    # When config files (not resource files) need to be deployed from a distribution package,
    # that package might be installed in editable mode.
    # *   If in editable mode, use symlinks.
    # *   If not in editable mode, use copy.
    # The detection of editable mode is done by looking at the `venv` path in the orig file.
    #
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
    # Whether override should be used or not depends on whether the file is a config or it is a resource:
    # *   config files are specific to target environment and are kept untouched (manually updated if needed)
    # *   resource files are common for all deployments - they represent the latest update and should be overriden
    override_target_file="${4}"

    # Load user config for env vars:
    # *   module_path_file_tuples
    # shellcheck disable=SC1090
    source "${deploy_files_conf_path}"

    case "${deployment_mode}" in
        "symlink_method")
            # Use symlinks (e.g. to modify files when they are part of Git repo):
            file_deployment_command="ln -sn"
        ;;
        "copy_method")
            # Use copies (e.g. to avoid modifying orig package content):
            file_deployment_command="cp -p"
        ;;
        "detect_method")
            file_deployment_command="detect_file_deployment_command"
        ;;
        *)
            echo "ERROR: unknown deployment_mode: \"${deployment_mode}\"" 1>&2
            "${ret_command}" 1
        ;;
    esac

    # Verify number of items in `module_path_file_tuples` is divisible by 3:
    # shellcheck disable=SC2154
    if [[ "$((${#module_path_file_tuples[@]}%3))" != "0" ]]
    then
        echo "ERROR: Number of items in \`module_path_file_tuples\` is not divisible by 3" 1>&2
        "${ret_command}" 1
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

            # Test existence of the source file:
            config_file_path="${module_path}/${relative_dir_path}/${file_name}"
            test -f "${config_file_path}"

            # Deploy file to the target:
            if [[ ! -e "${target_dir}/${file_name}" ]] && [[ ! -L "${target_dir}/${file_name}" ]]
            then
                eval "${file_deployment_command}" "${config_file_path}" "${target_dir}/${file_name}"
            else
                if [[ "${override_target_file}" == "override_target_file" ]]
                then
                    rm "${target_dir}/${file_name}"
                    eval "${file_deployment_command}" "${config_file_path}" "${target_dir}/${file_name}"
                fi
            fi
        fi
    done
}

########################################################################################################################
# Prepare artifacts: deploy configs (conditionally copies or symlinks).

deploy_files_conf_path="${argrelay_dir}/exe/deploy_config_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of configs to be deployed." 1>&2
    echo "Provide \`${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
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
    # project_module sample_conf argrelay_server.yaml
    # project_module sample_conf argrelay_client.json
)
########################################################################################################################
deploy_config_files_conf_EOF
    "${ret_command}" 1
fi

# See `FS_16_07_78_84.conf_dir_priority.md`:
if [[ -n "${ARGRELAY_CONF_BASE_DIR+x}" ]]
then
    argrelay_conf_base_dir="${ARGRELAY_CONF_BASE_DIR}"
else
    # If `ARGRELAY_CONF_BASE_DIR` env var is not defined, use path to user home:
    argrelay_conf_base_dir=~"/.argrelay.conf.d/"

    # Path should be a directory or symlink to directory, otherwise default is `@/conf/`:
    if [[ ! -e "${argrelay_conf_base_dir}" ]]
    then
        argrelay_conf_base_dir="${argrelay_dir}/conf/"
    fi
fi

if [[ -e "${argrelay_conf_base_dir}" ]]
then
    if [[ ! -d "${argrelay_conf_base_dir}" ]]
    then
        echo "ERROR: (see FS_16_07_78_84.conf_dir_priority.md) path must be a dir or a symlink to dir: ${argrelay_conf_base_dir}" 1>&2
        "${ret_command}" 1
    fi
fi

deploy_files_procedure "${deploy_files_conf_path}" "detect_method" "${argrelay_conf_base_dir}" "do_not_override"

########################################################################################################################
# Prepare artifacts: deploy resources (symlinks).

deploy_files_conf_path="${argrelay_dir}/exe/deploy_resource_files_conf.bash"

if [[ ! -f "${deploy_files_conf_path}" ]]
then
    echo "ERROR: \`${deploy_files_conf_path}\` does not exists" 1>&2
    echo "It is required to know list of resources to be deployed." 1>&2
    echo "Provide \`${deploy_files_conf_path}\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'deploy_resource_files_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This resource file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_dev_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying resource files, format:
# module_name relative_dir_path resource_file_name
module_path_file_tuples=(
    argrelay custom_integ_res argrelay_common_lib.bash
    argrelay custom_integ_res argrelay_rc.bash
    argrelay custom_integ_res check_env.bash
    argrelay custom_integ_res dev_shell.bash
    argrelay custom_integ_res init_shell_env.bash
    argrelay custom_integ_res upgrade_all_packages.bash
)
########################################################################################################################
deploy_resource_files_conf_EOF
    "${ret_command}" 1
fi

deploy_files_procedure "${deploy_files_conf_path}" "symlink_method" "${argrelay_dir}/exe/" "override_target_file"

########################################################################################################################
# Prepare artifacts: generate resources.

# Generate `@/exe/run_argrelay_server`:
cat << PYTHON_SERVER_EOF > "${argrelay_dir}/exe/run_argrelay_server"
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/argrelay/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

import os

from argrelay import misc_helper_common

# FS_29_54_67_86 dir_structure: \`@/exe/run_argrelay_server\` -> \`@/\`:
misc_helper_common.set_argrelay_dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argrelay.relay_server.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_SERVER_EOF

# Generate `@/exe/run_argrelay_client`:
cat << PYTHON_CLIENT_EOF > "${argrelay_dir}/exe/run_argrelay_client"
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/argrelay/argrelay
# It is NOT supposed to be version-controlled per project as it:
# *   is generated
# *   differs per environment (due to different abs path to \`venv\`)
# It should rather be added to \`.gitignore\`.

import os

from argrelay import misc_helper_common

# FS_29_54_67_86 dir_structure: \`@/exe/run_argrelay_client\` -> \`@/\`:
misc_helper_common.set_argrelay_dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argrelay.relay_client.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_CLIENT_EOF

# Make both executable:
chmod u+x "${argrelay_dir}/exe/run_argrelay_client"
chmod u+x "${argrelay_dir}/exe/run_argrelay_server"

########################################################################################################################
# Generate source-able Bash config file and generate symlinks for command to be used with `argrelay`.

if [[ ! -f "${argrelay_dir}/conf/argrelay_rc_conf.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/conf/argrelay_rc_conf.bash\` does not exists" 1>&2
    echo "It is required to know which command names will have \`argrelay\` auto-completion." 1>&2
    echo "Provide \`${argrelay_dir}/conf/argrelay_rc_conf.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    cat << 'argelay_rc_conf_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

# Bash array of command names (names of symlinks to `@/exe/run_argrelay_client`):
# shellcheck disable=SC2034
argrelay_bind_command_basenames=(
    relay_demo
    some_command
    service_relay_demo
)
########################################################################################################################
argelay_rc_conf_EOF
    "${ret_command}" 1
fi

# Load user config for env vars:
# *   argrelay_bind_command_basenames
source "${argrelay_dir}/conf/argrelay_rc_conf.bash"

# shellcheck disable=SC2154
if [[ "${#argrelay_bind_command_basenames[@]}" -lt 1 ]]
then
    # At least one command should be listed in `argrelay_bind_command_basenames`:
    "${ret_command}" 1
fi

for argrelay_command_basename in "${argrelay_bind_command_basenames[@]}"
do
    # When symlinked `${argrelay_command_basename}` is executed,
    # its name is sent as the first arg (args[0])
    # which `argrelay` framework can use to look up and run any custom command line interpreter.

    symlink_path="${argrelay_dir}/bin/${argrelay_command_basename}"

    # Symlink `@/bin/${argrelay_command_basename}` command to `@/exe/run_argrelay_client`:
    if [[ -L "${symlink_path}" ]]
    then
        if [[ "$( readlink "${symlink_path}" )" != "../exe/run_argrelay_client" ]]
        then
            echo "WARN: symlink does not point to \`@/exe/run_argrelay_client\`: ${symlink_path}"
            ln -snf "../exe/run_argrelay_client" "${symlink_path}"
        fi
    else
        if [[ -e "${symlink_path}" ]]
        then
            echo "ERROR: symlink creation is obstructed by the existing path (review and remove): ${symlink_path}"
            exit 1
        else
            ln -sn "../exe/run_argrelay_client" "${symlink_path}"
        fi
    fi
done

########################################################################################################################
# Ensure (non-interactive) `@/exe/dev_shell.bash` starts and exits.

"${argrelay_dir}/exe/dev_shell.bash" "exit"

########################################################################################################################
# Build and test project.

if [[ ! -f "${argrelay_dir}/exe/build_project.bash" ]]
then
    echo "ERROR: \`${argrelay_dir}/exe/build_project.bash\` does not exists" 1>&2
    echo "It is required as custom build step for integration project, but can do nothing." 1>&2
    echo "Provide \`${argrelay_dir}/exe/build_project.bash\`, for example (copy and paste and modify):" 1>&2
    echo "" 1>&2
    # TODO: This matches content of default config stored in `argrelay` repo - try to deduplicate.
    cat << 'build_project_EOF'
########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the build scripts like this should build and test itself.

# It is fine to run tox on every start of FS_58_61_77_69 `dev_shell` because it is only used by `argrelay` devs:
# Build and test:
python -m tox
########################################################################################################################
build_project_EOF
    "${ret_command}" 1
fi

# Provide project-specific build script:
source "${argrelay_dir}/exe/build_project.bash"

########################################################################################################################
# Capture dependencies.

# Update `@/conf/dev_env_packages.txt` to know what was there at the time of bootstrapping:
cat << 'REQUIREMENTS_EOF' > "${argrelay_dir}/conf/dev_env_packages.txt"
###############################################################################
# Note that these dependencies are not necessarily required ones,
# those required are listed in `setup.py` script and can be installed as:
# pip install -e .
###############################################################################
REQUIREMENTS_EOF
# FS_85_33_46_53 bootstrap package management:
# Ignore `argrelay` itself (or anything installed in editable mode):
pip freeze --exclude-editable >> "${argrelay_dir}/conf/dev_env_packages.txt"

########################################################################################################################

eval "${bootstrap_dev_env_old_opts}"
unset bootstrap_dev_env_old_opts

########################################################################################################################
# EOF
########################################################################################################################
