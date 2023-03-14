from pymongo import MongoClient

from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper import eprint
from argrelay.misc_helper.AbstractPlugin import instantiate_plugin
from argrelay.mongo_data import MongoClientWrapper
from argrelay.mongo_data.MongoServerWrapper import MongoServerWrapper
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc


class LocalServer:
    """
    This is plain server functionality without API-wrapper to expose over the network (hence, local).

    The API-wrapper exposing `LocalServer` over the network is `CustomFlaskApp`.
    """

    server_config: ServerConfig
    mongo_server: MongoServerWrapper
    mongo_client: MongoClient
    query_engine: QueryEngine
    help_hint_cache: HelpHintCache

    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.mongo_server = MongoServerWrapper()
        self.mongo_client = MongoClientWrapper.get_mongo_client(self.server_config.mongo_config)
        self.query_engine = QueryEngine(
            self.server_config.query_cache_config,
            self.get_mongo_database(),
        )
        self.help_hint_cache = HelpHintCache(
            self.query_engine,
        )

    def start_local_server(self):
        self._activate_plugins()
        self._start_mongo_server()
        self._load_mongo_data()
        self._create_mongo_index()
        self._populate_help_hint_cache()

    def get_mongo_database(self):
        return self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

    def get_query_engine(self):
        return self.query_engine

    def _activate_plugins(self):
        """
        Calls each plugin to update :class:`StaticData`.
        """

        for plugin_instance_id in self.server_config.plugin_instance_id_load_list:
            plugin_entry = self.server_config.plugin_dict[plugin_instance_id]

            if plugin_entry.plugin_type == PluginType.LoaderPlugin:
                plugin_object: AbstractLoader = instantiate_plugin(
                    plugin_instance_id,
                    plugin_entry,
                )
                plugin_object.activate_plugin()
                # Store instance of `AbstractLoader` under specified id for future use:
                self.server_config.data_loaders[plugin_instance_id] = plugin_object
                # Use loader to update data:
                self.server_config.static_data = plugin_object.update_static_data(self.server_config.static_data)
                continue

            if plugin_entry.plugin_type == PluginType.InterpFactoryPlugin:
                plugin_object: AbstractInterpFactory = instantiate_plugin(
                    plugin_instance_id,
                    plugin_entry,
                )
                plugin_object.activate_plugin()
                # Store instance of `AbstractInterpFactory` under specified id for future use:
                self.server_config.interp_factories[plugin_instance_id] = plugin_object
                continue

            if plugin_entry.plugin_type == PluginType.DelegatorPlugin:
                plugin_object: AbstractDelegator = instantiate_plugin(
                    plugin_instance_id,
                    plugin_entry,
                )
                plugin_object.activate_plugin()
                # Store instance of `AbstractDelegator` under specified id for future use:
                self.server_config.action_delegators[plugin_instance_id] = plugin_object
                continue

        eprint("validating data...")
        self._validate_static_data()

    def _validate_static_data(self):
        self._validate_static_data_schema()
        self._validata_static_data_by_plugins()

    def _validate_static_data_schema(self):
        # Note that this is slow for large data sets:
        static_data_dict = static_data_desc.dict_schema.dump(self.server_config.static_data)
        static_data_desc.validate_dict(static_data_dict)

    def _validata_static_data_by_plugins(self):
        all_plugins: [AbstractLoader] = []
        all_plugins.extend(self.server_config.data_loaders.values())
        all_plugins.extend(self.server_config.interp_factories.values())
        all_plugins.extend(self.server_config.action_delegators.values())

        for plugin_instance in all_plugins:
            plugin_instance.validate_loaded_data(self.server_config.static_data)

    def _start_mongo_server(self):
        self.mongo_server.start_mongo_server(self.server_config.mongo_config)

    def _load_mongo_data(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]
        MongoClientWrapper.store_envelopes(
            mongo_db,
            self.server_config.static_data,
        )

    def _create_mongo_index(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]
        # Include `envelope_class` field into index by default:
        self.server_config.static_data.known_arg_types.append(ReservedArgType.EnvelopeClass.name)
        MongoClientWrapper.create_index(
            mongo_db,
            self.server_config.static_data,
        )

    def _populate_help_hint_cache(self):
        self.help_hint_cache.populate_cache()
