#!/usr/bin/env bash

# This script configures demo client and starts demo server.
#
# It can be the first script run after repo clone and
# should assume nothing has been bootstrapped
# (until after it does it by itself).

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

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
script_name="$( basename -- "${script_source}" )"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"
pid_file="${argrelay_dir}/var/${script_name}.pid"
log_file="${argrelay_dir}/logs/${script_name}.log"

# Use bootstrap to set `@/conf/` to `@/dst/relay_demo`:
cd "${argrelay_dir}" || exit 1
"${argrelay_dir}/exe/bootstrap_dev_env.bash" "dst/relay_demo"

# Bootstrap finished, now we can source the lib:
source "${argrelay_dir}/exe/argrelay_common_lib.bash"

remove_pid_file_if_stale "${pid_file}"

# NOTE: `server_host_name` is supposed to be local for this script to make sense:
server_host_name="$( jq --raw-output ".connection_config.server_host_name" "${argrelay_dir}/conf/argrelay.client.json" )"
server_port_number="$( jq --raw-output ".connection_config.server_port_number" "${argrelay_dir}/conf/argrelay.client.json" )"

kill_via_pid_file_or_ensure_closed_port "${pid_file}" "${server_host_name}" "${server_port_number}"
# Wait for 1 min (60 sec):
wait_for_closed_port 60 "${server_host_name}" "${server_port_number}"

function shutdown_jobs {
    saved_exit_code="${?}"
    kill_via_pid_file_or_ensure_closed_port "${pid_file}" "${server_host_name}" "${server_port_number}" && true
    # Wait for 1 min (60 sec):
    wait_for_closed_port 60 "${server_host_name}" "${server_port_number}" && true
    remaining_processes="$( jobs -p )"
    if [[ -n "$( jobs -p )" ]]
    then
        echo "WARN: remaining background processes: ${remaining_processes}" 1>&2 && true
    fi
    # Restore `saved_exit_code`:
    ( exit "${saved_exit_code:-0}" )
}

function combined_on_exit_trap {
    shutdown_jobs
    color_failure_only
}

trap combined_on_exit_trap EXIT

"${argrelay_dir}/bin/run_argrelay_server" 1>> "${log_file}" 2>&1 &
echo $! > "${pid_file}"

# Wait for 1 min (60 sec):
wait_for_open_port 60 "${pid_file}" "${server_host_name}" "${server_port_number}"

"${argrelay_dir}/exe/dev_shell.bash" "${@}"
