#!/usr/bin/env bash

# This script is not supposed to be run or sourced directly.
# Instead, run `dev-shell.bash`.

# The steps this script performs:
# * Set up python venv.
# * Build `argrelay`.
# * Install `argrelay` in editable mode.
# * Bind command name `try_relay` with Bash auto-completion.
#   The binding is temporarily (while `dev-shell.bash` is running).
#   This step is what normally goes to `~/.bashrc` to make
#   Bash auto-completion permanent.

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

# Prepare venv - start with python of specific version:
"${pythonX}" -m venv venv
source venv/bin/activate

# Continue with python from venv:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .

# Build and test:
python -m tox

# Add `example` dir into PATH to make Bash pick up `try_relay` command:
export PATH="${PATH}:$(pwd)/example"

# Enable auto-completion for `try_relay` command:
if [[ "${BASH_VERSION}" == 5* ]]
then
    complete -o nosort -C "python -m argrelay.relay_client" try_relay
else
    # Old Bash versions do not support `nosort` option:
    complete -C "python -m argrelay.relay_client" try_relay
fi

# Symlink sample config client and server files as user dot files:
ln -snf "$(pwd)/example/argrelay.client.yaml" ~/".argrelay.client.yaml"
ln -snf "$(pwd)/example/argrelay.server.yaml" ~/".argrelay.server.yaml"

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

if [[ "${BASH_VERSION}" == 5* ]]
then
    # TODO: Change it to F12:
    # Bind F8 to invoke_completion:
    bind -x '"\e[19~":"invoke_completion"'
    # See this page for ANSI escape sequences:
    # https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
else
    # Bind Alt + Shift + Q.
    # Old Bash versions have poor support for some key shortcuts:
    bind -x '"\eQ":"invoke_completion"'
    # See limitation of `bind -x`:
    # https://stackoverflow.com/a/4201274
fi

# List command paths:
for cmd_item in python pip tox
do
    echo -n "${cmd_item}: "
    which "${cmd_item}"
done

# Show what would be done for `try_relay` auto-completion:
complete -p try_relay

# Disable exit on errors for interactive shell:
set +e
set +u

