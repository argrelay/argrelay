import importlib
from typing import Type

from pymongo import MongoClient

from argrelay.data_schema.ServerConfigSchema import server_config_desc
from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.PluginType import PluginType
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.misc_helper import eprint
from argrelay.mongo_data import MongoClientWrapper
from argrelay.mongo_data.MongoServerWrapper import MongoServerWrapper


class LocalServer:
    """
    Server functionality without network-exposed API wrapper
    """

    server_config: ServerConfig
    mongo_server: MongoServerWrapper
    mongo_client: MongoClient

    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.mongo_server = MongoServerWrapper()
        self.mongo_client = MongoClientWrapper.get_mongo_client(self.server_config.mongo_config)

    def start_local_server(self):
        self._run_plugins()
        self._start_mongo_server()
        self._index_data()

    def get_mongo_database(self):
        return self.mongo_client[self.server_config.mongo_config.database_name]

    def _run_plugins(self):
        """
        Calls each plugin to update :class:`StaticData`.
        """

        eprint(f"plugin_list: {self.server_config.plugin_list}")

        for plugin_entry in self.server_config.plugin_list:
            eprint(f"using: {plugin_entry}")
            plugin_module = importlib.import_module(plugin_entry.plugin_module_name)

            if plugin_entry.plugin_type == PluginType.LoaderPlugin:
                plugin_class: Type[AbstractLoader] = getattr(
                    plugin_module,
                    plugin_entry.plugin_class_name,
                )
                plugin_object: AbstractLoader = plugin_class(plugin_entry.plugin_config)
                # Use loader to update data:
                self.server_config.static_data = plugin_object.update_static_data(self.server_config.static_data)
                server_config_desc.object_schema.validate(self.server_config.static_data)

            if plugin_entry.plugin_type == PluginType.InterpFactoryPlugin:
                plugin_class: Type[AbstractInterpFactory] = getattr(
                    plugin_module,
                    plugin_entry.plugin_class_name,
                )
                plugin_object: AbstractInterpFactory = plugin_class(plugin_entry.plugin_config)
                # Store instance of factory under specified id for future use:
                self.server_config.interp_factories[plugin_entry.plugin_id] = plugin_object

    def _start_mongo_server(self):
        self.mongo_server.start_mongo_server(self.server_config.mongo_config)

    def _index_data(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.database_name]
        MongoClientWrapper.store_objects(mongo_db, self.server_config.static_data)
