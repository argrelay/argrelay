from __future__ import annotations

from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.enum_desc.PluginType import PluginType
from argrelay.runtime_context.PluginClientAbstract import PluginClientAbstract


class PluginCheckEnvAbstract(PluginClientAbstract):
    """
    Implements FS_36_17_84_44 `check_env`.
    """

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
        )

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.LoaderPlugin

    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        """
        Executes 1 to N checks and returns results of each one.

        *   `online_mode == False` allows skipping some checks which require connection to serve.
        *   `online_mode == True` execute all checks - if connection to serve is required, such checks may fail.
        *   `online_mode is None` allows selecting default behavior (or automatic detection).
        """
        pass
