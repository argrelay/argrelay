import importlib
from copy import deepcopy
from typing import Type

from argrelay.enum_desc.PluginType import PluginType
from argrelay.runtime_data.PluginEntry import PluginEntry


class AbstractPlugin:

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        self.plugin_instance_id: str = plugin_instance_id
        self.plugin_config_dict: dict = self.load_config(plugin_config_dict)

        self.validate_config()

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        """
        Pre-process the given config on load (e.g. populate default values).

        The default implementation is to return `plugin_config_dict` as is.

        The typical implementation is to call `TypeDesc.dict_from_input_dict`
        so that defaults are populated according to the given `Schema`.
        """
        return deepcopy(plugin_config_dict)

    def validate_config(
        self,
    ) -> None:
        """
        Validate schema or data for `plugin_config_dict`.

        The typical implementation is to call `TypeDesc.validate_dict(self.plugin_config_dict)`.

        If `load_config` is implemented via `TypeDesc.dict_from_input_dict`,
        validating step is only necessary if it does anything extra beyond what `Schema` can validate.
        """
        pass

    def get_plugin_type(
        self,
    ) -> PluginType:
        """
        Return one of the `PluginType`-s.
        """
        raise NotImplementedError

    def activate_plugin(
        self,
    ) -> None:
        """
        One-time plugin activation callback during startup.

        This is a chance to initialize (once) any resources plugin requires.
        """
        pass


def import_plugin_class(
    plugin_entry: PluginEntry,
):
    plugin_module = importlib.import_module(plugin_entry.plugin_module_name)
    plugin_class: Type[AbstractPlugin] = getattr(
        plugin_module,
        plugin_entry.plugin_class_name,
    )
    return plugin_class
