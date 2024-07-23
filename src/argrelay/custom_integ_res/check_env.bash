#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

# FS_36_17_84_44: check_env script:
# This script:
# *   initially, runs basic checks in shell just to pass control to Python
# *   subsequently, for majority of checks, it runs checks implemented via plugins in Python
# All detected errors and info are reported on stdout.

# Debug: Print commands before execution:
#set -x
# Debug: Print commands after reading from a script:
#set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

########################################################################################################################

# Color scheme has to be synced with `python -m argrelay.check_env`:
success_color="\e[42m\e[30m"
warning_color="\e[43m\e[30m"
failure_color="\e[41m\e[97m"
field_color="\e[96m"
failure_message="\e[31m"
warning_message="\e[93m"
success_message="\e[92m"
reset_style="\e[0m"

# Indicate success|failure by color:
function color_failure_and_success_check_env {
    exit_code="${?}"
    if [[ "${exit_code}" == "0" ]]
    then
        # Only if this script is NOT sourced by another:
        if [[ "${0}" == "${BASH_SOURCE[0]}" ]]
        then
            echo -e "${success_color}SUCCESS:${reset_style} ${BASH_SOURCE[0]}" 1>&2
        fi
    else
        echo -e "${failure_color}FAILURE:${reset_style} ${BASH_SOURCE[0]}: exit_code: ${exit_code}" 1>&2
        exit "${exit_code}"
    fi
}

trap color_failure_and_success_check_env EXIT

########################################################################################################################

# This wrapper function is required to avoid `@/exe/bootstrap_env.bash` exiting this script
# (otherwise this script will miss the chance to provide detailed error description).
# The problem is that `return` command executed within boostrap are actually executed here -
# when wrapped into a func, `return` within bootstrap will exist just that func:
function activate_venv {
    # Bootstrap should be run from `argrelay_dir`:
    cd "${argrelay_dir}"
    # Run bootstrap to activate venv only:
    set +e
    source "${argrelay_dir}/exe/bootstrap_env.bash" activate_venv_only_flag
    exit_code="${?}"
    # Restore trap (overridden by bootstrap):
    trap color_failure_and_success_check_env EXIT
    set -e
    return "${exit_code}"
}

########################################################################################################################
# Report `script_dir`:
echo -e "${success_color}INFO:${reset_style} ${field_color}script_dir:${reset_style} ${script_dir}"

########################################################################################################################
# Report `argrelay_dir` by verifying that `argrelay_dir` contains `@/exe/bootstrap_env.bash`:
if [[ ! -f "${argrelay_dir}/exe/bootstrap_env.bash" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}argrelay_dir:${reset_style} ${failure_message}# \`argrelay_dir\` must have \`@/exe/bootstrap_env.bash\` script, but it is missing: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}argrelay_dir:${reset_style} ${argrelay_dir}"

########################################################################################################################
# Report `@/conf/` target:
if [[ -L "${argrelay_dir}/conf" ]]
then
    conf_target="$( readlink -- "${argrelay_dir}/conf" )"
    if [[ ! -d "${argrelay_dir}/${conf_target}" ]]
    then
        echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/conf:${reset_style} ${failure_message}# \`@/conf\` symlink target is not a directory: ${conf_target}${reset_style}"
        exit 1
    fi
elif [[ -d "${argrelay_dir}/conf" ]]
then
    conf_target="${argrelay_dir}/conf"
    echo -e "${warning_color}WARN:${reset_style} ${field_color}@/conf:${reset_style} ${warning_message}# \`@/conf\` is a directory (not a symlink to a directory): ${conf_target}${reset_style}"
    # Warn only - do not fail.
else
    conf_target="${argrelay_dir}/conf"
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/conf:${reset_style} ${failure_message}# \`@/conf\` does not lead to a directory: ${conf_target}${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}@/conf:${reset_style} ${conf_target} ${success_message}# \`@/conf\` symlink is a directory${reset_style}"

########################################################################################################################
# Report `venv_path`:
if ! activate_venv
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}venv_path:${reset_style} ${failure_message}# \`venv\` activation via \`@/exe/bootstrap_env.bash\` script failed - re-run bootstrap manually and inspect the reason why it fails via its extensive debug output: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}venv_path:${reset_style} ${VIRTUAL_ENV}"

########################################################################################################################
# Report `python_version`:
# shellcheck disable=SC2154 # `path_to_pythonX` is assigned by bootstrap:
curr_python_version="$( "${path_to_pythonX}" --version 2>&1 | sed 's/^[^[:digit:]]*\([^[:space:]]*\).*$/\1/g' )"
echo -e "${success_color}INFO:${reset_style} ${field_color}python_version:${reset_style} ${curr_python_version}"

########################################################################################################################
# Source it after ensuring that bootstrap was finished:
source "${argrelay_dir}/exe/argrelay_common_lib.bash"

########################################################################################################################
# TODO: Rename this to `argrelay_pip_version` and add `argrelay_module_version` which is obtained via Python part from internal module variable.
# Report `argrelay_version`:
set +e
argrelay_version="$( pip show argrelay | grep '^Version:' | cut -f2 -d' ' )"
exit_code="${?}"
set -e
if [[ "${exit_code}" != "0" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}argrelay_version:${reset_style} ${failure_message}# unable to detect version of \`argrelay\` package via \`pip show argrelay\`${reset_style}"
    exit 1
fi
# Check if `argrelay_version` string matches semver version format:
# https://stackoverflow.com/a/72900791/441652
# But semver version format is not compatible (conflicts) with - see: `docs/dev_notes/version_format.md`.
# Using simplified regex to see if version looks like version:
if [[ ! "${argrelay_version}" =~ ^[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+.*$ ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}argrelay_version:${reset_style} ${failure_message}# \`argrelay_version\` does not match version format: ${argrelay_version}${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}argrelay_version:${reset_style} ${argrelay_version}"

########################################################################################################################
# Switch to Python:
python -m argrelay.check_env "${argrelay_dir}" "${@}"
