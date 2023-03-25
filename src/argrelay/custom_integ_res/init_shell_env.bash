#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script is NOT supposed to be run or sourced directly.
# Instead, run `dev_shell.bash`.

# The steps this script implements FS_58_61_77_69 dev_shell:
# *   Runs `bootstrap_outside_venv.bash` to set up Python and artifacts.
# *   Runs `argrelay_rc.bash` to configure auto-completion for this shell session.

# Note that enabling exit on error (like `set -e` below) will exit parent
# `dev_shell.bash` script (as this one is sourced) - that is intentional.

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

# The dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# It is expected that `dev_shell.bash` switches to the target project dir itself (not this script).

# This is why `bootstrap_venv.bash` script has to be part of the project dir:
./bootstrap_venv.bash

# Enable auto-completion:
source ./argrelay_rc.bash

# Show commands configured for auto-completion:
# shellcheck disable=SC2154
for argrelay_command_name in "${argrelay_bind_commands[@]}"
do
    complete -p "${argrelay_command_name}"
done

# Disable exit on errors and any extra debug info for interactive shell
# (see enabling them for the duration of this script above):
set +u
set +E
set +e
set +o pipefail
set +v
set +x
