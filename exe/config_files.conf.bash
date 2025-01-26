########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying config files, format:
# module_name module_dir_src_path argrelay_dir_dst_path
# shellcheck disable=SC2034
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).
    #       Integration assumes different plugins, their configs, etc.

    # For example:
    argrelay_app_bootstrap sample_conf/argrelay_client.json conf/argrelay_client.json
    argrelay_app_bootstrap sample_conf/argrelay_server.yaml conf/argrelay_server.yaml
    argrelay_app_bootstrap sample_conf/argrelay_plugin.yaml conf/argrelay_plugin.yaml
    argrelay_app_bootstrap sample_conf/check_env_plugin.conf.bash conf/check_env_plugin.conf.bash
    argrelay_app_bootstrap sample_conf/check_env_plugin.conf.yaml conf/check_env_plugin.conf.yaml
)
########################################################################################################################

