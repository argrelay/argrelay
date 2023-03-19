#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This script is NOT supposed to be run or sourced directly.
# Instead, run `dev_shell.bash`.

# The steps this script implements FS_58_61_77_69 dev_shell:
# *   Runs `bootstrap_outside_venv.bash` to set up Python and artifacts.
# *   Runs `argrelay_rc.bash` to configure auto-completion for this shell session.

# Note that enabling exit on error (like `set -e` below) will exit parent
# `dev_shell.bash` script (as this one is sourced) - that is intentional.

# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Error on undefined variables:
set -u
# Debug: Print commands after reading from a script:
#set -v
# Debug: Print commands before execution:
#set -x

# This is why the script has to be symlinked to the project dir:
./init_python.bash

# Activate pre-configured Python `venv`:
source ./python_conf.bash
# shellcheck disable=SC2154
source "${path_to_venvX}"/bin/activate
# Ensure refs to `argrelay` work when `dev_shell.bash` starts with empty `venv`:
pip install argrelay

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

# Note that this is often redundant, but ensures `dev_shell.bash` session re-deploys anything missing:
"${argrelay_path}"/custom_integ_res/bootstrap_outside_venv.bash

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
set +o pipefail
set +e
set +u
set +v
set +x

