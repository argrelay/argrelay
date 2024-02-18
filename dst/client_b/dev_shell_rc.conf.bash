# See FS_57_36_37_48 multiple clients:
# Limitation of using multiple nested `@/exe/dev_shell.bash` requires this config.

# This config is for `@/tests/slow_tests/multiple_clients/test_multiple_clients.bash` with
# these paths to the clients:
#     *   `@/tmp/multiple_clients/client_a/`
#     *   `@/tmp/multiple_clients/client_b/`
# shellcheck disable=SC2154
source "${argrelay_dir}/../client_a/exe/argrelay_rc.bash"
