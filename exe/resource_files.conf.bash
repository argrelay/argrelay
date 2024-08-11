########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This resource file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying resource files, format:
# module_name module_dir_src_path argrelay_dir_dst_path
# shellcheck disable=SC2034
module_path_file_tuples=(
    argrelay custom_integ_res/argrelay_common_lib.bash exe/argrelay_common_lib.bash
    argrelay custom_integ_res/shell_env.bash exe/shell_env.bash
    argrelay custom_integ_res/check_env.bash exe/check_env.bash
    argrelay custom_integ_res/dev_shell.bash exe/dev_shell.bash
    argrelay custom_integ_res/init_shell_env.bash exe/init_shell_env.bash
    argrelay custom_integ_res/upgrade_env_packages.bash exe/upgrade_env_packages.bash
    argrelay custom_integ_res/script_plugin.d/check_env_plugin.all_plugins.bash exe/script_plugin.d/check_env_plugin.all_plugins.bash
    argrelay custom_integ_res/script_plugin.d/check_env_plugin.bash_version.bash exe/script_plugin.d/check_env_plugin.bash_version.bash
)
########################################################################################################################
