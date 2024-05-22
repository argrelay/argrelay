########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This resource file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_dev_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying resource files, format:
# module_name relative_dir_path resource_file_name
# shellcheck disable=SC2034
module_path_file_tuples=(
    argrelay custom_integ_res argrelay_common_lib.bash
    argrelay custom_integ_res shell_env.bash
    argrelay custom_integ_res check_env.bash
    argrelay custom_integ_res dev_shell.bash
    argrelay custom_integ_res init_shell_env.bash
    argrelay custom_integ_res upgrade_all_packages.bash
)
########################################################################################################################
