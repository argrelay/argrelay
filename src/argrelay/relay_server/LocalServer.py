from __future__ import annotations

import time
import uuid
from copy import deepcopy
from typing import Union

from pymongo import MongoClient

from argrelay.composite_forest.CompositeForestValidator import validate_composite_forest
from argrelay.composite_forest.DictTreeWalker import contains_whitespace
from argrelay.enum_desc.PluginSide import PluginSide
from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.misc_helper_common import eprint
from argrelay.mongo_data import MongoClientWrapper
from argrelay.mongo_data.MongoServerWrapper import MongoServerWrapper
from argrelay.mongo_data.ProgressTracker import ProgressTracker
from argrelay.plugin_delegator.DelegatorAbstract import DelegatorAbstract
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.relay_server.UsageStatsStore import UsageStatsStore
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer, instantiate_server_plugin
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.IndexModel import IndexModel, index_props_
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import (
    envelope_collection_desc,
)
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_, envelope_payload_, envelope_id_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import search_control_list_
from argrelay.schema_config_interp.SearchControlSchema import (
    arg_name_to_prop_name_map_,
    collection_name_,
    search_control_desc,
)


class LocalServer:
    """
    This is plain server functionality without API-wrapper to expose over the network (hence, local).

    The API-wrapper exposing `LocalServer` over the network is `CustomFlaskApp`.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_config: PluginConfig,
    ):
        self.server_instance_id = uuid.uuid4()
        self.server_config: ServerConfig = server_config
        self.plugin_config: PluginConfig = plugin_config
        self.mongo_server: MongoServerWrapper = MongoServerWrapper()
        self.mongo_client: MongoClient = MongoClientWrapper.get_mongo_client(self.server_config.mongo_config)
        self.usage_stats_store = UsageStatsStore()
        self.query_engine: QueryEngine = QueryEngine(
            self.server_config.query_cache_config,
            self.get_mongo_database(),
            self.server_config.mongo_config.distinct_values_query,
        )
        self.help_hint_cache: HelpHintCache = HelpHintCache(
            self.query_engine,
        )

        self.cleaned_mongo_collections: set[str] = set()
        """
        *   On one hand, Mongo collections may have state and need to be cleaned.
        *   On another hand, they can be repeatedly updated by more than one plugin (potentially adding more data).

        Server uses `cleaned_mongo_collections` to track what collection have been cleaned once and what have not.
        """

        # FS_45_08_22_15 index model:
        # This internal server state is a convenience cache for index model which is also stored in data backend.
        self.index_model_per_collection: dict[str, IndexModel] = {}

        # seconds since epoch:
        self.server_start_time: int = int(time.time())

        self.root_func_loader: Union[AbstractInterpFactory | None] = None

    def start_local_server(
        self,
    ):
        self._instantiate_plugins()
        self._validate_composite_forest()
        self._activate_plugins()
        self._start_mongo_server()
        self._store_mongo_data()
        self._populate_help_hint_cache()
        self._log_connection_url()

    def stop_local_server(
        self,
    ):
        self._stop_mongo_server()

    def get_mongo_database(
        self,
    ):
        return self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

    def get_query_engine(
        self,
    ):
        return self.query_engine

    def _validate_composite_forest(
        self,
    ):
        validate_composite_forest(
            self.server_config.server_plugin_control.composite_forest,
            self.server_config.plugin_instances,
        )

    def _instantiate_plugins(
        self,
    ):
        """
        Instantiates every plugin.
        """

        for plugin_instance_id in self.plugin_config.plugin_instance_id_activate_list:
            plugin_entry: PluginEntry = self.plugin_config.server_plugin_instances[plugin_instance_id]

            if not plugin_entry.plugin_enabled:
                continue

            if (
                plugin_entry.plugin_side != PluginSide.PluginServerSideOnly
                and
                plugin_entry.plugin_side != PluginSide.PluginAnySide
            ):
                continue

            plugin_instance: AbstractPluginServer = instantiate_server_plugin(
                self.server_config,
                plugin_instance_id,
                plugin_entry,
            )
            plugin_type = plugin_instance.get_plugin_type()

            assert plugin_type.plugin_side is plugin_entry.plugin_side

            self.server_config.plugin_instances[plugin_instance_id] = plugin_instance

            if plugin_type is PluginType.LoaderPlugin:
                plugin_instance: AbstractLoader
                # Store instance of `AbstractLoader` under specified id for future use:
                self.server_config.data_loaders[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.InterpFactoryPlugin:
                plugin_instance: AbstractInterpFactory
                # Store instance of `AbstractInterpFactory` under specified id for future use:
                self.server_config.interp_factories[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.DelegatorPlugin:
                plugin_instance: DelegatorAbstract
                # Store instance of `DelegatorAbstract` under specified id for future use:
                self.server_config.action_delegators[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.ConfiguratorPlugin:
                plugin_instance: DelegatorAbstract
                # Store instance of `ConfiguratorAbstract` under specified id for future use:
                self.server_config.server_configurators[plugin_instance_id] = plugin_instance
                continue

    def _activate_plugins(
        self,
    ):
        for plugin_instance_id in self.plugin_config.plugin_instance_id_activate_list:
            # Skip those which were not instantiated:
            if plugin_instance_id in self.server_config.plugin_instances:
                self.server_config.plugin_instances[plugin_instance_id].activate_plugin()

        interp_factory: AbstractInterpFactory
        for plugin_instance_id, interp_factory in self.server_config.interp_factories.items():
            if interp_factory.is_root_func_loader():
                # There can only be one `root_func_loader`:
                assert self.root_func_loader is None
                self.root_func_loader = interp_factory

    def _pre_validate_static_data_per_step(
        self,
        envelope_collections: list[EnvelopeCollection],
        progress_tracker: ProgressTracker,
    ):
        self._pre_validate_static_data_schema_per_step(
            envelope_collections,
        )
        self._pre_validate_data_envelope_string_index_prop_values_per_step(
            envelope_collections,
            progress_tracker,
        )

    # noinspection PyMethodMayBeStatic
    def _pre_validate_static_data_schema_per_step(
        self,
        envelope_collections: list[EnvelopeCollection],
    ):
        # Note that this is slow for large data sets:
        for envelope_collection_obj in envelope_collections:
            envelope_collection_dict = envelope_collection_desc.dict_schema.dump(envelope_collection_obj)
            envelope_collection_desc.validate_dict(envelope_collection_dict)

    def _pre_validate_data_envelope_string_index_prop_values_per_step(
        self,
        envelope_collections: list[EnvelopeCollection],
        progress_tracker: ProgressTracker,
    ):
        """
        This validation ensures there is no blank values (`None`, whitespace, etc.) in `index_prop`-s.

        TODO: TODO_39_25_11_76: `data_envelope`-s with missing props.

        See also FS_99_81_19_25 no space in options.

        See also `_post_validate_all_data_envelope_for_missing_index_prop_names`.
        """

        for envelope_collection in envelope_collections:
            collection_name = envelope_collection.collection_name
            progress_tracker.track_collection_size_increment(
                collection_name,
                len(envelope_collection.data_envelopes),
            )
            for data_envelope in envelope_collection.data_envelopes:
                index_props = self.index_model_per_collection[collection_name].index_props
                for index_prop in index_props:
                    if index_prop not in data_envelope:
                        # Let the `data_envelope` load without some `prop_name`-s from `index_prop`-s
                        # in pre-validation - if any of `data_envelope`-s have that `prop_name`, it will fail
                        # in post-validation (see where `_raise_validation_error_for_missing_prop_name` is used).
                        # For now:
                        #     It is allowed to have no `prop_name` for all `data_envelope`
                        #     within given `collection_name` until at least one has it.
                        # TODO: TODO_39_25_11_76: `data_envelope`-s with missing props:
                        #       Be careful with "until at least one has it" as this
                        #       delayed validation has to be explicitly/separately run
                        #       after data is loaded.
                        #       Consider refactoring data manipulation into safe manager.
                        continue

                    prop_value = data_envelope[index_prop]
                    self._validate_string_prop_value(
                        collection_name,
                        index_prop,
                        prop_value,
                    )

    def _validate_string_prop_value(
        self,
        collection_name,
        index_prop,
        prop_value,
    ):
        if isinstance(prop_value, str):
            if not prop_value or not prop_value.strip():
                raise ValueError(f"`{collection_name}.{index_prop}` [{prop_value}] has to be non-blank string")
            if contains_whitespace(prop_value):
                raise ValueError(f"`{collection_name}.{index_prop}` [{prop_value}] cannot contain whitespace")
        elif isinstance(prop_value, list):
            for prop_value_item in prop_value:
                self._validate_string_prop_value(
                    collection_name,
                    index_prop,
                    prop_value_item,
                )
        else:
            # FS_06_99_43_60: array `prop_value`:
            raise ValueError(f"`{collection_name}.{index_prop}` has to be a `list` of `str` or `str`")

    def _post_validate_stored_data(
        self,
        progress_tracker: ProgressTracker,
    ):
        self._post_validate_all_data_envelope_for_missing_index_prop_names(
            progress_tracker,
        )
        self._post_validate_search_props_and_index_props_reference_each_other(
            self._scan_for_all_search_props(),
            progress_tracker,
        )

    def _post_validate_search_props_and_index_props_reference_each_other(
        self,
        search_props_per_collection: dict[str, set[str]],
        progress_tracker: ProgressTracker,
    ):
        """
        See TODO_39_25_11_76 missing props based on `search_control`-s for all loaded functions.

        This function relies on `_post_validate_all_data_envelope_for_missing_index_prop_names`
        to guarantee that all listed `index_props` exists in every loaded `data_envelope`.
        On top of that fact, this function ensures that every `search_control` used
        specifies `search_props` which exists among `index_props`.
        """

        # TODO: Deduplicate with L <- R:
        # Compare L -> R:
        # Ensure that `index_model` references are used in  some`search_control`.
        for collection_name, index_model in self.index_model_per_collection.items():
            if collection_name not in search_props_per_collection:
                progress_tracker.track_unused_index_props_per_collection_unused_by_search_control(
                    collection_name,
                    # all are unused:
                    index_model.index_props,
                )
            else:
                search_props = search_props_per_collection[collection_name]
                unused_index_props = []
                for index_prop in index_model.index_props:
                    if index_prop not in search_props:
                        unused_index_props.append(index_prop)
                if len(unused_index_props) > 0:
                    progress_tracker.track_unused_index_props_per_collection_unused_by_search_control(
                        collection_name,
                        # unused are selected only:
                        unused_index_props,
                    )

        # TODO: Deduplicate with L -> R:
        # Compare L <- R:
        # Ensure that every `search_prop` is among the `index_prop`-s in `index_model`:
        for collection_name, search_props in search_props_per_collection.items():
            if collection_name not in self.index_model_per_collection:
                progress_tracker.track_dangling_search_props_per_collection_undefined_by_index_model(
                    collection_name,
                    # all are dangling:
                    search_props,
                )
            else:
                search_props = search_props_per_collection[collection_name]
                index_props = self.index_model_per_collection[collection_name].index_props
                dangling_search_props = []
                for search_prop in search_props:
                    if search_prop not in index_props:
                        dangling_search_props.append(search_prop)
                if len(dangling_search_props) > 0:
                    progress_tracker.track_dangling_search_props_per_collection_undefined_by_index_model(
                        collection_name,
                        # dangling are selected only:
                        dangling_search_props,
                    )

    def _scan_for_all_search_props(
        self,
    ) -> dict[str, set[str]]:
        """
        Build search `prop_name`-s per `collection_name`
        by scanning `search_control`-s for `prop_name`-s.
        """

        search_props_per_collection: dict[str, set[str]] = {}

        plugin_search_controls: list[SearchControl] = []
        for plugin_instance in self.server_config.plugin_instances.values():
            plugin_search_controls.extend(plugin_instance.provide_plugin_search_control())

        # Scan `search_control`-s of all plugins:
        for search_control in plugin_search_controls:
            self._populate_search_props_per_collection(
                search_control_desc.dict_from_input_obj(search_control),
                search_props_per_collection,
            )

        # Scan `search_control`-s of all funcs:
        for func_envelope in self.query_engine.get_data_envelopes_cursor(
            ReservedEnvelopeClass.class_function.name,
            {
                f"{ReservedPropName.envelope_class.name}": f"{ReservedEnvelopeClass.class_function.name}",
            },
        ):
            for search_control in func_envelope[instance_data_][search_control_list_]:
                self._populate_search_props_per_collection(
                    search_control,
                    search_props_per_collection,
                )

        return search_props_per_collection

    # noinspection PyMethodMayBeStatic
    def _populate_search_props_per_collection(
        self,
        search_control: dict,
        search_props_per_collection,
    ):
        search_collection_name = search_control[collection_name_]

        search_props = search_props_per_collection.setdefault(
            search_collection_name,
            set(),
        )

        for arg_name_to_prop_name_entry in search_control[arg_name_to_prop_name_map_]:
            assert type(arg_name_to_prop_name_entry) is dict
            assert len(arg_name_to_prop_name_entry) == 1
            search_prop_name = next(iter(arg_name_to_prop_name_entry.values()))
            search_props.add(search_prop_name)

    def _post_validate_all_data_envelope_for_missing_index_prop_names(
        self,
        progress_tracker: ProgressTracker,
    ):
        """
        See TODO_39_25_11_76 missing props based on `index_prop`-s per `envelope_collection`.

        See also:
        *   `_pre_validate_data_envelope_string_index_prop_values_per_step`
        *   `_post_validate_search_props_and_index_props_reference_each_other`
        """

        progress_tracker.track_total_validation_start()

        # Verify that all prop names per `collection_name`
        # exists in all corresponding `data_envelope`-s:
        for collection_name in self.index_model_per_collection.keys():
            progress_tracker.track_collection_validation_start(collection_name)
            self.post_validate_collection_for_missing_index_prop_names(
                collection_name,
                progress_tracker,
            )
            progress_tracker.track_collection_validation_stop(collection_name)

        progress_tracker.track_total_validation_stop()

    def post_validate_collection_for_missing_index_prop_names(
        self,
        collection_name,
        progress_tracker,
    ):
        index_model = self.index_model_per_collection[collection_name]
        prev_found_missing_prop_names: dict[str, dict] = {}
        prev_found_existing_prop_names: dict[str, dict] = {}
        for data_envelope in self.query_engine.get_data_envelopes_cursor(
            collection_name,
            {},
        ):
            # TODO: Even if we track and validate `data_envelope` count on server start,
            #       we do not validate (only track increments) for `DelegatorDataBackendSet`
            #       for now - to do this, we need know how many `data_envelope`-s each
            #       set operation replaces.
            progress_tracker.track_collection_validation_increment(collection_name)

            for prop_name in index_model.index_props:
                if prop_name not in data_envelope:

                    if prop_name not in prev_found_missing_prop_names:
                        prev_found_missing_prop_names[prop_name] = deepcopy(data_envelope)

                    if prop_name in prev_found_existing_prop_names:
                        self._raise_validation_error_for_missing_prop_name(
                            True,
                            collection_name,
                            prop_name,
                            data_envelope,
                            prev_found_existing_prop_names[prop_name],
                        )
                else:

                    if prop_name not in prev_found_existing_prop_names:
                        prev_found_existing_prop_names[prop_name] = deepcopy(data_envelope)

                    if prop_name in prev_found_missing_prop_names:
                        self._raise_validation_error_for_missing_prop_name(
                            False,
                            collection_name,
                            prop_name,
                            data_envelope,
                            prev_found_missing_prop_names[prop_name],
                        )
                    prop_value = data_envelope[prop_name]
                    self._validate_string_prop_value(
                        collection_name,
                        prop_name,
                        prop_value,
                    )

    # noinspection PyMethodMayBeStatic
    def _raise_validation_error_for_missing_prop_name(
        self,
        is_missing_otherwise_existing_prop_name: bool,
        collection_name: str,
        prop_name: str,
        curr_sample: dict,
        prev_sample: dict,
    ):
        """
        Raise informative exception for cases of TODO_39_25_11_76: `data_envelope`-s with missing props.
        """

        # It is allowed to have no `prop_name` for all `data_envelope` until at least one has it.
        if is_missing_otherwise_existing_prop_name:
            raise ValueError(
                f"`data_envelope` of `collection_name` [{collection_name}] does not have `prop_name` [{prop_name}] while another one had:\ncurr_sample:\n{curr_sample}\nprev_sample:\n{prev_sample}"
            )
        else:
            raise ValueError(
                f"`data_envelope` of `collection_name` [{collection_name}] has `prop_name` [{prop_name}] while another one did not have:\ncurr_sample:\n{curr_sample}\nprev_sample:\n{prev_sample}"
            )

    def _start_mongo_server(
        self,
    ):
        self.mongo_server.start_mongo_server(self.server_config.mongo_config)

    def _stop_mongo_server(
        self,
    ):
        self.mongo_server.stop_mongo_server()

    # noinspection PyMethodMayBeStatic
    def _populate_func_missing_dynamic_props_(
        self,
        func_envelope_collection: EnvelopeCollection,
        func_index_props: list[str],
    ):
        """
        TODO: TODO_39_25_11_76 missing props: populate missing props supported by funcs.

        This function only targets `ReservedEnvelopeClass.class_function` (because loading funcs is special).
        There is no decision (yet) to populate missing `prop_value`-s for any `data_envelope`.
        Instead, there is a validation to prevent missing `prop_name`-s for other `data_envelope`-s - if it fails,
        the corresponding loader has to be fixed to provide seme set of `prop_name`-s for all `data_envelope`.
        """

        # Populate missing `prop_name`-s with special value:
        for data_envelope in func_envelope_collection.data_envelopes:
            envelope_class = data_envelope[ReservedPropName.envelope_class.name]
            if envelope_class == ReservedEnvelopeClass.class_function.name:
                for prop_name in func_index_props:
                    if prop_name not in data_envelope:
                        data_envelope[prop_name] = SpecialChar.NoPropValue.value

    def _store_mongo_data(
        self,
    ):

        progress_tracker = ProgressTracker()

        # At this moment, funcs have already been loaded on `AbstractPlugin.activate_plugin`.
        func_envelope_collection = EnvelopeCollection(
            collection_name = ReservedEnvelopeClass.class_function.name,
            data_envelopes = self.root_func_loader.get_func_data_envelopes(),
        )
        self._define_func_index_model(
            func_envelope_collection,
        )
        # Initial step: store funcs and any data from config:
        self.store_mongo_data_step(
            # Single `envelope_collection` with `func_data_envelopes`:
            [func_envelope_collection],
            "config_data",
            progress_tracker,
        )

        for plugin_instance_id in self.plugin_config.plugin_instance_id_activate_list:
            if plugin_instance_id in self.server_config.data_loaders:
                plugin_instance = self.server_config.data_loaders[plugin_instance_id]

                # Use loader to define required FS_45_08_22_15 index models.
                index_models: list[IndexModel] = plugin_instance.list_index_models()

                for index_model in index_models:
                    self._define_index_model_step(
                        index_model,
                    )

                # Use loader to update data:
                envelope_collections: list[EnvelopeCollection] = plugin_instance.load_envelope_collections(
                    self.query_engine,
                )

                self.store_mongo_data_step(
                    envelope_collections,
                    plugin_instance_id,
                    progress_tracker,
                )

        self._store_meta_data(
            progress_tracker,
        )

        self._post_validate_stored_data(progress_tracker)

    def _store_meta_data(
        self,
        progress_tracker,
    ):
        """
        This method stores FS_45_08_22_15 index model into data backend.

        The index model (metadata) is used for FS_74_69_61_79 get set data envelope.
        """

        # Add generated `envelope_collection` (itself) for completeness:
        self._define_index_model_step(
            IndexModel(
                collection_name = ReservedEnvelopeClass.class_collection.name,
                index_props = [
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    ReservedPropName.envelope_class.name,
                    ReservedPropName.collection_name.name,
                ],
            ),
        )

        envelope_collection = EnvelopeCollection(
            collection_name = ReservedEnvelopeClass.class_collection.name,
            data_envelopes = []
        )
        for collection_name, index_model in self.index_model_per_collection.items():
            envelope_collection.data_envelopes.append({
                envelope_id_: f"{collection_name}",
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_collection.name,
                # TODO: May add loader plugin instance name as metadata:
                ReservedPropName.collection_name.name: collection_name,
                envelope_payload_: {
                    index_props_: list(index_model.index_props),
                },
            })

        self.store_mongo_data_step(
            [envelope_collection],
            self.__class__.__name__,
            progress_tracker,
        )

    def _define_func_index_model(
        self,
        func_envelope_collection: EnvelopeCollection,
    ):
        """
        Implements FS_45_08_22_15 index model.

        Unlike most of other data, func data is not loaded via loaders and its index model is defined here.
        """

        func_index_props: list[str] = self.root_func_loader.get_func_dynamic_index_props()

        self._populate_func_missing_dynamic_props_(
            func_envelope_collection,
            func_index_props,
        )

        # These added after `_populate_func_missing_dynamic_props_` to ensure that they are populated explicitly.
        # Extend `index_props` for funcs:
        func_index_props.extend([
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            ReservedPropName.envelope_class.name,
            ReservedPropName.func_id.name,
            ReservedPropName.func_state.name,
        ])

        func_index_model: IndexModel = IndexModel(
            collection_name = ReservedEnvelopeClass.class_function.name,
            index_props = func_index_props,
        )

        self._define_index_model_step(func_index_model)

    def _define_index_model_step(
        self,
        given_index_model: IndexModel,
    ):
        """
        Implements internal API for FS_45_08_22_15 index model.

        If there are already existing list of `index_props` per `class_name` per `collection_name`,
        it is possible to call it again, but `index_props` must be exactly the same.
        This is to allow multiple loaders define data they work with,
        but that data definition must match across all loaders working with this type.

        TODO: Limitation: this is append only at the moment
              (you cannot remove added index model - you can only extend or restart server to start over).

        TODO: Expose this via REST API.
        """

        known_index_model: dict[str, IndexModel] = self.index_model_per_collection

        # Ensure `given_index_model` does not redefine `known_index_model` anyhow:
        if given_index_model.collection_name not in known_index_model:
            known_index_model[given_index_model.collection_name] = given_index_model
        else:
            known_index_model = known_index_model[given_index_model.collection_name]
            # Compare L to R:
            for known_index_prop in known_index_model.index_props:
                assert known_index_prop in given_index_model.index_props
            # Compare R to L:
            for given_index_prop in given_index_model.index_props:
                assert given_index_prop in known_index_model.index_props

    def delete_data_envelopes(
        self,
        collection_name: str,
        query_dict: dict,
    ):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]
        MongoClientWrapper.delete_data_envelopes(
            mongo_db,
            collection_name,
            query_dict,
        )

    def store_mongo_data_step(
        self,
        envelope_collections: list[EnvelopeCollection],
        step_name: str,
        progress_tracker: ProgressTracker,
    ):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

        eprint(f"step name: {step_name}:")

        self._pre_validate_static_data_per_step(
            envelope_collections,
            progress_tracker,
        )

        MongoClientWrapper.store_envelopes(
            mongo_db,
            self.cleaned_mongo_collections,
            envelope_collections,
            progress_tracker,
        )

        self._create_mongo_index_step(
            envelope_collections,
        )

    def invalidate_cache_for_collection(
        self,
        collection_name: str,
    ):
        self.query_engine.invalidate_cache_for_collection(collection_name)

    def _create_mongo_index_step(
        self,
        envelope_collections: list[EnvelopeCollection],
    ):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

        for envelope_collection in envelope_collections:
            collection_name = envelope_collection.collection_name

            index_props: list[str] = self.index_model_per_collection[collection_name].index_props

            MongoClientWrapper.create_index(
                mongo_db,
                collection_name,
                index_props,
            )

    def _populate_help_hint_cache(
        self,
    ):
        self.help_hint_cache.populate_cache()

    def _log_connection_url(
        self,
    ):
        host_name = self.server_config.connection_config.server_host_name
        port_number = self.server_config.connection_config.server_port_number
        eprint(f"http://{host_name}:{port_number}")
