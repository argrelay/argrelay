#!/usr/bin/env bash

# This script is source-able by `~/.bashrc`:
#     source path/to/argrelay-rc.bash
# First, "copy and paste and modify" it.
# When sourced in `~/.bashrc`, `argrelay` auto-completion for `reley_demo` command
# becomes permanent and available immediately in any Bash instance.
# Instead of `relay_demo` there might be `your_command`.
# Those places requiring modification are marked with `CUSTOMIZE` keyword.

# Note that enabling exit on error (like `set -e` below) will exit parent Bash shell (as this one is sourced).
# Use these options with care as it prevents starting any shell in case of errors.

# Return non-zero exit code from commands within a pipeline:
#set -o pipefail
# Exit on non-zero exit code from a command:
#set -e
# Error on undefined variables:
#set -u
# Debug: Print commands after reading from a script:
#set -v
# Debug: Print commands before execution:
#set -x

# Path to exposes commands with `PATH` evn var:
# CUSTOMIZE: Use explicit dirname of `/path/to/somewhere` where `your_command` is instead of "automatic" `$(pwd)`.
PATH_TO_SCRIPTS="$(pwd)"

# The following files are generated/deployed by `build-git-env.bash`/`build-pip-env.bash` scripts.
# Ensure both server and client scripts are in the same dir (copy them there if not):
test -f "${PATH_TO_SCRIPTS}/run_argrelay_server" || return 1
test -f "${PATH_TO_SCRIPTS}/run_argrelay_client" || return 1
# Ensure both server and client configs are deployed (`build-git-env.bash` creates them if not available):
test -f ~/".argrelay.server.yaml" || return 1
test -f ~/".argrelay.client.json" || return 1

# Add dir with `relay_demo` command into PATH to make it available in Bash as plain `basename`:
PATH="${PATH_TO_SCRIPTS}:${PATH}"
export PATH

# When `run_argrelay_client` is executed,
# its actual command name is sent as the first arg (args[0]) which `argrelay` framework
# can use to look up and run any custom command line interpreter.
# The demo is configured to expect `relay_demo` as the first arg.
# Create `relay_demo` command (just symlink to `run_argrelay_client`):
# CUSTOMIZE: Use `your_command` instead of `relay_demo`.
cd "${PATH_TO_SCRIPTS}" > /dev/null || return 1
ln -snf run_argrelay_client relay_demo
cd - > /dev/null || return 1

# Command line auto-completion process is largely similar to parsing command line args.
# The difference is only in last step - either/or:
# (A) an action is run             (based on provided parsed arg values)
# (B) arg values are suggested     (based on provided parsed arg values)
# Therefore, the same `run_argrelay_client` can run both processes:
# (A) as target command of `relay_demo` symlink (above)
# (B) as `-C` argument to Bash `complete` to configure auto-completion for `relay_demo` (below)
# Enable auto-completion for `relay_demo` command:
if [[ "${BASH_VERSION}" == 5* ]]
then
    # CUSTOMIZE: Use `your_command` instead of `relay_demo`.
    complete -o nosort -C run_argrelay_client relay_demo
else
    # Old Bash versions do not support `nosort` option:
    # CUSTOMIZE: Use `your_command` instead of `relay_demo`.
    complete           -C run_argrelay_client relay_demo
fi

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
        export COMP_TYPE="94"
        # NOTE: Not useful: for any key sequence, it is only set to the last key (no use case at the moment).
        export COMP_KEY="88"

        run_argrelay_client
    )
}

# Bind Alt+Shift+Q to `invoke_completion` function.
bind -x '"\eQ":"invoke_completion"'
# See limitation of `bind -x` (which might only be a limitation of older Bash versions):
# https://stackoverflow.com/questions/4200800/in-bash-how-do-i-bind-a-function-key-to-a-command/4201274#4201274

# Disable exit on errors and any extra debug info for interactive shell
# (see enabling them for the duration of this script above):
set +o pipefail
set +e
set +u
set +v
set +x
