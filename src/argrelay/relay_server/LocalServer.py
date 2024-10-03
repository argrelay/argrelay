from __future__ import annotations

import time
import uuid
from copy import deepcopy

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
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.relay_server.UsageStatsStore import UsageStatsStore
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer, instantiate_server_plugin
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.DataModel import DataModel
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections, index_props_
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_, envelope_payload_, envelope_id_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import search_control_list_
from argrelay.schema_config_interp.SearchControlSchema import (
    keys_to_types_list_,
    collection_name_,
    envelope_class_,
    search_control_desc,
)
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_


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

        # FS_45_08_22_15 data model manipulation:
        # This internal server state is a convenience cache for data model which is also stored in data backend.
        self.data_model_per_class_per_collection: dict[str, dict[str, DataModel]] = {}

        # seconds since epoch:
        self.server_start_time: int = int(time.time())

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
            plugin_entry: PluginEntry = self.plugin_config.plugin_instance_entries[plugin_instance_id]

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
                plugin_instance: AbstractDelegator
                # Store instance of `AbstractDelegator` under specified id for future use:
                self.server_config.action_delegators[plugin_instance_id] = plugin_instance
                continue

            if plugin_type is PluginType.ConfiguratorPlugin:
                plugin_instance: AbstractDelegator
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

    def _pre_validate_static_data_per_step(
        self,
        progress_tracker: ProgressTracker,
    ):
        self._pre_validate_static_data_schema_per_step()
        self._pre_validata_static_data_by_plugins_per_step()
        self._pre_validate_data_envelope_string_index_prop_values_per_step(progress_tracker)

    def _pre_validate_static_data_schema_per_step(
        self,
    ):
        # Note that this is slow for large data sets:
        static_data_dict = static_data_desc.dict_schema.dump(self.server_config.static_data)
        static_data_desc.validate_dict(static_data_dict)

    def _pre_validata_static_data_by_plugins_per_step(
        self,
    ):
        for plugin_instance in self.server_config.plugin_instances.values():
            plugin_instance.validate_loaded_data(self.server_config.static_data)

    def _pre_validate_data_envelope_string_index_prop_values_per_step(
        self,
        progress_tracker: ProgressTracker,
    ):
        """
        This validation ensures there is no blank values (`None`, whitespace, etc.) in `index_prop`-s.

        TODO: TODO_39_25_11_76: `data_envelope`-s with missing props.

        See also FS_99_81_19_25 no space in options.

        See also `_post_validate_all_data_envelope_missing_index_prop_names`.
        """

        for collection_name, envelope_collection in self.server_config.static_data.envelope_collections.items():
            progress_tracker.track_collection_size_increment(
                collection_name,
                len(envelope_collection.data_envelopes),
            )
            for index_prop in envelope_collection.index_props:
                for data_envelope in envelope_collection.data_envelopes:
                    envelope_class = data_envelope[ReservedPropName.envelope_class.name]

                    if index_prop not in data_envelope:
                        # TODO: TODO_39_25_11_76: `data_envelope`-s with missing props:
                        # Let the `data_envelope` load without some `prop_name`-s from `index_prop`-s
                        # in pre-validation - if any of `data_envelope`-s have that `prop_name`, it will fail
                        # in post-validation (see where `_raise_validation_error_for_missing_prop_name` is used).
                        # For now:
                        #     It is allowed to have no `prop_name` for all `data_envelope`
                        #     within given `collection_name` until at least one has it.
                        continue

                    prop_value = data_envelope[index_prop]
                    self._validate_string_prop_value(
                        envelope_class,
                        index_prop,
                        prop_value,
                    )

    def _validate_string_prop_value(
        self,
        envelope_class,
        index_prop,
        prop_value,
    ):
        if isinstance(prop_value, str):
            if not prop_value and prop_value.strip():
                raise ValueError(f"`{envelope_class}.{index_prop}` [{prop_value}] has to be non-blank string")
            if contains_whitespace(prop_value):
                raise ValueError(f"`{envelope_class}.{index_prop}` [{prop_value}] cannot contain whitespace")
        elif isinstance(prop_value, list):
            for prop_value_item in prop_value:
                self._validate_string_prop_value(
                    envelope_class,
                    index_prop,
                    prop_value_item,
                )
        else:
            # FS_06_99_43_60: list arg value:
            raise ValueError(f"`{envelope_class}.{index_prop}` has to be a `list` of `str` or `str`")

    def _post_validate_stored_data(
        self,
        progress_tracker: ProgressTracker,
    ):
        search_props_per_class_per_collection: dict[str, dict[str, set[str]]] = self._scan_for_all_search_props()

        self._post_validate_all_data_envelope_for_missing_index_prop_names(
            search_props_per_class_per_collection,
            progress_tracker,
        )
        self._post_validate_all_data_envelope_for_missing_search_prop_names(
            search_props_per_class_per_collection,
            progress_tracker,
        )

    def _post_validate_all_data_envelope_for_missing_search_prop_names(
        self,
        search_props_per_class_per_collection: dict[str, dict[str, set[str]]],
        progress_tracker: ProgressTracker,
    ):
        """
        See TODO_39_25_11_76 missing props based on `search_control`-s for all loaded functions.

        This function relies on `_post_validate_all_data_envelope_missing_index_prop_names`
        to guarantee that all listed `index_props` exists in every loaded `data_envelope`.
        On top of that fact, this function ensures that every `search_control` used
        specifies `search_props` which exists among `index_props`.
        """

        # TODO: Deduplicate with L <- R:
        # Compare L -> R:
        # Ensure that `data_model` references are used in  some`search_control`.
        for collection_name, data_model_per_class in self.data_model_per_class_per_collection.items():
            for class_name, data_model in data_model_per_class.items():
                if (
                    collection_name not in search_props_per_class_per_collection
                    or
                    class_name not in search_props_per_class_per_collection[collection_name]
                ):
                    progress_tracker.track_unused_index_props_per_collection_unused_by_search_control(
                        collection_name,
                        class_name,
                        # all are unused:
                        data_model.index_props,
                    )
                else:
                    search_props = search_props_per_class_per_collection[collection_name][class_name]
                    unused_index_props = []
                    for index_prop in data_model.index_props:
                        if index_prop not in search_props:
                            unused_index_props.append(index_prop)
                    if len(unused_index_props) > 0:
                        progress_tracker.track_unused_index_props_per_collection_unused_by_search_control(
                            collection_name,
                            class_name,
                            # unused are selected only:
                            unused_index_props,
                        )

        # TODO: Deduplicate with L -> R:
        # Compare L <- R:
        # Ensure that every `search_prop` is among the `index_prop`-s in `data_model`:
        for collection_name, search_props_per_class in search_props_per_class_per_collection.items():
            for class_name, search_props in search_props_per_class.items():
                if (
                    collection_name not in self.data_model_per_class_per_collection
                    or
                    class_name not in self.data_model_per_class_per_collection[collection_name]
                ):
                    progress_tracker.track_dangling_search_props_per_collection_undefined_by_data_model(
                        collection_name,
                        class_name,
                        # all are dangling:
                        search_props,
                    )
                else:
                    search_props = search_props_per_class_per_collection[collection_name][class_name]
                    index_props = self.data_model_per_class_per_collection[collection_name][class_name].index_props
                    dangling_search_props = []
                    for search_prop in search_props:
                        if search_prop not in index_props:
                            dangling_search_props.append(search_prop)
                    if len(dangling_search_props) > 0:
                        progress_tracker.track_dangling_search_props_per_collection_undefined_by_data_model(
                            collection_name,
                            class_name,
                            # dangling are selected only:
                            dangling_search_props,
                        )

    def _scan_for_all_search_props(
        self,
    ) -> dict[str, dict[str, set[str]]]:
        """
        Build search prop names per (2-level map) `collection_name` and `envelope_class`
        by scanning `search_control`-s for `prop_name`-s.
        """

        search_props_per_class_per_collection: dict[str, dict[str, set[str]]] = {}

        # TODO: TODO_08_25_32_95: redesign `class_to_collection_map`:
        # NOTE: Server config may not configure all mappings from `class_name`-s to `collection_name`-s.
        #       It only configures overrides (and, by default, `collection_name` matches `class_name`).
        #       Instead, to have full picture, build mappings based on stored data.
        assert self.server_config.class_to_collection_map is not None
        # Build `full_class_to_collection_map`:
        full_class_to_collection_map: dict[str, str] = {}
        for collection_name, data_model_per_class in self.data_model_per_class_per_collection.items():
            for class_name in data_model_per_class:
                if class_name in full_class_to_collection_map:
                    # Each `class_name` should be mapped to the same `collection_name`:
                    assert full_class_to_collection_map[class_name] == collection_name
                else:
                    full_class_to_collection_map[class_name] = collection_name

        plugin_search_controls: list[SearchControl] = []
        for plugin_instance in self.server_config.plugin_instances.values():
            plugin_search_controls.extend(plugin_instance.provide_plugin_search_control())

        # Scan `search_control`-s of all plugins:
        for search_control in plugin_search_controls:
            self._populate_search_props_per_class_per_collection(
                search_control_desc.dict_from_input_obj(search_control),
                search_props_per_class_per_collection,
            )

        # Scan `search_control`-s of all funcs:
        for func_envelope in self.query_engine.get_data_envelopes_cursor(
            full_class_to_collection_map[ReservedEnvelopeClass.ClassFunction.name],
            {
                f"{ReservedPropName.envelope_class.name}": f"{ReservedEnvelopeClass.ClassFunction.name}",
            },
        ):
            for search_control in func_envelope[instance_data_][search_control_list_]:
                self._populate_search_props_per_class_per_collection(
                    search_control,
                    search_props_per_class_per_collection,
                )

        return search_props_per_class_per_collection

    def _populate_search_props_per_class_per_collection(
        self,
        search_control: dict,
        search_props_per_class_per_collection,
    ):
        search_collection_name = search_control[collection_name_]
        search_class_name = search_control[envelope_class_]

        search_props_name_per_class = search_props_per_class_per_collection.setdefault(
            search_collection_name,
            {},
        )
        search_props = search_props_name_per_class.setdefault(
            search_class_name,
            set()
        )

        # TODO: TODO_66_66_75_78.split_arg_and_prop_concepts: Rename: `arg_type` to `prop_name`:
        for key_to_value_dict in search_control[keys_to_types_list_]:
            assert type(key_to_value_dict) is dict
            assert len(key_to_value_dict) == 1
            search_prop_name = next(iter(key_to_value_dict.values()))
            search_props.add(search_prop_name)

    def _post_validate_all_data_envelope_for_missing_index_prop_names(
        self,
        search_props_per_class_per_collection: dict[str, dict[str, set[str]]],
        progress_tracker: ProgressTracker,
    ):
        """
        See TODO_39_25_11_76 missing props based on `index_prop`-s per `envelope_collection`.

        See also:
        *   `_pre_validate_data_envelope_string_index_prop_values_per_step`
        *   `_post_validate_all_data_envelope_missing_search_prop_names`
        """

        progress_tracker.track_total_validation_start()

        # Verify that all prop names per (2-level map) `collection_name` and `envelope_class`
        # exists in all corresponding `data_envelope`-s:
        for collection_name, data_model_per_class in self.data_model_per_class_per_collection.items():
            progress_tracker.track_collection_validation_start(collection_name)

            prev_found_missing_prop_names: dict[str, dict] = {}
            prev_found_existing_prop_names: dict[str, dict] = {}
            for data_envelope in self.query_engine.get_data_envelopes_cursor(
                collection_name,
                {},
            ):
                progress_tracker.track_collection_validation_increment(collection_name)

                envelope_class = data_envelope[ReservedPropName.envelope_class.name]
                assert envelope_class in data_model_per_class

                for prop_name in data_model_per_class[envelope_class].index_props:
                    if prop_name not in data_envelope:

                        if prop_name not in prev_found_missing_prop_names:
                            prev_found_missing_prop_names[prop_name] = deepcopy(data_envelope)

                        if prop_name in prev_found_existing_prop_names:
                            self._raise_validation_error_for_missing_prop_name(
                                True,
                                collection_name,
                                envelope_class,
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
                                envelope_class,
                                prop_name,
                                data_envelope,
                                prev_found_missing_prop_names[prop_name],
                            )
                        prop_value = data_envelope[prop_name]
                        self._validate_string_prop_value(
                            envelope_class,
                            prop_name,
                            prop_value,
                        )

            progress_tracker.track_collection_validation_stop(collection_name)

        progress_tracker.track_total_validation_stop()

    # noinspection PyMethodMayBeStatic
    def _raise_validation_error_for_missing_prop_name(
        self,
        is_missing_otherwise_existing_prop_name: bool,
        collection_name: str,
        envelope_class: str,
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
                f"data_envelope of (collection_name: `{collection_name}`, envelope_class: `{envelope_class}`) does not have (prop_name: `{prop_name}`) while another one had:\ncurr_sample:\n{curr_sample}\nprev_sample:\n{prev_sample}"
            )
        else:
            raise ValueError(
                f"data_envelope of (collection_name: `{collection_name}`, envelope_class: `{envelope_class}`) has (prop_name: `{prop_name}`) while another one did not have:\ncurr_sample:\n{curr_sample}\nprev_sample:\n{prev_sample}"
            )

    def _start_mongo_server(
        self,
    ):
        self.mongo_server.start_mongo_server(self.server_config.mongo_config)

    def _stop_mongo_server(
        self,
    ):
        self.mongo_server.stop_mongo_server()

    def _populate_func_missing_props(
        self,
    ):
        """
        TODO: TODO_39_25_11_76 missing props: populate missing props supported by funcs.

        This function only targets `ReservedEnvelopeClass.ClassFunction` (because loading funcs is special).
        There is no decision (yet) to populate missing `prop_value`-s for any `data_envelope`.
        Instead, there is a validation to prevent missing `prop_name`-s for other `data_envelope`-s - if it fails,
        the corresponding loader has to be fixed to provide seme set of `prop_name`-s for all `data_envelope`.
        """

        # NOTE: There is actually only one `envelope_collection` (even if we loop):
        assert len(self.server_config.static_data.envelope_collections) == 1
        assert (
            self._get_collection_name(ReservedEnvelopeClass.ClassFunction.name)
            in
            self.server_config.static_data.envelope_collections
        )

        # Collect `prop_name`-s used by all funcs:
        func_prop_names: set[str] = set()
        for mongo_collection in self.server_config.static_data.envelope_collections:
            envelope_collection: EnvelopeCollection = self.server_config.static_data.envelope_collections[
                mongo_collection
            ]
            for data_envelope in envelope_collection.data_envelopes:
                envelope_class = data_envelope[ReservedPropName.envelope_class.name]
                if envelope_class == ReservedEnvelopeClass.ClassFunction.name:
                    for prop_name in envelope_collection.index_props:
                        func_prop_names.add(prop_name)

        # Populate missing `prop_name`-s with special value:
        for mongo_collection in self.server_config.static_data.envelope_collections:
            envelope_collection: EnvelopeCollection = self.server_config.static_data.envelope_collections[
                mongo_collection
            ]
            for data_envelope in envelope_collection.data_envelopes:
                envelope_class = data_envelope[ReservedPropName.envelope_class.name]
                if envelope_class == ReservedEnvelopeClass.ClassFunction.name:
                    for prop_name in func_prop_names:
                        if prop_name not in data_envelope:
                            data_envelope[prop_name] = SpecialChar.NoPropValue.value

    def _get_collection_name(
        self,
        class_name,
    ):
        if class_name in self.server_config.class_to_collection_map:
            return self.server_config.class_to_collection_map[class_name]
        else:
            return ReservedEnvelopeClass.ClassFunction.name

    def _store_mongo_data(
        self,
    ):

        progress_tracker = ProgressTracker()

        # At this moment, funcs have already been loaded on `AbstractPlugin.activate_plugin`.
        self._populate_func_missing_props()
        self._define_func_data_model()

        # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`:
        # Initial step: store funcs and any data from config:
        self._store_mongo_data_step(
            "config_data",
            progress_tracker,
        )

        for plugin_instance_id in self.plugin_config.plugin_instance_id_activate_list:
            if plugin_instance_id in self.server_config.data_loaders:
                plugin_instance = self.server_config.data_loaders[plugin_instance_id]

                # Each step starts with empty `static_data`:
                self.server_config.static_data = StaticData(
                    envelope_collections = {},
                )

                # Use loader to define required FS_45_08_22_15 data models.
                data_models: list[DataModel] = plugin_instance.list_data_models()

                # Use loader to update data:
                self.server_config.static_data = plugin_instance.update_static_data(
                    self.server_config.static_data,
                    self.query_engine,
                )

                for data_model in data_models:
                    self._define_data_model_step(
                        data_model,
                    )

                self._store_mongo_data_step(
                    plugin_instance_id,
                    progress_tracker,
                )

        self._store_data_model(
            progress_tracker,
        )

        self._post_validate_stored_data(progress_tracker)

    def _store_data_model(
        self,
        load_state,
    ):
        """
        This method stores FS_45_08_22_15 data model into data backend.

        The data model (metadata) is used for FS_74_69_61_79 get set data envelope.
        """

        # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`:
        #       This is a hack - it restores test assumption that last loaded `static_data` can be inspected.
        #       See `test_loader` in `test_GitRepoLoader_offline.py`.
        prev_static_data = self.server_config.static_data

        # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`:
        # TODO: Instead of populating `static_data` (temporary approach to load all data),
        #       the FS_45_08_22_15 data model manipulation API will have to update data backend itself.
        # Each step starts with empty `static_data`:
        self.server_config.static_data = StaticData(
            envelope_collections = {},
        )

        class_names = [
            ReservedEnvelopeClass.ClassCollectionMeta.name,
        ]
        # Init index fields (if they do not exist):
        collection_meta_index_props = [
            ReservedPropName.collection_name.name,
            ReservedPropName.envelope_class.name,
        ]
        init_envelop_collections(
            self.server_config.class_to_collection_map,
            self.server_config.static_data.envelope_collections,
            class_names,
            lambda collection_name, class_name: collection_meta_index_props,
        )

        collection_meta_envelopes = self.server_config.static_data.envelope_collections[
            self.server_config.class_to_collection_map[ReservedEnvelopeClass.ClassCollectionMeta.name]
        ].data_envelopes

        # Add generated `envelope_collection` (itself) for completeness:
        self._define_data_model_step(
            DataModel(
                collection_name = ReservedEnvelopeClass.ClassCollectionMeta.name,
                class_name = ReservedEnvelopeClass.ClassCollectionMeta.name,
                index_props = collection_meta_index_props,
            ),
        )

        for collection_name, data_model_per_class in self.data_model_per_class_per_collection.items():
            for class_name, data_model in data_model_per_class.items():
                assert ReservedPropName.envelope_class.name in data_model.index_props
                collection_meta_envelopes.append({
                    envelope_id_: f"{collection_name}:{class_name}",
                    ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassCollectionMeta.name,
                    # TODO: May add loader plugin instance name as metadata:
                    ReservedPropName.collection_name.name: collection_name,
                    envelope_payload_: {
                        index_props_: list(data_model.index_props),
                        data_envelopes_: [],
                    },
                })

        self._store_mongo_data_step(
            self.__class__.__name__,
            load_state,
        )

        # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`:
        #       This is a hack - it restores test assumption that last loaded `static_data` can be inspected.
        #       See `test_loader` in `test_GitRepoLoader_offline.py`.
        self.server_config.static_data = prev_static_data

    def _define_func_data_model(
        self,
    ):
        """
        Implements FS_45_08_22_15 data model manipulation.

        Unlike most of other data, func data is not loaded via loaders and its data model is defined here.
        """

        # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`
        #       At the moment, this func has to be called after loading func data into `static_data`.
        #       Specifically, we use `server_config.static_data.envelope_collections` for
        #       `ReservedEnvelopeClass.ClassFunction.name` to get all `index_props`.
        #       Later, it will be called internally while creating funcs data.

        func_collection = self.server_config.static_data.envelope_collections[
            # TODO: TODO_08_25_32_95: redesign `class_to_collection_map`:
            #       Using `DataModel` should eliminate the need for `class_to_collection_map`:
            self.server_config.class_to_collection_map[ReservedEnvelopeClass.ClassFunction.name]
        ]

        # Extend `index_props` for funcs:
        func_index_props = deepcopy(func_collection.index_props)
        func_index_props.extend([
            ReservedPropName.func_id.name,
            ReservedPropName.func_state.name,
        ])

        func_data_model: DataModel = DataModel(
            collection_name = ReservedEnvelopeClass.ClassFunction.name,
            class_name = ReservedEnvelopeClass.ClassFunction.name,
            index_props = func_index_props,
        )

        self._define_data_model_step(func_data_model)

    def _define_data_model_step(
        self,
        given_data_model: DataModel,
    ):
        """
        Implements internal API for FS_45_08_22_15 data model manipulation.

        If there are already existing list of `index_props` per `class_name` per `collection_name`,
        it is possible to call it again, but `index_props` must be exactly the same.
        This is to allow multiple loaders define data they work with,
        but that data definition must match across all loaders working with this type.

        TODO: Limitation: this is append only at the moment
              (you cannot remove added data model - you can only extend or restart server to start over).

        TODO: Expose this via REST API.
        """

        known_data_models: dict[str, DataModel] = self.data_model_per_class_per_collection.setdefault(
            given_data_model.collection_name,
            {},
        )

        # It is fine not to list `ReservedPropName.envelope_class` as it is implied by `DataModel.class_name`.
        # But it has to be present for search:
        if ReservedPropName.envelope_class.name not in given_data_model.index_props:
            given_data_model.index_props.append(ReservedPropName.envelope_class.name)

        # Ensure `given_data_model` does not redefine `known_data_models` anyhow:
        if given_data_model.class_name not in known_data_models:
            known_data_models[given_data_model.class_name] = given_data_model
        else:
            known_data_model = known_data_models[given_data_model.class_name]
            # Compare L to R:
            for known_index_prop in known_data_model.index_props:
                assert known_index_prop in given_data_model.index_props
            # Compare R to L:
            for given_index_prop in given_data_model.index_props:
                assert given_index_prop in known_data_model.index_props

    def _store_mongo_data_step(
        self,
        step_name: str,
        progress_tracker: ProgressTracker,
    ):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

        eprint(f"step name: {step_name}:")

        self._pre_validate_static_data_per_step(progress_tracker)

        MongoClientWrapper.store_envelopes(
            mongo_db,
            self.cleaned_mongo_collections,
            # TODO: TODO_00_79_72_55: Remove `static_data` from `server_config`:
            self.server_config.static_data,
            progress_tracker,
        )

        self._create_mongo_index_step()

    def _create_mongo_index_step(
        self,
    ):
        mongo_db = self.mongo_client[self.server_config.mongo_config.mongo_server.database_name]

        for collection_name in self.server_config.static_data.envelope_collections:
            envelope_collection: EnvelopeCollection = self.server_config.static_data.envelope_collections[
                collection_name
            ]
            # Include `envelope_class` field into index by default:
            index_props: list[str] = deepcopy(envelope_collection.index_props)
            index_props.append(ReservedPropName.envelope_class.name)
            MongoClientWrapper.create_index(
                mongo_db,
                collection_name,
                envelope_collection.index_props,
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
