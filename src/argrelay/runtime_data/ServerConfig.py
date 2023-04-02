from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig
from argrelay.relay_server.QueryCacheConfig import QueryCacheConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.StaticData import StaticData


@dataclass
class ServerConfig:
    connection_config: ConnectionConfig
    mongo_config: MongoConfig
    query_cache_config: QueryCacheConfig
    gui_banner_config: GuiBannerConfig

    plugin_instance_id_load_list: list[str]
    """
    List of `plugin_instance_id`s in order of loading. Each `plugin_instance_id` is a key into `plugin_dict`.
    """

    plugin_dict: dict[str, PluginEntry]
    """
    Key = `plugin_instance_id`
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
    action_delegators: dict[str, "AbstractDelegator"] = field(default_factory = lambda: {})
    """
    Entries in `action_delegators` are not directly loaded from config.
    These are plugin instances created during plugin activation.
    """
