from pymongo import MongoClient

from argrelay.meta_data.PluginType import PluginType
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.misc_helper import eprint
from argrelay.misc_helper.AbstractPlugin import instantiate_plugin
from argrelay.mongo_data import MongoClientWrapper
from argrelay.mongo_data.MongoServerWrapper import MongoServerWrapper
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc


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
        self._activate_plugins()
        self._start_mongo_server()
        self._index_data()

    def get_mongo_database(self):
        return self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

    def _activate_plugins(self):
        """
        Calls each plugin to update :class:`StaticData`.
        """

        eprint(f"plugin_list: {self.server_config.plugin_list}")

        for plugin_entry in self.server_config.plugin_list:
            eprint(f"using: {plugin_entry}")

            # Populate `plugin_dict`:
            self.server_config.plugin_dict[plugin_entry.plugin_id] = plugin_entry

            if plugin_entry.plugin_type == PluginType.LoaderPlugin:
                plugin_object: AbstractLoader = instantiate_plugin(plugin_entry)
                plugin_object.activate_plugin()
                # Use loader to update data:
                self.server_config.static_data = plugin_object.update_static_data(self.server_config.static_data)
                server_config_desc.dict_schema.validate(self.server_config.static_data)
                continue

            if plugin_entry.plugin_type == PluginType.InterpFactoryPlugin:
                plugin_object: AbstractInterpFactory = instantiate_plugin(plugin_entry)
                plugin_object.activate_plugin()
                # Store instance of `AbstractInterpFactory` under specified id for future use:
                self.server_config.interp_factories[plugin_entry.plugin_id] = plugin_object
                continue

            if plugin_entry.plugin_type == PluginType.InvocatorPlugin:
                plugin_object: AbstractInvocator = instantiate_plugin(plugin_entry)
                plugin_object.activate_plugin()
                # Store instance of `AbstractInvocator` under specified id for future use:
                self.server_config.action_invocators[plugin_entry.plugin_id] = plugin_object
                continue

    def _start_mongo_server(self):
        self.mongo_server.start_mongo_server(self.server_config.mongo_config)

    def _index_data(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]
        MongoClientWrapper.store_envelopes(mongo_db, self.server_config.static_data)
