
# This script tests FS_57_36_37_48 multiple clients coexistence.
# The steps it performs:
# *   Make two clones of current git repo:
#     *   `@/tmp/multiple_clients/client_a/`
#     *   `@/tmp/multiple_clients/client_b/`
# *   Run `@/exe/bootstrap_env.bash` for both with `@/conf/` respectively (within each repo):
#     *   `@/dst/client_a/`
#     *   `@/dst/client_b/`
# *   Start nested `@/exe/dev_shell.bash` for both (in that order)
#     *   `@/tmp/multiple_clients/client_a/exe/dev_shell.bash`
#     *   `@/tmp/multiple_clients/client_b/exe/dev_shell.bash`
# *   Commands used:
#     *   `lay`                is configured for both `client_a` and `client_b`
#     *   `relay_demo`         is configured for both `client_a` and `client_b`
#     *   `some_command`       is configured for `client_a` only
#     *   `service_relay_demo` is configured for `client_b` only
# *   TODO: How can we test automatically that both `Alt+Shift+Q` and `Tab` work?

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

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/tests/slow_tests/multiple_clients/` -> `@/`:
argrelay_dir="$( dirname "$( dirname "$( dirname "${script_dir}" )" )" )"

# Run `@/exe/bootstrap_env.bash` if this file does not exits:
source "${argrelay_dir}/exe/argrelay_common_lib.bash"
ensure_inside_dev_shell

# Clean up:
for client_x in client_a client_b
do
    rm -rf "${argrelay_dir}/tmp/multiple_clients/${client_x}"
done

# Git root:
git_this_origin="$( git rev-parse --show-toplevel )"

# Git clone for both:
for client_x in client_a client_b
do
    mkdir -p "${argrelay_dir}/tmp/multiple_clients/${client_x}"
    git clone "${git_this_origin}" "${argrelay_dir}/tmp/multiple_clients/${client_x}"
done

# Run `@/exe/bootstrap_env.bash` for both:
for client_x in client_a client_b
do
    cd "${argrelay_dir}/tmp/multiple_clients/${client_x}/" && "./exe/bootstrap_env.bash" "./dst/${client_x}"
done

# Start `@/exe/dev_shell.bash` for `client_b` only
# (which has `@/conf/dev_shell_env.bash` to source `@/exe/shell_env.bash` from `client_a`):
"${argrelay_dir}/tmp/multiple_clients/client_b/exe/dev_shell.bash"

# TODO: At the moment, this script simply set things up to check working setup manually.
