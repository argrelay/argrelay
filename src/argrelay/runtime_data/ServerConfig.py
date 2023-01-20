from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.StaticData import StaticData


@dataclass
class ServerConfig:
    connection_config: ConnectionConfig
    mongo_config: MongoConfig

    plugin_list: list[PluginEntry]
    """
    List of plugin. It is a list because the order might be important (it is the order of plugin activation).
    Indexed version (from `plugin_id` into `plugin_entry`) is generated into `plugin_dict`.
    """

    static_data: StaticData

    # TODO: Keep this runtime objects in separate (`ServerRuntime`?) class. Ensure/implement ServerConfig dumping on request (for troubleshooting).
    plugin_dict: dict[str, PluginEntry] = field(default_factory = lambda: {})
    """
    Entries in `plugin_dict` are not directly loaded from config.
    They are are populated from `plugin_list` (key = `plugin_id`, value = `plugin_entry`).
    """

    # TODO: Keep this runtime objects in separate (`ServerRuntime`?) class. Ensure/implement ServerConfig dumping on request (for troubleshooting).
    data_loaders: dict[str, "AbstractLoader"] = field(default_factory = lambda: {})
    """
    Entries in `data_loaders` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """

    # TODO: Keep this runtime objects in separate (`ServerRuntime`?) class. Ensure/implement ServerConfig dumping on request (for troubleshooting).
    interp_factories: dict[str, "AbstractInterpFactory"] = field(default_factory = lambda: {})
    """
    Entries in `interp_factories` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """

    # TODO: Keep this runtime objects in separate (`ServerRuntime`?) class. Ensure/implement ServerConfig dumping on request (for troubleshooting).
    action_invocators: dict[str, "AbstractInvocator"] = field(default_factory = lambda: {})
    """
    Entries in `action_invocators` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """
