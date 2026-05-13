#!/usr/bin/env zsh
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is just a wrapper to start a new shell with special config and stay in that shell.
# Implements FS_58_61_77_69 dev_shell.

# Set special env var used to restore shell options before passing control to next interactive shell:
if [[ -z "${ARGRELAY_USER_SHELL_OPTS+x}" ]]
then
    # Ensure use shell does not print anything to stdout.
    # Any output on stdout on shell init creates problems for many other commands (e.g. `ssh`).
    if [[ -n "$( TERM=dumb zsh -l -i -c "true" 2> /dev/null )" ]]
    then
        echo "ERROR: shell init generates stdout - redirect that output to stderr instead" 1>&2
        exit 1
    fi

    # See `@/exe/bootstrap_env.py` regarding `history`:
    # shellcheck disable=SC2034
    # shellcheck disable=SC2155
    export ARGRELAY_USER_SHELL_OPTS="$( unset ARGRELAY_DEBUG ; zsh -l -i -c "set +o" 2> /dev/null | grep "^set [+-]o" | grep -v "[[:space:]]history$" )"
fi

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

if [[ -n "${dev_shell_old_opts+x}" ]] ; then exit 1 ; fi

# Save `set`-able options to restore them at the end of this source-able script:
# https://unix.stackexchange.com/a/383581/23886
# See `@/exe/bootstrap_env.py` regarding `history`:
dev_shell_old_opts="$( set +o | grep -v "[[:space:]]history$" )"
case "${-}" in
    *e*) dev_shell_old_opts="${dev_shell_old_opts}; set -e" ;;
      *) dev_shell_old_opts="${dev_shell_old_opts}; set +e" ;;
esac

# Debug: Print commands before execution:
#set -x
# Debug: Print commands after reading from a script:
#set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Zsh uses `setopt ERR_RETURN` instead of Bash `set -E` to inherit trap on ERR by sub-shells:
setopt ERR_RETURN
# Error on undefined variables:
set -u

failure_color="\e[41m\e[97m"
reset_color="\e[0m"
banner_color="\e[95m"

# Indicate failure by color:
function color_failure_only {
    exit_code="${?}"
    if [[ "${exit_code}" != "0" ]]
    then
        echo -e "${failure_color}FAILURE:${reset_color} ${(%):-%N}: exit_code: ${exit_code}" 1>&2
        exit "${exit_code}"
    fi
}

trap color_failure_only EXIT

script_source="${(%):-%N}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

cd "${argrelay_dir}" || exit 1

# Let some code know that it runs under `@/exe/dev_shell.zsh` (e.g to run some tests conditionally):
ARGRELAY_DEV_SHELL="$( date +"%Y-%m-%dT%H:%M:%S%z" )"
export ARGRELAY_DEV_SHELL

# The new shell executes `@/exe/init_shell_env.zsh` script as its init file:
# Zsh does not have `--init-file`, but we can use `ZDOTDIR` to point to a temporary dir with `.zshrc`.
# Use `exec` to replace current process:
if [[ "$#" -eq "0" ]]
then
    # Interactive:
    echo -e "${banner_color}INFO: avoid starting nested \`@/exe/dev_shell.zsh\` on demand by \`source\`-ing this config in \`~/.zshrc\` by default: ${argrelay_dir}/exe/shell_env.zsh${reset_color}" 1>&2
    ZDOTDIR_TEMP="$( mktemp -d )"
    echo "source ~/.zshrc && source ${argrelay_dir}/exe/init_shell_env.zsh" > "${ZDOTDIR_TEMP}/.zshrc"
    ZDOTDIR="${ZDOTDIR_TEMP}" zsh
    rm -rf "${ZDOTDIR_TEMP}"
else
    # Non-interactive:
    # All args passed to `@/exe/dev_shell.zsh` are executed as command line:
    exec zsh -c "source ~/.zshrc && source ${argrelay_dir}/exe/init_shell_env.zsh && ( ${*} )"
fi
