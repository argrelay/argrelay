from __future__ import annotations

from argrelay.runtime_context.AbstractPlugin import AbstractPlugin, import_plugin_class
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractPluginServer(AbstractPlugin):

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        self.server_config: ServerConfig = server_config
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
        )

    def provide_plugin_search_control(
        self,
    ) -> list[SearchControl]:
        """
        Report `search_control`, if plugin uses any.

        If plugin uses `search_control`, it is supposed to report it so that server can validate `data_envelope`-s.
        """
        return []


def instantiate_server_plugin(
    server_config: ServerConfig,
    plugin_instance_id: str,
    plugin_entry,
):
    plugin_class = import_plugin_class(plugin_entry)
    plugin_object: AbstractPlugin = plugin_class(
        server_config,
        plugin_instance_id,
        plugin_entry.plugin_config,
    )
    return plugin_object
