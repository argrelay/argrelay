#!/usr/bin/env bash

# This script configures demo client and starts demo server.

# TODO:
# *    Configure to stop background process on hup.
# *    When inside non-interactive `dev_shell.bash`, run Python `server_control` scripts (redirect output to demo_server.log):
#      *    Standard check: if port is open, fail.
#      *    Standard check: if PID file is locked, fail.
#      *    Start server.
#      *    Standard check: ensure PID file is locked, otherwise, fail.
#      *    Wait for open port.
# *    When server is started, run another `dev_shell.bash` interactively.

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

# Use bootstrap to set `@/conf/` to `@/dst/relay_demo`:
cd "${argrelay_dir}" || exit 1
"${argrelay_dir}/exe/bootstrap_dev_env.bash" "dst/relay_demo"

"${argrelay_dir}/exe/dev_shell.bash" "${@}"
