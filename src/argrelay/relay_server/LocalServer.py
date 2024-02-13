import time
import uuid
from copy import deepcopy

from pymongo import MongoClient

from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper_common import eprint
from argrelay.mongo_data import MongoClientWrapper
from argrelay.mongo_data.MongoServerWrapper import MongoServerWrapper
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_context.AbstractPlugin import instantiate_plugin, AbstractPlugin
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc


class LocalServer:
    """
    This is plain server functionality without API-wrapper to expose over the network (hence, local).

    The API-wrapper exposing `LocalServer` over the network is `CustomFlaskApp`.
    """

    def __init__(
        self,
        server_config: ServerConfig,
    ):
        self.server_instance_id = uuid.uuid4()
        self.server_config: ServerConfig = server_config
        self.mongo_server: MongoServerWrapper = MongoServerWrapper()
        self.mongo_client: MongoClient = MongoClientWrapper.get_mongo_client(self.server_config.mongo_config)
        self.query_engine: QueryEngine = QueryEngine(
            self.server_config.query_cache_config,
            self.get_mongo_database(),
            self.server_config.mongo_config.distinct_values_query,
        )
        self.help_hint_cache: HelpHintCache = HelpHintCache(
            self.query_engine,
        )
        # seconds since epoch:
        self.server_start_time: int = int(time.time())

    def start_local_server(self):
        self._activate_plugins()
        self._start_mongo_server()
        self._load_mongo_data()
        self._create_mongo_index()
        self._populate_help_hint_cache()
        self._log_connection_url()

    def stop_local_server(self):
        self._stop_mongo_server()

    def get_mongo_database(self):
        return self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

    def get_query_engine(self):
        return self.query_engine

    def _activate_plugins(self):
        """
        Calls each plugin to update :class:`StaticData`.
        """

        for plugin_instance_id in self.server_config.plugin_instance_id_activate_list:
            plugin_entry: PluginEntry = self.server_config.plugin_instance_entries[plugin_instance_id]

            if not plugin_entry.plugin_enabled:
                continue

            plugin_instance: AbstractPlugin = instantiate_plugin(
                self.server_config,
                plugin_instance_id,
                plugin_entry,
            )
            plugin_type = plugin_instance.get_plugin_type()

            if plugin_type is PluginType.LoaderPlugin:
                plugin_instance: AbstractLoader
                plugin_instance.activate_plugin()
                # Store instance of `AbstractLoader` under specified id for future use:
                self.server_config.data_loaders[plugin_instance_id] = plugin_instance
                # Use loader to update data:
                self.server_config.static_data = plugin_instance.update_static_data(self.server_config.static_data)
                continue

            if plugin_type is PluginType.InterpFactoryPlugin:
                plugin_instance: AbstractInterpFactory
                plugin_instance.activate_plugin()
                # Store instance of `AbstractInterpFactory` under specified id for future use:
                self.server_config.interp_factories[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.DelegatorPlugin:
                plugin_instance: AbstractDelegator
                plugin_instance.activate_plugin()
                # Store instance of `AbstractDelegator` under specified id for future use:
                self.server_config.action_delegators[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.ConfiguratorPlugin:
                plugin_instance: AbstractDelegator
                plugin_instance.activate_plugin()
                # Store instance of `AbstractConfigurator` under specified id for future use:
                self.server_config.server_configurators[plugin_instance_id] = plugin_instance
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

    def _stop_mongo_server(self):
        self.mongo_server.stop_mongo_server()

    def _load_mongo_data(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]
        MongoClientWrapper.store_envelopes(
            mongo_db,
            # TODO_00_79_72_55: Remove `static_data` from `server_config`:
            self.server_config.static_data,
        )

    def _create_mongo_index(self):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

        for collection_name in self.server_config.static_data.envelope_collections:
            envelope_collection: EnvelopeCollection = self.server_config.static_data.envelope_collections[
                collection_name
            ]
            # Include `envelope_class` field into index by default:
            index_fields: list[str] = deepcopy(envelope_collection.index_fields)
            index_fields.append(ReservedArgType.EnvelopeClass.name)
            MongoClientWrapper.create_index(
                mongo_db,
                collection_name,
                envelope_collection.index_fields,
            )

    def _populate_help_hint_cache(self):
        self.help_hint_cache.populate_cache()

    def _log_connection_url(self):
        host_name = self.server_config.connection_config.server_host_name
        port_number = self.server_config.connection_config.server_port_number
        eprint(f"http://{host_name}:{port_number}")
