import importlib
from typing import Type


class AbstractPlugin:
    plugin_instance_id: str
    config_dict: dict

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        self.plugin_instance_id = plugin_instance_id
        self.config_dict = config_dict

    def activate_plugin(self):
        """
        One-time plugin activation callback during server startup.

        This is a chance to initialize (once) any resources plugin requires.
        """
        pass

    def validate_loaded_data(self, static_data: "StaticData"):
        """
        Callback to validate data after all :class:`AbstractLoader`-s completed loading data.

        This is a chance for any plugin to verify that the data still matches its expectation.
        """
        pass


def import_plugin_class(plugin_entry):
    plugin_module = importlib.import_module(plugin_entry.plugin_module_name)
    plugin_class: Type[AbstractPlugin] = getattr(
        plugin_module,
        plugin_entry.plugin_class_name,
    )
    return plugin_class


def instantiate_plugin(
    plugin_instance_id: str,
    plugin_entry,
):
    plugin_class = import_plugin_class(plugin_entry)
    plugin_object: AbstractPlugin = plugin_class(
        plugin_instance_id,
        plugin_entry.plugin_config,
    )
    return plugin_object
