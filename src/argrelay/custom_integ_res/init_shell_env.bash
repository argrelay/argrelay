#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This script is NOT supposed to be run or sourced directly.
# Instead, run `@/exe/dev_shell.bash`.

# The steps this script implements FS_58_61_77_69 dev_shell:
# *   Runs `@/exe/bootstrap_dev_env.bash` to activate Python `venv`.
# *   Runs `@/exe/argrelay_rc.bash` to configure auto-completion for this shell session.

# Note that enabling exit on error (like `set -e` below) will exit parent
# `@/exe/dev_shell.bash` script (as this one is sourced) - that is intentional.

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

if [[ -n "${init_shell_env_old_opts+x}" ]] ; then exit 1 ; fi

# Save `set`-able options to restore them at the end of this source-able script:
# https://unix.stackexchange.com/a/383581/23886
# See `@/exe/bootstrap_dev_env.bash` regarding `history`:
init_shell_env_old_opts="$( set +o | grep -v "[[:space:]]history$" )"
case "${-}" in
    *e*) init_shell_env_old_opts="${init_shell_env_old_opts}; set -e" ;;
      *) init_shell_env_old_opts="${init_shell_env_old_opts}; set +e" ;;
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

reset_color="\e[0m"
delimiter_color="\e[91m"
field_color="\e[96m"

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

# It is expected that `@/exe/dev_shell.bash` switches to the target project dir itself (not this script).

# FS_85_33_46_53: a copy of script `@/exe/bootstrap_dev_env.bash` has to be stored within the project
# as the creator of everything:
source "${argrelay_dir}/exe/bootstrap_dev_env.bash" activate_venv_only_flag

# Collect info about `@/conf/`:
if [[ -L "${argrelay_dir}/conf" ]]
then
    conf_status="$( readlink -- "${argrelay_dir}/conf" )"
    if [[ ! -d "${argrelay_dir}/conf" ]]
    then
        conf_status="[error]"
    fi
elif [[ -d "${argrelay_dir}/conf" ]]
then
    conf_status="[dir]"
else
    conf_status="[error]"
fi

# Source extra config:
if [[ -f "${argrelay_dir}/conf/dev_shell_rc.conf.bash" ]]
then
    source "${argrelay_dir}/conf/dev_shell_rc.conf.bash"
fi

# Enable auto-completion:
source "${argrelay_dir}/exe/argrelay_rc.bash"

# TODO: FS_16_07_78_84: respect conf dir priority:
server_host_name="$( jq --raw-output ".connection_config.server_host_name" "${argrelay_dir}/conf/argrelay_client.json" )"
server_port_number="$( jq --raw-output ".connection_config.server_port_number" "${argrelay_dir}/conf/argrelay_client.json" )"

eval "${init_shell_env_old_opts}"
unset init_shell_env_old_opts

# This env var is set by the script which sources this one:
# shellcheck disable=SC2154
eval "${ARGRELAY_USER_SHELL_OPTS}"

# This is a basic info normally reported by FS_36_17_84_44 `check_env` script:
echo -e "\
${field_color}nested shell level:${reset_color} ${SHLVL} ${delimiter_color}|${reset_color} \
${field_color}argrelay:${reset_color} $( pip show argrelay | grep '^Version:' | cut -f2 -d' ' || true ) ${delimiter_color}|${reset_color} \
${field_color}@/conf:${reset_color} ${conf_status} ${delimiter_color}|${reset_color} \
${field_color}venv:${reset_color} ${VIRTUAL_ENV} ${delimiter_color}|${reset_color} \
${field_color}server:${reset_color} http://${server_host_name}:${server_port_number}" \
1>&2
