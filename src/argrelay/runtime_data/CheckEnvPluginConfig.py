from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_data.PluginEntry import PluginEntry


@dataclass
class CheckEnvPluginConfig:
    """
    See also `CheckEnvPluginConfigSchema`.
    """

    check_env_plugin_instances: dict[str, PluginEntry] = field()
    """
    Same as `server_plugin_instances` but for FS_36_17_84_44 `check_env` only.
    """

    check_env_plugin_instance_id_activate_list: list[str] = field()
    """
    Same as `plugin_instance_id_activate_list` but for FS_36_17_84_44 `check_env` only.
    """
