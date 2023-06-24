#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This script is NOT supposed to be run or sourced directly.
# Instead, run `@/exe/dev_shell.bash`.

# The steps this script implements FS_58_61_77_69 dev_shell:
# *   Runs `@/exe/bootstrap_dev_env.bash` to set up Python and artifacts.
# *   Runs `@/exe/argrelay_rc.bash` to configure auto-completion for this shell session.

# Note that enabling exit on error (like `set -e` below) will exit parent
# `@/exe/dev_shell.bash` script (as this one is sourced) - that is intentional.

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

# It is expected that `@/exe/dev_shell.bash` switches to the target project dir itself (not this script).

# FS_85_33_46_53: a copy of script `@/exe/bootstrap_dev_env.bash` has to be stored within the project
# as the creator of everything:
source "${argrelay_dir}/exe/bootstrap_dev_env.bash" activate_venv_only_flag

# Enable auto-completion:
source "${argrelay_dir}/exe/argrelay_rc.bash"

# Show commands configured for auto-completion:
# shellcheck disable=SC2154
for argrelay_command_basename in "${argrelay_bind_command_basenames[@]}"
do
    complete -p "${argrelay_command_basename}"
done

# Disable exit on errors and any extra debug info for interactive shell
# (see enabling them for the duration of this script above):
set +u
set +E
set +e
set +o pipefail
set +v
set +x
