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
# *   Bash-phase: initially, it runs basic checks in Bash to ensure sane environment for Python-phase
# *   Python-phase: subsequently, it passes control to Python for majority of checks implemented as plugins
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
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}venv_path:${reset_style} ${failure_message}# \`venv\` activation via \`@/exe/bootstrap_env.bash\` script failed - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}venv_path:${reset_style} ${VIRTUAL_ENV}"

########################################################################################################################
# Report whether `PYTHON_PATH` is set:
if [[ -n "${PYTHON_PATH+x}" ]]
then
    echo -e "${warning_color}WARN:${reset_style} ${field_color}PYTHON_PATH:${reset_style} ${PYTHON_PATH} ${warning_message}# \`PYTHON_PATH\` is set which may load modules outside of \`venv\` - to avoid issues make sure it is intentional.${reset_style}"
else
    echo -e "${success_color}INFO:${reset_style} ${field_color}PYTHON_PATH:${reset_style} ${success_message}# \`PYTHON_PATH\` is not set = no overrides for \`venv\` modules (good).${reset_style}"
fi

########################################################################################################################
# Report `python_version`:
# shellcheck disable=SC2154 # `path_to_pythonX` is assigned by bootstrap:
curr_python_version="$( "${path_to_pythonX}" --version 2>&1 | sed 's/^[^[:digit:]]*\([^[:space:]]*\).*$/\1/g' )"
echo -e "${success_color}INFO:${reset_style} ${field_color}python_version:${reset_style} ${curr_python_version}"

########################################################################################################################
# Report `is_pip_installed`:
if ( python -m pip --version 1> /dev/null )
then
    echo -e "${success_color}INFO:${reset_style} ${field_color}is_pip_installed:${reset_style} True ${success_message}# Module \`pip\` is present."
else
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}is_pip_installed:${reset_style} False ${failure_message}# Module \`pip\` is missing - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi

########################################################################################################################
# Report `argrelay_pip_version`:
set +e
argrelay_pip_version="$( pip show argrelay | grep '^Version:' | cut -f2 -d' ' )"
exit_code="${?}"
set -e
if [[ "${exit_code}" != "0" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}argrelay_pip_version:${reset_style} ${failure_message}# Unable to detect version of \`argrelay\` package via \`pip show argrelay\` - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi
# Check if `argrelay_pip_version` string matches semver version format:
# https://stackoverflow.com/a/72900791/441652
# But semver version format is not compatible (conflicts) with - see: `docs/dev_notes/version_format.md`.
# Using simplified regex to see if version looks like version:
if [[ ! "${argrelay_pip_version}" =~ ^[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+.*$ ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}argrelay_pip_version:${reset_style} ${failure_message}# \`argrelay_pip_version\` does not match version format: ${argrelay_pip_version}${reset_style}"
    exit 1
fi
echo -e "${success_color}INFO:${reset_style} ${field_color}argrelay_pip_version:${reset_style} ${argrelay_pip_version}"

########################################################################################################################
# Check `@/exe/argrelay_common_lib.bash` is a symlink-ed script
# which partially ensures bootstrap has already been run
# (in other words, `argrelay` was not simply installed via `pip`):
if [[ -L "${argrelay_dir}/exe/argrelay_common_lib.bash" ]]
then
    symlink_target="$( readlink -- "${argrelay_dir}/exe/argrelay_common_lib.bash" )"
    if [[ ! -f "${symlink_target}" ]]
    then
        echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/exe/argrelay_common_lib.bash:${reset_style} ${symlink_target} ${failure_message}# Symlink target is not a file${reset_style}"
        exit 1
    fi
    if [[ "${symlink_target}" != "${VIRTUAL_ENV}"* ]]
    then
        echo -e "${warning_color}WARN:${reset_style} ${field_color}@/exe/argrelay_common_lib.bash:${reset_style} ${symlink_target} ${warning_message}# Symlink target is outside \`venv\` => is \`argrelay\` installed in editable mode?${reset_style}"
        # Warn only - do not fail.
    else
        echo -e "${success_color}INFO:${reset_style} ${field_color}@/exe/argrelay_common_lib.bash:${reset_style} ${symlink_target} ${success_message}# Symlink target is inside \`venv\`${reset_style}"
    fi
else
    if [[ -e "${argrelay_dir}/exe/argrelay_common_lib.bash" ]]
    then
        echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/exe/argrelay_common_lib.bash:${reset_style} ${argrelay_dir}/exe/argrelay_common_lib.bash ${failure_message}# Not a symlink - remove manually and re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
        exit 1
    else
        echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/exe/argrelay_common_lib.bash:${reset_style} ${argrelay_dir}/exe/argrelay_common_lib.bash ${failure_message}# Does not exist - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
        exit 1
    fi
fi

source "${argrelay_dir}/exe/argrelay_common_lib.bash"

########################################################################################################################
# Run all `check_env_plugin.*`:

if [[ ! -e "${argrelay_dir}/conf/check_env_plugin.conf.bash" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/conf/check_env_plugin.conf.bash:${reset_style} ${argrelay_dir}/conf/check_env_plugin.conf.bash ${failure_message}# Does not exist - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi

source "${argrelay_dir}/conf/check_env_plugin.conf.bash"

########################################################################################################################
# Ensure config for Python `check_env` is present:

if [[ ! -e "${argrelay_dir}/conf/check_env_plugin.conf.yaml" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}@/conf/check_env_plugin.conf.yaml:${reset_style} ${argrelay_dir}/conf/check_env_plugin.conf.yaml ${failure_message}# Does not exist - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi

########################################################################################################################
# Start `check_env` in `dry_run` mode (e.g. ensure no config schema mismatch):

set +e
python -m argrelay.check_env "${argrelay_dir}" "dry_run"
exit_code="${?}"
set -e
if [[ "${exit_code}" != "0" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}check_env_python:${reset_style} ${failure_message}# Unable to run Python \`check_env\` in \`dry_run\` mode - re-try after re-running \`@/exe/bootstrap_env.bash\`: ${argrelay_dir}/exe/bootstrap_env.bash${reset_style}"
    exit 1
fi

########################################################################################################################
# Run checks in Python:

python -m argrelay.check_env "${argrelay_dir}" "${@}"
