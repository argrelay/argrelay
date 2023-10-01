#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is just a wrapper to start a new shell with special config and stay in that shell.
# Implements FS_58_61_77_69 dev_shell.

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

failure_color="\e[41m"
reset_color="\e[0m"

# Indicate failure by color:
function on_exit {
    exit_code="${?}"
    if [[ "${exit_code}" != "0" ]]
    then
        echo -e "${failure_color}FAILURE:${reset_color} ${BASH_SOURCE[0]}: exit_code: ${exit_code}" 1>&2
        exit "${exit_code}"
    fi
}

trap on_exit EXIT

# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

cd "${argrelay_dir}" || exit 1

# Let some code know that it runs under `@/exe/dev_shell.bash` (e.g to run some tests conditionally):
ARGRELAY_DEV_SHELL="$(date)"
export ARGRELAY_DEV_SHELL

# The new shell executes `@/exe/init_shell_env.bash` script as its init file:
# https://serverfault.com/questions/368054
if [[ "$#" -eq "0" ]]
then
    # Interactive:
    bash --init-file <(echo "source ~/.bashrc && source ${argrelay_dir}/exe/init_shell_env.bash")
else
    # Non-interactive:
    # All args passed to `@/exe/dev_shell.bash` are executed as command line:
    bash --init-file <(echo "source ~/.bashrc && source ${argrelay_dir}/exe/init_shell_env.bash") -i -c "${*}"
fi

