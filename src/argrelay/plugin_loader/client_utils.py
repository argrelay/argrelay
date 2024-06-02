import os
from typing import Union

from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.misc_helper_common.TypeDesc import TypeDesc


def load_client_plugin_config(
    plugin_instance_id: str,
    type_desc: TypeDesc,
) -> Union[dict, None]:
    """
    This function loads plugin config on client side.

    See FS_83_23_99_90 client plugin config override.
    """

    config_file_path = f"{get_argrelay_dir()}/conf/plugin_config/{plugin_instance_id}.yaml"
    if os.path.isfile(config_file_path):
        return type_desc.dict_from_yaml_file(config_file_path)
    else:
        return None
