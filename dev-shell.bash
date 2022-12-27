
# Setup dev env.
# This is just a wrapper to start new shell and stay there.

# Return first non-zero exit code from commands in a pipeline:
#set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Error on undefined variables:
set -u
# Debug: Print commands after reading from a script:
#set -v
# Debug: Print commands before execution:
#set -x

# Switch to dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1

# The new shell executes `dev-init.bash` script interactively as its init file:
# https://serverfault.com/questions/368054
bash --init-file <(echo "source ~/.bashrc && source ./dev-init.bash")
