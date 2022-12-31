from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.meta_data.ConnectionConfig import ConnectionConfig
from argrelay.meta_data.PluginEntry import PluginEntry
from argrelay.meta_data.StaticData import StaticData
from argrelay.mongo_data.MongoConfig import MongoConfig


@dataclass
class ServerConfig:
    connection_config: ConnectionConfig
    mongo_config: MongoConfig
    plugin_list: list[PluginEntry]
    static_data: StaticData
    interp_factories: dict[str, AbstractInterpFactory] = field(default_factory = lambda: {})
