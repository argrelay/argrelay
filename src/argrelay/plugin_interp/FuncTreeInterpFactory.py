from __future__ import annotations

from copy import deepcopy

from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.FuncTreeInterp import FuncTreeInterp, func_init_control_, func_search_control_
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import (
    delegator_plugin_ids_,
    func_selector_tree_,
    ignored_func_ids_list_,
    func_tree_interp_config_desc,
)
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig, assert_plugin_instance_id
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_
from argrelay.schema_config_interp.SearchControlSchema import (
    keys_to_types_list_,
    populate_search_control,
)

tree_path_selector_prefix_ = "tree_path_selector_"
tree_path_selector_key_prefix_ = "s"


class FuncTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_26_43_73_72 func tree.
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
        # FS_26_43_73_72 func tree: func id to list of its relative paths populated by `load_func_envelopes`.
        # These func tree paths are relative to the interp node within FS_01_89_09_24 interp tree
        # (as fully qualified func path is composed of interp tree path where this plugin instance is attached to).
        # Each func id can be attached to more than one leaf (hence, there is a list of paths to that func id).
        self.func_ids_to_func_rel_paths: dict[str, list[list[str]]] = {}

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        # TODO_74_03_78_60: Call `TypeDesc` API to do load (to populate defaults) -> dump automatically.
        return func_tree_interp_config_desc.dict_schema.dump(
            func_tree_interp_config_desc.dict_schema.load(
                plugin_config_dict
            )
        )

    def validate_config(
        self,
    ):
        func_tree_interp_config_desc.validate_dict(self.plugin_config_dict)

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
    ):
        """
        To implement FS_26_43_73_72 func tree, this plugin loads func `data_envelope`-s automatically.

        It queries `delegator_plugin_ids` to retrieve func `data_envelope`-s and populates their search props
        by inspecting configured `func_selector_tree` where each function is plugged into.

        TODO: It should fail if function does not exists in `func_selector_tree` and `ignore_functions` list.

        TODO: It should fail if function exists in `func_selector_tree` but was never found in loaded func envelopes.

        """
        super().load_func_envelopes(
            interp_tree_abs_path,
        )
        interp_tree_node_config_dict = self.interp_tree_abs_paths_to_node_configs[interp_tree_abs_path]

        func_tree_walker = TreeWalker(
            "func_tree",
            interp_tree_node_config_dict[func_selector_tree_],
        )
        self.func_ids_to_func_rel_paths: dict[str, list[list[str]]] = func_tree_walker.build_str_leaves_paths()

        # Retrieve func `data_envelope`-s from all delegators:
        func_envelopes_index: dict[str, dict[tuple[str, ...], dict]] = {}
        for delegator_plugin_id in interp_tree_node_config_dict[delegator_plugin_ids_]:
            assert_plugin_instance_id(
                self.server_config,
                delegator_plugin_id,
                PluginType.DelegatorPlugin,
            )
            action_delegator: AbstractDelegator = self.server_config.action_delegators[delegator_plugin_id]
            func_envelopes = action_delegator.get_supported_func_envelopes()
            for func_envelope in func_envelopes:
                func_id = func_envelope[ReservedArgType.FuncId.name]
                if func_id not in self.func_ids_to_func_rel_paths:
                    if func_id not in interp_tree_node_config_dict[ignored_func_ids_list_]:
                        raise RuntimeError(
                            f"plugin_instance_id='{self.plugin_instance_id}': func_id='{func_id}' is neither in `{func_selector_tree_}` nor in `{ignored_func_ids_list_}`"
                        )
                    else:
                        # Func is ignored - skip:
                        continue
                if func_id not in func_envelopes_index:
                    func_envelopes_index[func_id] = {}
                for func_rel_path in self.func_ids_to_func_rel_paths[func_id]:
                    assert tuple(func_rel_path) not in func_envelopes_index[func_id]
                    func_envelopes_index[func_id][tuple(func_rel_path)] = deepcopy(func_envelope)

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
            func_envelopes_index,
        )

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        class_names = [
            ReservedEnvelopeClass.ClassFunction.name,
        ]
        init_envelop_collections(
            self.server_config,
            class_names,
            lambda collection_name, class_name: [
                ReservedArgType.EnvelopeClass.name,
            ] + prop_names
        )
        envelope_collection = self.server_config.static_data.envelope_collections[
            class_to_collection_map[ReservedEnvelopeClass.ClassFunction.name]
        ]
        # Write func envelopes into `StaticData` (as if it is a loader plugin):
        envelope_collection.data_envelopes.extend(interp_tree_abs_path_func_envelopes)

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
        Provide search control based on `func_ids_to_func_rel_paths`.
        """

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        interp_tree_node_config_dict[func_search_control_] = populate_search_control(
            class_to_collection_map,
            ReservedEnvelopeClass.ClassFunction.name,
            [],
        )

        # `func_search_control` should include keys from the interp tree abs path:
        keys_to_types_list = interp_tree_node_config_dict[func_search_control_][keys_to_types_list_]

        # Include interp tree path:
        base_sel_ipos = 0
        for offset_sel_ipos in range(len(interp_tree_abs_path)):
            sel_ipos = base_sel_ipos + offset_sel_ipos
            keys_to_types_list.append({
                f"{path_step_key_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

        # Include func tree path:
        base_sel_ipos = len(interp_tree_abs_path)
        max_len = max_path_len(self.func_ids_to_func_rel_paths)
        for offset_sel_ipos in range(max_len):
            sel_ipos = base_sel_ipos + offset_sel_ipos
            keys_to_types_list.append({
                f"{path_step_key_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

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
        for func_id in self.func_ids_to_func_rel_paths:
            func_rel_paths: list[list[str]] = self.func_ids_to_func_rel_paths[func_id]

            for func_rel_path in func_rel_paths:

                func_envelope = func_envelopes_index[func_id][tuple(func_rel_path)]

                # Include interp tree path:
                base_sel_ipos = 0
                for offset_sel_ipos, path_step_id in enumerate(interp_tree_abs_path):
                    sel_ipos = base_sel_ipos + offset_sel_ipos
                    prop_name = func_envelope_path_step_prop_name(sel_ipos)
                    func_envelope[prop_name] = path_step_id
                    prop_names.append(prop_name)

                # Include func tree path:
                base_sel_ipos = len(interp_tree_abs_path)
                for offset_sel_ipos, path_step_id in enumerate(func_rel_path):
                    sel_ipos = base_sel_ipos + offset_sel_ipos
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
            self.func_ids_to_func_rel_paths,
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
    func_ids_to_func_rel_paths: dict[str, list[list[str]]],
):
    """
    Find maximum path length.
    """
    max_len: int = 0
    for func_rel_paths in func_ids_to_func_rel_paths.values():
        for func_rel_path in func_rel_paths:
            max_len = max(max_len, len(func_rel_path))
    return max_len
