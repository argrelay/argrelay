#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is just a wrapper to start a new shell with special config and stay in that shell.
# Implements FS_58_61_77_69 dev_shell.

# Set special env var used to restore shell options before passing control to next interactive shell:
if [[ -z "${ARGRELAY_USER_SHELL_OPTS+x}" ]]
then
    # Ensure use shell does not print anything to stdout.
    # Any output on stdout on shell init creates problems for many other commands (e.g. `ssh`).
    if [[ -n "$( bash -l -i -c "true" 2> /dev/null )" ]]
    then
        echo "ERROR: shell init generates stdout - redirect that output to stderr instead" 1>&2
        exit 1
    fi

    # See `@/exe/bootstrap_dev_env.bash` regarding `history`:
    # shellcheck disable=SC2034
    # shellcheck disable=SC2155
    export ARGRELAY_USER_SHELL_OPTS="$( unset ARGRELAY_DEBUG ; bash -l -i -c " set +o | grep -v \"[[:space:]]history$\" " 2> /dev/null )"
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
# See `@/exe/bootstrap_dev_env.bash` regarding `history`:
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
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

failure_color="\e[41m"
reset_color="\e[0m"
banner_color="\e[94m"

# Indicate failure by color:
function color_failure_only {
    exit_code="${?}"
    if [[ "${exit_code}" != "0" ]]
    then
        echo -e "${failure_color}FAILURE:${reset_color} ${BASH_SOURCE[0]}: exit_code: ${exit_code}" 1>&2
        exit "${exit_code}"
    fi
}

trap color_failure_only EXIT

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

cd "${argrelay_dir}" || exit 1

# Let some code know that it runs under `@/exe/dev_shell.bash` (e.g to run some tests conditionally):
ARGRELAY_DEV_SHELL="$(date)"
export ARGRELAY_DEV_SHELL

echo -e "${banner_color}INFO: keep starting nested \`@/exe/dev_shell.bash\` on demand or \`source\` this config by default in \`~/.bashrc\`: ${argrelay_dir}/exe/argrelay_rc.bash${reset_color}" 1>&2

# The new shell executes `@/exe/init_shell_env.bash` script as its init file:
# https://serverfault.com/questions/368054
# Use `exec` to replace current process:
if [[ "$#" -eq "0" ]]
then
    # Interactive:
    exec bash --init-file <( echo "source ~/.bashrc && source ${argrelay_dir}/exe/init_shell_env.bash" )
else
    # Non-interactive:
    # All args passed to `@/exe/dev_shell.bash` are executed as command line:
    exec bash --init-file <( echo "source ~/.bashrc && source ${argrelay_dir}/exe/init_shell_env.bash" ) -i -c "${*}"
fi

