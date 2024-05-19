########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `@/exe/bootstrap_dev_env.bash` to configure `module_path_file_tuples` below.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
# shellcheck disable=SC2034
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).
    #       Integration assumes different plugins, their configs, etc.

    # For example:
    argrelay sample_conf argrelay_server.yaml
    argrelay sample_conf argrelay_client.json
)
########################################################################################################################

