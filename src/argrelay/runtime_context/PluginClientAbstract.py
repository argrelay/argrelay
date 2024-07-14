from argrelay.runtime_context.AbstractPlugin import AbstractPlugin, import_plugin_class


class PluginClientAbstract(AbstractPlugin):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
        )


def instantiate_client_plugin(
    plugin_instance_id: str,
    plugin_entry,
):
    plugin_class = import_plugin_class(plugin_entry)
    plugin_object: AbstractPlugin = plugin_class(
        plugin_instance_id,
        plugin_entry.plugin_config,
    )
    return plugin_object
