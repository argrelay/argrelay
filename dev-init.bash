#!/usr/bin/env bash

# This script is not supposed to be run or sourced directly.
# Instead, run `dev-shell.bash`.

# The steps this script performs:
# * Set up python `venv/relay_demo`.
# * Build `argrelay`.
# * Install `argrelay` in editable mode.
# * Configure Bash auto-completion for command name `relay_demo` .
#   The binding is temporarily (while `dev-shell.bash` is running).
#   This step is what normally goes to `~/.bashrc` to make Bash auto-completion permanent.

# Return first non-zero exit code from commands in a pipeline:
set -o pipefail
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

# Guard against direct execution (when it is sourced from `dev-shell.bash` as init file, arg[0] is "bash"):
if [[ "$( basename "$0" )" != "bash" ]]
then
    echo "ERROR: script \`dev-init.bash\` is not run directly, instead, run \`dev-shell.bash\`" 1>&2
    return 1
fi

# TODO: update if needed - better move into separate small source-able file (ignored by git):
pythonX="python3.7"
# TODO: update if needed - better move into separate small source-able file (ignored by git):
path_to_pythonX="/path/to/another/${pythonX}/here"
if [[ -d "${path_to_pythonX}" ]]
then
    export PATH="${path_to_pythonX}:${PATH}"
fi

# Test python:
which "${pythonX}"
if ! "${pythonX}" -c 'print("'"${pythonX}"' works")'
then
    echo "ERROR: ${pythonX} command is not available in PATH - modify this script to fix it" 1>&2
fi

# Prepare `venv/relay_demo` - start with python of specific version:
"${pythonX}" -m venv venv/relay_demo
source venv/relay_demo/bin/activate

# Continue with python from `venv/relay_demo`:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .

# Build and test:
python -m tox

# Add `demo` dir into PATH to make Bash pick up `relay_demo` command:
PATH="${PATH}:$(pwd)/demo"
export PATH

# Enable auto-completion for `relay_demo` command:
if [[ "${BASH_VERSION}" == 5* ]]
then
    complete -o nosort -C "python -m argrelay.relay_client" relay_demo
else
    # Old Bash versions do not support `nosort` option:
    complete -C "python -m argrelay.relay_client" relay_demo
fi

# Symlink sample config client and server files as user dot files:
ln -snf "$(pwd)/demo/argrelay.client.yaml" ~/".argrelay.client.yaml"
ln -snf "$(pwd)/demo/argrelay.server.yaml" ~/".argrelay.server.yaml"

# Invoke completion programmatically:
function invoke_completion {
    # This function can be turned into generic one to invoke any
    # registered completion in Bash, but it is not straightforward, see:
    # https://brbsix.github.io/2015/11/29/accessing-tab-completion-programmatically-in-bash/
    # Instead, at least, invoke completion command for just the script above:
    (
        export COMP_LINE="${READLINE_LINE}"
        export COMP_POINT="${READLINE_POINT}"
        # CompType.DescribeArgs = ASCII '^':
        export COMP_TYPE='94'
        # NOTE: Not useful: for any key sequence, it is only set to the last key (no use case at the moment).
        export COMP_KEY="88"

        python -m argrelay.relay_client
    )
}

# Bind Alt+Shift+Q to `invoke_completion` function.
bind -x '"\eQ":"invoke_completion"'
# See limitation of `bind -x` (which might only be a limitation of older Bash versions):
# https://stackoverflow.com/questions/4200800/in-bash-how-do-i-bind-a-function-key-to-a-command/4201274#4201274

# Show what would be done for `relay_demo` auto-completion:
complete -p relay_demo

# Disable exit on errors for interactive shell (see enabling them for the duration of this script above):
set +e
set +u
