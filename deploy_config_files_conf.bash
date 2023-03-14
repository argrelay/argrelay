########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

# Tuples specifying config files, format:
# module_name relative_dir_path config_file_name
module_path_file_tuples=(
    # Note: a project integrating `argrelay` must provide its own set of
    #       customized `argrelay` config files instead (from its own module).

    argrelay argrelay.conf.d argrelay.server.yaml
    argrelay argrelay.conf.d argrelay.client.json
)
########################################################################################################################

