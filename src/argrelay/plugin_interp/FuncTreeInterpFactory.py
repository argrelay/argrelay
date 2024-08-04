from __future__ import annotations

from copy import deepcopy
from typing import Union

from argrelay.composite_forest.CompositeForestExtractor import extract_jump_tree, extract_func_tree
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker, normalize_tree, sequence_starts_with
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common import eprint
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.FuncTreeInterp import FuncTreeInterp, func_init_control_, func_search_control_
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import (
    func_selector_tree_,
    func_tree_interp_config_desc,
    jump_tree_,
)
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_
from argrelay.schema_config_interp.SearchControlSchema import (
    keys_to_types_list_,
    populate_search_control,
    search_control_desc,
)
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_enabled_, plugin_dependencies_

tree_path_selector_prefix_ = "tree_path_selector_"
tree_path_selector_key_prefix_ = "s"


class FuncTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_26_43_73_72 func tree.
    Implements FS_91_88_07_23 jump tree.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

        self._compare_config_with_composite_forest()

        # FS_26_43_73_72 func tree: func id to list of its absolute paths populated by `load_func_envelopes`.
        # These func tree paths are absolute within FS_33_76_82_84 composite forest.
        # Each func id can be attached to more than one leaf (hence, there is a list of paths to that func id).
        self.func_ids_to_func_abs_paths: dict[str, list[list[str]]] = {}

        # FS_91_88_07_23 jump tree
        self.plugin_config_dict.setdefault(jump_tree_, {})
        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.jump_tree,
            self.plugin_config_dict[jump_tree_],
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = dict_tree_walker.build_paths_to_paths()
        """
        Implements FS_91_88_07_23 jump tree:
        for given `interp_tree_abs_path` (FS_01_89_09_24) selects next `interp_tree_abs_path`.
        """

        self.plugin_search_control: Union[SearchControl, None] = None

    # TODO: TODO_10_72_28_05: This will go away together with switch to FS_33_76_82_84 composite forest config:
    def _compare_config_with_composite_forest(
        self,
    ):
        expected_dict = self.plugin_config_dict[jump_tree_]
        actual_dict = extract_jump_tree(
            self.server_config.server_plugin_control.composite_forest,
        )
        eprint(f"expected_dict: {expected_dict}")
        eprint(f"actual_dict: {actual_dict}")
        assert expected_dict == actual_dict

    # TODO: TODO_10_72_28_05: This will go away together with switch to FS_33_76_82_84 composite forest config:
    def _compare_config_with_composite_forest_func_tree(
        self,
        expected_func_selector_tree_dict: dict,
    ):
        expected_dict = normalize_tree(expected_func_selector_tree_dict)
        actual_dict = normalize_tree(extract_func_tree(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_instance_id,
        ))
        eprint(f"expected_dict: {expected_dict}")
        eprint(f"actual_dict: {actual_dict}")
        assert expected_dict == actual_dict

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return func_tree_interp_config_desc.dict_from_input_dict(plugin_config_dict)

    def provide_plugin_search_control(
        self,
    ) -> list[SearchControl]:
        if self.plugin_search_control:
            return [self.plugin_search_control]
        else:
            return []

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        self.interp_tree_abs_paths.extend(
            this_plugin_instance_interp_tree_abs_paths,
        )

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        """
        To implement FS_26_43_73_72 func tree, this plugin loads func `data_envelope`-s automatically.

        It loops through func `data_envelope`-s and populates their tree path search props
        according to configured `func_selector_tree` where each function is plugged into.
        """

        mapped_func_ids: list[str] = super().load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )
        interp_tree_node_config_dict = self.interp_tree_abs_paths_to_node_configs[interp_tree_abs_path]

        self._compare_config_with_composite_forest_func_tree(
            interp_tree_node_config_dict[func_selector_tree_],
        )

        dict_tree_walker = DictTreeWalker(
            CompositeInfoType.func_tree,
            interp_tree_node_config_dict[func_selector_tree_],
        )
        self.func_ids_to_func_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()

        # `func_envelope` (2-level map) per `func_id` per `func_abs_path`
        func_id_to_func_abs_path_to_func_envelope: dict[str, dict[tuple[str, ...], dict]] = {}
        # Loop through func `data_envelope`-s from all delegators:
        for func_id, func_envelope in func_ids_to_func_envelopes.items():
            if func_id not in self.func_ids_to_func_abs_paths:
                # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
                # This `func_id` is not plugged into given tree.
                # It will be loaded as `FuncState.fs_unplugged`.
                continue
            func_abs_paths = self.func_ids_to_func_abs_paths[func_id]
            for func_abs_path in func_abs_paths:
                assert (
                    func_id not in func_id_to_func_abs_path_to_func_envelope
                    or
                    tuple(func_abs_path) not in func_id_to_func_abs_path_to_func_envelope[func_id]
                )
                if self._is_best_matching_abs_tree_path(func_abs_path, interp_tree_abs_path):
                    # This `func_id` is mapped into the `func_tree` under this plugin:
                    func_id_to_func_abs_path_to_func_envelope.setdefault(
                        func_id,
                        {},
                    )[tuple(func_abs_path)] = deepcopy(func_envelope)
                    mapped_func_ids.append(func_id)

        # Ensure every `func_id` mapped into the tree is part of `func_envelope`-s loaded from delegators:
        for func_id in self.func_ids_to_func_abs_paths.keys():
            if func_id not in mapped_func_ids:
                raise RuntimeError(
                    f"plugin_instance_id=`{self.plugin_instance_id}`: func_id=`{func_id}` is not published by any enabled delegator activated so far - please check `{plugin_enabled_}` and `{plugin_dependencies_}`"
                )

        self.populate_func_envelope_collection(
            func_id_to_func_abs_path_to_func_envelope,
            interp_tree_abs_path,
            interp_tree_node_config_dict,
        )

        return mapped_func_ids

    def populate_func_envelope_collection(
        self,
        func_id_to_func_abs_path_to_func_envelope: dict[str, dict[tuple[str, ...], dict]],
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict,
    ):
        self.populate_init_control(
            interp_tree_abs_path,
            interp_tree_node_config_dict,
        )
        self.populate_search_control(
            interp_tree_abs_path,
            interp_tree_node_config_dict,
        )
        (
            interp_tree_abs_path_func_envelopes,
            prop_names,
        ) = self.populate_func_tree_props(
            interp_tree_abs_path,
            interp_tree_node_config_dict,
            func_id_to_func_abs_path_to_func_envelope,
        )
        class_to_collection_map: dict = self.server_config.class_to_collection_map
        class_names = [
            ReservedEnvelopeClass.ClassFunction.name,
        ]
        init_envelop_collections(
            self.server_config,
            class_names,
            lambda collection_name, class_name: (
                [
                    ReservedPropName.envelope_class.name,
                ] + prop_names
            )
        )
        envelope_collection = self.server_config.static_data.envelope_collections[
            class_to_collection_map[ReservedEnvelopeClass.ClassFunction.name]
        ]
        # Write func envelopes into `StaticData` (as if it is a loader plugin):
        envelope_collection.data_envelopes.extend(interp_tree_abs_path_func_envelopes)

    def _is_best_matching_abs_tree_path(
        self,
        func_abs_path,
        given_interp_tree_abs_path,
    ) -> bool:
        if sequence_starts_with(func_abs_path, given_interp_tree_abs_path):
            best_matching_abs_tree_path = given_interp_tree_abs_path
            max_matched_len = len(best_matching_abs_tree_path)
            for interp_tree_abs_path in self.interp_tree_abs_paths:
                if given_interp_tree_abs_path == interp_tree_abs_path:
                    continue
                if sequence_starts_with(func_abs_path, interp_tree_abs_path):
                    if max_matched_len < len(interp_tree_abs_path):
                        best_matching_abs_tree_path = interp_tree_abs_path
                        max_matched_len = len(best_matching_abs_tree_path)
                        break
                    elif max_matched_len == len(interp_tree_abs_path):
                        # There should not be two plugin paths leading to the same func:
                        raise RuntimeError()
                    else:
                        continue
            return given_interp_tree_abs_path == best_matching_abs_tree_path
        else:
            return False

    # noinspection PyMethodMayBeStatic
    def populate_init_control(
        self,
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict: dict,
    ):
        interp_tree_node_config_dict[func_init_control_] = {
            init_types_to_values_: {},
        }

        init_types_to_values = interp_tree_node_config_dict[func_init_control_][init_types_to_values_]
        for sel_ipos, path_step in enumerate(interp_tree_abs_path):
            init_types_to_values[f"{func_envelope_path_step_prop_name(sel_ipos)}"] = path_step

    def populate_search_control(
        self,
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict,
    ):
        """
        Provide `func_search_control` based on `func_ids_to_func_abs_paths`.
        """

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        plugin_search_control_dict: dict = populate_search_control(
            class_to_collection_map,
            ReservedEnvelopeClass.ClassFunction.name,
            [],
        )

        # `func_search_control` should include keys from the interp tree abs path:
        keys_to_types_list = plugin_search_control_dict[keys_to_types_list_]

        # Include func tree path:
        max_len = max_path_len(self.func_ids_to_func_abs_paths)
        for sel_ipos in range(max_len):
            keys_to_types_list.append({
                f"{path_step_key_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

        # Include other fields:
        keys_to_types_list.append({
            "state": ReservedPropName.func_state.name
        })
        keys_to_types_list.append({
            "id": ReservedPropName.func_id.name
        })

        interp_tree_node_config_dict[func_search_control_] = plugin_search_control_dict
        self.plugin_search_control = search_control_desc.obj_from_input_dict(plugin_search_control_dict)

    def populate_func_tree_props(
        self,
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict,
        func_envelopes_index: dict[str, dict[tuple[str, ...], dict]],
    ) -> tuple[list[dict], list[str]]:
        """
        Populates func tree properties for each func `data_envelope` based on its path in func tree.

        For each func envelope:
        *   Select its place on the func tree (provided by plugin config).
        *   Populate the path as envelope props with `tree_path_selector_prefix_`.
        """
        interp_tree_abs_path_func_envelopes: list[dict] = []
        prop_names: list[str] = []
        for func_id in self.func_ids_to_func_abs_paths:
            func_abs_paths: list[list[str]] = self.func_ids_to_func_abs_paths[func_id]

            for func_abs_path in func_abs_paths:

                if (
                    func_id not in func_envelopes_index
                    or
                    tuple(func_abs_path) not in func_envelopes_index[func_id]
                ):
                    continue

                func_envelope = func_envelopes_index[func_id][tuple(func_abs_path)]

                # Include func tree path:
                for sel_ipos, path_step_id in enumerate(func_abs_path):
                    prop_name = func_envelope_path_step_prop_name(sel_ipos)
                    func_envelope[prop_name] = path_step_id
                    prop_names.append(prop_name)

                interp_tree_abs_path_func_envelopes.append(func_envelope)

        return (
            interp_tree_abs_path_func_envelopes,
            prop_names,
        )

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        return FuncTreeInterp(
            self.plugin_instance_id,
            self.interp_tree_abs_paths_to_node_configs[interp_ctx.interp_tree_abs_path],
            interp_ctx,
            self.func_ids_to_func_abs_paths,
            self.paths_to_jump,
        )


def func_envelope_path_step_prop_name(
    path_step_ipos: int,
) -> str:
    return f"{tree_path_selector_prefix_}{path_step_ipos}"


def path_step_key_arg_name(
    path_step_ipos: int,
) -> str:
    return f"{tree_path_selector_key_prefix_}{path_step_ipos}"


def max_path_len(
    func_ids_to_func_abs_paths: dict[str, list[list[str]]],
):
    """
    Find maximum path length.
    """
    max_len: int = 0
    for func_rel_paths in func_ids_to_func_abs_paths.values():
        for func_rel_path in func_rel_paths:
            max_len = max(max_len, len(func_rel_path))
    return max_len
