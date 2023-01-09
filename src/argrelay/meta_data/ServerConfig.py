from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.meta_data.ConnectionConfig import ConnectionConfig
from argrelay.meta_data.PluginEntry import PluginEntry
from argrelay.meta_data.StaticData import StaticData
from argrelay.mongo_data.MongoConfig import MongoConfig


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

    plugin_dict: dict[str, PluginEntry] = field(default_factory = lambda: {})
    """
    Entries in `plugin_dict` are not directly loaded from config.
    They are are populated from `plugin_list` (key = `plugin_id`, value = `plugin_entry`).
    """

    interp_factories: dict[str, "AbstractInterpFactory"] = field(default_factory = lambda: {})
    """
    Entries in `interp_factories` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """

    action_invocators: dict[str, "AbstractInvocator"] = field(default_factory = lambda: {})
    """
    Entries in `action_invocators` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """
