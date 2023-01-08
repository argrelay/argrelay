import importlib
from typing import Type


class AbstractPlugin:
    config_dict: dict

    def __init__(
        self,
        config_dict: dict,
    ):
        self.config_dict = config_dict

    def activate_plugin(self):
        pass


def import_plugin_class(plugin_entry):
    plugin_module = importlib.import_module(plugin_entry.plugin_module_name)
    plugin_class: Type[AbstractPlugin] = getattr(
        plugin_module,
        plugin_entry.plugin_class_name,
    )
    return plugin_class


def instantiate_plugin(plugin_entry):
    plugin_class = import_plugin_class(plugin_entry)
    plugin_object: AbstractPlugin = plugin_class(plugin_entry.plugin_config)
    return plugin_object
