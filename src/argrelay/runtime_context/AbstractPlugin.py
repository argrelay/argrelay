import importlib
from copy import deepcopy
from typing import Type

from argrelay.enum_desc.PluginType import PluginType
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractPlugin:

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        self.server_config: ServerConfig = server_config
        self.plugin_instance_id: str = plugin_instance_id
        self.plugin_config_dict: dict = self.load_config(plugin_config_dict)

        self.validate_config()

    # TODO_10_72_28_05: This will go away together with switch to FS_33_76_82_84 composite tree config:
    def _compare_config_with_composite_tree(
        self,
    ):
        """
        Compares `CompositeInfoType` extracted from `composite_tree` with
        data manually specified in `plugin_config_dict`.
        """
        pass

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        """
        Pre-proces the given config on load (e.g. populate default values).

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
        One-time plugin activation callback during server startup.

        This is a chance to initialize (once) any resources plugin requires.
        """
        pass

    def validate_loaded_data(
        self,
        static_data: "StaticData"
    ) -> None:
        """
        Callback to validate data after all :class:`AbstractLoader`-s completed loading data.

        This is a chance for any plugin to verify that the data still matches its expectation.
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


def instantiate_plugin(
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
