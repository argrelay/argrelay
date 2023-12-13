#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# FS_36_17_84_44: check script: TODO: draft:
exit 0

# This script shows details about online servers
# configured via `@/conf/argrelay.client.json` (from client point of view).
# Server might not be local, but client always is.

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

# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"
source "${argrelay_dir}/exe/argrelay_common_defs.bash"

server_host_name="$( jq --raw-output ".connection_config.server_host_name" "${argrelay_dir}/conf/argrelay.client.json" )"
server_port_number="$( jq --raw-output ".connection_config.server_port_number" "${argrelay_dir}/conf/argrelay.client.json" )"

# TODO: Connect to server to get:
#       server instance id (UUID),
#       argrelay framework server version,
#       server start time,
#       server setup version,
#       server setup commit id,
#       etc.

# TODO: Check if server is local.
#       Do not check via hostname.
#       Simply check netstat against port number to select pid.
#       Check if pid file exists.
#       Check if pid in pid file matches pid from netstat.
#       Verify if localhost:server_port_number succeeds with the same server instance id.

# TODO: additionally:
#       show latest server log.
