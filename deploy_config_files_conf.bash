########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.
# It is *sourced* by `bootstrap_venv.bash` to configure `module_path_file_tuples` below.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).
    #       Integration assumes different plugins, their configs, etc.

    # For example (see `deploy_config_files.bash` from `argrelay` repo):
    argrelay argrelay.conf.d argrelay.server.yaml
    argrelay argrelay.conf.d argrelay.client.json
)
########################################################################################################################

