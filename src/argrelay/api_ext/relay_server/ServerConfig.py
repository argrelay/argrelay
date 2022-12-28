from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.api_ext.ConnectionConfig import ConnectionConfig
from argrelay.api_ext.relay_server.AbstractInterpFactory import AbstractInterpFactory
from argrelay.api_ext.relay_server.PluginEntry import PluginEntry
from argrelay.api_ext.relay_server.StaticData import StaticData
from argrelay.mongo_data.MongoConfig import MongoConfig


@dataclass
class ServerConfig:
    connection_config: ConnectionConfig
    mongo_config: MongoConfig
    plugin_list: list[PluginEntry]
    static_data: StaticData
    interp_factories: dict[str, AbstractInterpFactory] = field(default_factory = lambda: {})
