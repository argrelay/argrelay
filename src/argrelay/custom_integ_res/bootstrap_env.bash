#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This script should ALWAYS be called with current dir = project dir `@/` (see `argrelay_dir` below).

# This script is a thin shim:
# *   When `source`-ed with `activate_venv_only_flag`: activates Python `venv` in the caller's shell.
# *   When executed directly: delegates to `@/exe/bootstrap_env.py` for full bootstrap.

# FS_59_19_34_39.supported_shell.md:
# Shell compatibility shim - must run before any Bash/Zsh-specific code:
if [[ -n "${BASH_SOURCE+x}" ]]; then
    _current_script="${BASH_SOURCE[0]}"
    [[ "${0}" != "${BASH_SOURCE[0]}" ]] && _is_sourced="true" || _is_sourced="false"
    _errtrace_opt="set -E"
else
    # Zsh
    _current_script="${(%):-%x}"
    [[ "${ZSH_EVAL_CONTEXT}" == *:file* ]] && _is_sourced="true" || _is_sourced="false"
    _errtrace_opt="setopt ERR_RETURN"
fi

# TODO: TODO_11_66_62_70: python_bootstrap: SKIP:
#       `bash`-specific.

if [[ -n "${bootstrap_env_old_opts+x}" ]] ; then exit 1 ; fi

# Save `set`-able options to restore them at the end of this source-able script:
# https://unix.stackexchange.com/a/383581/23886
# Not saving history because:
# *   it is not modified within `argrelay` scripts
# *   it should not be restored in non-interactive files (disabled by default)
bootstrap_env_old_opts="$( set +o | grep -v "[[:space:]]history$" )"
case "${-}" in
    *e*) bootstrap_env_old_opts="${bootstrap_env_old_opts}; set -e" ;;
      *) bootstrap_env_old_opts="${bootstrap_env_old_opts}; set +e" ;;
esac

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: SKIP:
#       `bash`-specific.

# Keep output-related `set`-able options same when this script is sourced
# (otherwise, full debug output for bootstrap is adequate as it runs in hardly predictable target environment):
if [[ "${_is_sourced}" != "true" ]] ; then

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v

fi

# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells (Bash: set -E; Zsh: setopt ERR_RETURN):
eval "${_errtrace_opt}"
# Error on undefined variables:
set -u

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: SKIP:
#       `bash`-specific.

is_script_sourced="${_is_sourced}"

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: SKIP:
#       `bash`-specific.

# Bash does not allow `return` if the script is not sourced (`exit` must be used):
# https://stackoverflow.com/a/49857550/441652
if [[ "${is_script_sourced}" == "true" ]]
then
    ret_command="return"
else
    ret_command="exit"
fi

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: DONE:
#       Support color on success/failure.

success_color="\e[42m\e[30m"
failure_color="\e[41m\e[97m"
reset_color="\e[0m"

# Indicate success|failure by color:
function color_failure_and_success_bootstrap_env {
    exit_code="${?}"
    if [[ "${exit_code}" == "0" ]]
    then
        # Only if this script is NOT sourced by another:
        if [[ "${_is_sourced}" != "true" ]]
        then
            echo -e "${success_color}SUCCESS:${reset_color} ${_current_script}" 1>&2
        fi
    else
        echo -e "${failure_color}FAILURE:${reset_color} ${_current_script}: exit_code: ${exit_code}" 1>&2
        "${ret_command}" "${exit_code}"
    fi
}

trap color_failure_and_success_bootstrap_env EXIT

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: SKIP:
#       `bash`-specific.

script_source="${_current_script}"
# shellcheck disable=SC2034
script_name="$( basename -- "${script_source}" )"
# The dir of this script:
# shellcheck disable=SC2034
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# Note: In case of `bootstrap_env.bash`, `argrelay_dir` is not `script_dir`, but always the current directory
# (it is supposed to be started from the dir where project is being set up).
# FS_29_54_67_86 dir_structure: current dir = `@/`:
argrelay_dir="$( realpath "$( dirname "." )" )"

# Ensure it is called from project root (which should contain `@/exe/` dir):
test -d "${argrelay_dir}/exe/"

########################################################################################################################

# TODO: TODO_11_66_62_70: python_bootstrap: DONE:
#       Use `argparse` instead.

# Collect flags from command line args:
activate_venv_only_flag=""
passthrough_args=()
for arg_i in "${@}"
do

    if [[ "${arg_i}" == "activate_venv_only_flag" ]]
    then
        # Used by `@/exe/dev_shell.bash` (by `@/exe/init_shell_env.bash`)
        # to activate Python venv only:
        activate_venv_only_flag="activate_venv_only_flag"
        continue
    fi

    passthrough_args+=( "${arg_i}" )
done

########################################################################################################################

# Compatibility hack to translate:
# *   from `bootstrap_env.bash path/to/env/dir`
# *   into `bootstrap_env.py --env path/to/env/dir`

# Select the first arg that specifies existing directory and use it for `--env` arg to `bootstrap_env.py`
selected_env_path=""
remaining_args=()
for arg_i in "${passthrough_args[@]+"${passthrough_args[@]}"}"
do
    if [[ -z "${selected_env_path}" ]] && [[ -d "${arg_i}" ]]
    then
        selected_env_path="${arg_i}"
    else
        remaining_args+=( "${arg_i}" )
    fi
done
passthrough_args=( "${remaining_args[@]+"${remaining_args[@]}"}" )

########################################################################################################################

if [[ -n "${activate_venv_only_flag}" ]]
then
    # Query venv path from `@/exe/bootstrap_env.py` (reads config, no venv needed):
    # Pass current @/conf symlink target as --env to avoid mismatch assertion when conf != default env:
    _eval_env_args=()
    if [[ -L "${argrelay_dir}/conf" ]]
    then
        # TODO: TODO_11_66_62_70.python_bootstrap.md
        #       protoprimer: HACK: untils TODO_41_10_50_01.implement_env_selector.md implemented:
        #       There should not be arg "dst/.github".
        #       Instead, `bootstrap_env.py` should select "dst/.github" automatically:
        _eval_env_args=( "--env" "$( readlink "${argrelay_dir}/conf" )" )
    fi
    path_to_venvX="$( "${argrelay_dir}/exe/bootstrap_env.py" eval "${_eval_env_args[@]+"${_eval_env_args[@]}"}" | jq -r '.leap_derived.state_local_venv_dir_abs_path_inited // empty' )"
    unset _eval_env_args
    source "${path_to_venvX}/bin/activate"
    eval "${bootstrap_env_old_opts}"
    unset bootstrap_env_old_opts
    "${ret_command}" 0
fi

########################################################################################################################

eval "${bootstrap_env_old_opts}"
unset bootstrap_env_old_opts

# Safe array expansion idiom (survives `set -u` with empty array):
if [[ -n "${selected_env_path}" ]]
then
    "${argrelay_dir}/exe/bootstrap_env.py" -vvv --env "${selected_env_path}" "${passthrough_args[@]+"${passthrough_args[@]}"}"
else
    "${argrelay_dir}/exe/bootstrap_env.py" -vvv "${passthrough_args[@]+"${passthrough_args[@]}"}"
fi

########################################################################################################################
# EOF
########################################################################################################################
