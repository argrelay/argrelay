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

    plugin_id_load_list: list[str]
    """
    List of `plugin_id`s in order of loading. Each `plugin_id` is a key into `plugin_dict`.
    """

    plugin_dict: dict[str, PluginEntry]
    """
    Key = `plugin_id`
    """

    static_data: StaticData

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
