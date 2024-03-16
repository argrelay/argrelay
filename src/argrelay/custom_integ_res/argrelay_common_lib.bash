#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

# This script is supposed to be sourced by others, not run directly:
[[ "${BASH_SOURCE[0]}" == "${0}" ]] && exit 1

# This library script expects caller script (the sourcing script) to ensure few things:
# *   `script_source` should be set as:
#     script_source="${BASH_SOURCE[0]}"
#     by the caller.
#     The lib script cannot know the depth sourced at - it does not know which index (0, or 1, ...)
#     to use against `BASH_SOURCE` array, but for the top-level caller it is always 0.
# *   `script_dir` should be set to absolute script dirname:
#     https://stackoverflow.com/a/246128/441652
#     script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
#     by the caller before it changed dir anywhere.
#     This is the way to ensure the dir where the caller script resides.
# *   `argrelay_dir` should be set the `@/` (see FS_29_54_67_86) by the caller
#     because only the caller knew its relative path to the `argrelay_dir`
#     (that is the way to find location of this source this lib script).

# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
function derive_argrelay_dir_relative_to {

    # Must be prefixed with "@/":
    local prefixed_script_rel_path="${1}"
    test "${prefixed_script_rel_path:0:2}" == "@/"

    local script_rel_path="${prefixed_script_rel_path:2}"

    # Remove `script_rel_path` from `script_source`:
    # https://stackoverflow.com/a/16623897/441652
    # shellcheck disable=SC2034
    # shellcheck disable=SC2154
    local argrelay_dir="${script_source%"${script_rel_path}"}"
}

function print_ISO_timestamp_UTC {
    date -u +"%Y-%m-%dT%H:%M:%S.%3NZ"
}

function log_on_stderr {
    log_level="${1}"
    log_message="${2}"
    log_timestamp="$( print_ISO_timestamp_UTC )"
    echo "${log_timestamp}: ${log_level}: ${log_message}" 1>&2
}

function ensure_inside_dev_shell {
    # Ensure the script was started in `@/exe/dev_shell.bash`:
    if [[ -z "${ARGRELAY_DEV_SHELL:-}" ]]
    then
        echo "ERROR: Run this script under \`@/exe/dev_shell.bash\`." 1>&2
        exit 1
    fi

    # Ensure it is a `venv` (`@/exe/dev_shell.bash` activates `venv` configured in `@/conf/python_conf.bash`):
    test -n "${VIRTUAL_ENV}"

    # Ensure `@/conf` is already in place:
    test -d "${argrelay_dir}/conf"
}

function remove_pid_file_if_stale {
    # Use case (FS_86_73_43_45): clean up stale pid file.

    pid_file="${1}"

    if [[ -f "${pid_file}" ]]
    then
        pid_value="$( cat "${pid_file}" )"
        if [[ -d "/proc/${pid_value}" ]]
        then
            log_on_stderr "INFO" "pid [${pid_value}] has a running process, leaving pid file [${pid_file}]"
        else
            log_on_stderr "INFO" "pid [${pid_value}] does not have running process, removing pid file [${pid_file}]"
            rm "${pid_file}"
        fi
    fi
}

function kill_via_pid_file_or_ensure_closed_port {
    # Use case (FS_86_73_43_45): trigger server shut down if pid file exists or ensure server is down otherwise.
    # Unlike `wait_for_closed_port`, this func does not wait for port to close.
    # It only ensures port is closed when there is no pid file.

    pid_file="${1}"
    server_host_name="${2}"
    server_port_number="${3}"

    if [[ -f "${pid_file}" ]]
    then
        pid_value="$( cat "${pid_file}" )"
        if [[ -d "/proc/${pid_value}" ]]
        then
            log_on_stderr "INFO" "pid [${pid_value}] has a running process, stopping it, removing pid file [${pid_file}]"
            kill "${pid_value}"
            rm "${pid_file}"
        else
            log_on_stderr "WARN" "pid [${pid_value}] does not have a running process, doing nothing, removing pid file [${pid_file}]"
            rm "${pid_file}"
        fi
    else
        set +e
        # Note that it is only assumed that the right server runs on that port
        # (no easy way to 100% ensure it is not something else):
        nc -z "${server_host_name}" "${server_port_number}"
        exit_code="${?}"
        set -e

        if [[ "${exit_code}" == "0" ]]
        then
            log_on_stderr "ERROR" "port [${server_port_number}] is open, stop that server without pid file manually"
            exit 1
        else
            log_on_stderr "INFO" "port [${server_port_number}] is closed, as expected with missing pid file"
        fi
    fi
}

function exit_if_port_open {
    # Use case (FS_86_73_43_45): do nothing if server is up (exit current process).

    server_host_name="${1}"
    server_port_number="${2}"

    set +e
    # Note that it is only assumed that the right server runs on that port
    # (no way to 100% ensure it is not something else):
    nc -z "${server_host_name}" "${server_port_number}"
    exit_code="${?}"
    set -e

    if [[ "${exit_code}" == "0" ]]
    then
        log_on_stderr "INFO" "port [${server_port_number}] is open, no need to start server"
        exit 0
    else
        log_on_stderr "INFO" "port [${server_port_number}] is closed, need to start server"
    fi
}

function wait_for_open_port {
    # Use case (FS_86_73_43_45): ensure server is up before return.

    timeout_sec="${1}"
    pid_file="${2}"
    server_host_name="${3}"
    server_port_number="${4}"

    end_time_sec="$(( $( date "+%s" ) + ${timeout_sec} ))"

    # Wait until server has opened its port:
    while ! nc -z "${server_host_name}" "${server_port_number}"
    do
        # Check if PID still exists:
        pid_value="$( cat "${pid_file}" )"
        if [[ ! -d "/proc/${pid_value}" ]]
        then
            log_on_stderr "ERROR" "pid [${pid_value}] from pid file [${pid_file}] does not exists anymore"
            exit 1
        fi

        if [[ "${end_time_sec}" -lt "$( date "+%s" )" ]]
        then
            log_on_stderr "ERROR" "timeout"
            exit 1
        fi

        log_on_stderr "INFO" "waiting for open port ${server_host_name}:${server_port_number}"
        sleep 5
    done

    log_on_stderr "INFO" "port is open now: ${server_host_name}:${server_port_number}"
}

function wait_for_closed_port {
    # Use case  (FS_86_73_43_45): ensure server is down before return.
    # Unlike `kill_via_pid_file_or_ensure_closed_port`, this func does not trigger server shut down.

    timeout_sec="${1}"
    server_host_name="${2}"
    server_port_number="${3}"

    end_time_sec="$(( $( date "+%s" ) + ${timeout_sec} ))"

    # Wait until server has closed its port:
    while nc -z "${server_host_name}" "${server_port_number}"
    do
        if [[ "${end_time_sec}" -lt "$( date "+%s" )" ]]
        then
            log_on_stderr "ERROR" "timeout"
            exit 1
        fi
        log_on_stderr "INFO" "waiting for closed port ${server_host_name}:${server_port_number}"
        sleep 5
    done

    log_on_stderr "INFO" "port is closed now: ${server_host_name}:${server_port_number}"
}
