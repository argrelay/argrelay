from __future__ import annotations

from copy import deepcopy

from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.FuncArgsInterp import func_init_control_, func_search_control_
from argrelay.plugin_interp.FuncArgsInterpFactory import FuncArgsInterpFactory
from argrelay.plugin_interp.FuncArgsInterpFactoryConfigSchema import (
    delegator_plugin_ids_,
    func_selector_tree_,
    ignored_func_ids_list_,
)
from argrelay.plugin_interp.FuncTreeInterp import FuncTreeInterp
from argrelay.plugin_interp.InterpTreeContext import InterpTreeContext
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig, assert_plugin_instance_id
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_, envelope_class_

tree_path_selector_prefix_ = "tree_path_selector_"
tree_path_selector_key_prefix_ = "s"


# TODO: At the moment `FuncTreeInterpFactory` derives from `FuncArgsInterpFactory`,
#       but it is conceptually confusing because `FuncTree` interp never interprets `FuncArgs`.
#       Introduce common base class?
class FuncTreeInterpFactory(FuncArgsInterpFactory):
    """
    Implements FS_26_43_73_72 func tree.
    """

    def load_func_envelopes(
        self,
        interp_tree_context: InterpTreeContext,
        server_config: ServerConfig,
    ):
        """
        To implement FS_26_43_73_72 func tree, this plugin loads func `data_envelope`-s automatically.

        It queries `delegator_plugin_ids` to retrieve func `data_envelope`-s and populates their search props
        by inspecting configured `func_selector_tree` where each function is plugged into.

        TODO: It should fail if function does not exists in `func_selector_tree` and `ignore_functions` list.

        TODO: It should fail if function exists in `func_selector_tree` but was never found in loaded func envelopes.

        """
        super().load_func_envelopes(
            interp_tree_context,
            server_config,
        )
        interp_tree_path = interp_tree_context.interp_tree_path
        context_config = self.tree_path_config_dict[interp_tree_path]

        func_tree_walker = TreeWalker(
            "func",
            context_config[func_selector_tree_],
        )
        self.func_paths: dict[str, list[list[str]]] = func_tree_walker.build_str_leaves_paths()

        # Retrieve func `data_envelope`-s from all delegators:
        func_envelopes_index: dict[str, dict[tuple[str, ...], dict]] = {}
        for delegator_plugin_id in context_config[delegator_plugin_ids_]:
            assert_plugin_instance_id(
                server_config,
                delegator_plugin_id,
                PluginType.DelegatorPlugin,
            )
            action_delegator: AbstractDelegator = server_config.action_delegators[delegator_plugin_id]
            func_envelopes = action_delegator.get_supported_func_envelopes()
            for func_envelope in func_envelopes:
                func_id = func_envelope[ReservedArgType.FuncId.name]
                if func_id not in self.func_paths:
                    if func_id not in context_config[ignored_func_ids_list_]:
                        raise RuntimeError(
                            f"`{func_id}` is neither in `{func_selector_tree_}` nor in `{ignored_func_ids_list_}`"
                        )
                    else:
                        # Func is ignored - skip:
                        continue
                if func_id not in func_envelopes_index:
                    func_envelopes_index[func_id] = {}
                for func_path in self.func_paths[func_id]:
                    assert tuple(func_path) not in func_envelopes_index[func_id]
                    func_envelopes_index[func_id][tuple(func_path)] = deepcopy(func_envelope)

        self.populate_init_control(
            interp_tree_path,
            context_config,
        )

        self.populate_search_control(
            interp_tree_path,
            context_config,
        )

        interp_tree_path_func_envelopes: list[dict] = self.populate_func_tree_props(
            interp_tree_path,
            context_config,
            func_envelopes_index,
        )

        # Write func envelopes into `StaticData` (as if it is a loader plugin):
        server_config.static_data.data_envelopes.extend(interp_tree_path_func_envelopes)

    # noinspection PyMethodMayBeStatic
    def populate_init_control(
        self,
        interp_tree_path: tuple[str, ...],
        context_config: dict,
    ):
        context_config[func_init_control_] = {
            init_types_to_values_: {},
        }

        init_types_to_values = context_config[func_init_control_][init_types_to_values_]
        for sel_ipos, path_step in enumerate(interp_tree_path):
            init_types_to_values[f"{func_envelope_path_step_prop_name(sel_ipos)}"] = path_step

    def populate_search_control(
        self,
        interp_tree_path: tuple[str, ...],
        context_config,
    ):
        """
        Provide search control based on `func_paths`.
        """
        context_config[func_search_control_] = {
            envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
            keys_to_types_list_: [],
        }

        # `func_search_control` should include keys from the context provided by interp tree:
        keys_to_types_list = context_config[func_search_control_][keys_to_types_list_]

        # Include interp tree path:
        base_sel_ipos = 0
        for offset_sel_ipos in range(len(interp_tree_path)):
            sel_ipos = base_sel_ipos + offset_sel_ipos
            keys_to_types_list.append({
                f"{path_step_key_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

        # Include func tree path:
        base_sel_ipos = len(interp_tree_path)
        max_len = max_path_len(self.func_paths)
        for offset_sel_ipos in range(max_len):
            sel_ipos = base_sel_ipos + offset_sel_ipos
            keys_to_types_list.append({
                f"{path_step_key_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

    def populate_func_tree_props(
        self,
        interp_tree_path: tuple[str, ...],
        context_config,
        func_envelopes_index: dict[str, dict[tuple[str, ...], dict]],
    ) -> list[dict]:
        """
        Populates func tree properties for each func `data_envelope` based on its path in func tree.

        For each func envelope:
        *   Select its place on the func tree (provided by plugin config).
        *   Populate the path as envelope props with `tree_path_selector_prefix_`.
        """
        interp_tree_path_func_envelopes = []
        for func_id in self.func_paths:
            func_paths_list: list[list[str]] = self.func_paths[func_id]

            for func_path in func_paths_list:

                func_envelope = func_envelopes_index[func_id][tuple(func_path)]

                # Include interp tree path:
                base_sel_ipos = 0
                for offset_sel_ipos, path_step_id in enumerate(interp_tree_path):
                    sel_ipos = base_sel_ipos + offset_sel_ipos
                    prop_name = func_envelope_path_step_prop_name(sel_ipos)
                    func_envelope[prop_name] = path_step_id

                # Include func tree path:
                base_sel_ipos = len(interp_tree_path)
                for offset_sel_ipos, path_step_id in enumerate(func_path):
                    sel_ipos = base_sel_ipos + offset_sel_ipos
                    prop_name = func_envelope_path_step_prop_name(sel_ipos)
                    func_envelope[prop_name] = path_step_id

                interp_tree_path_func_envelopes.append(func_envelope)

        return interp_tree_path_func_envelopes

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        return FuncTreeInterp(
            self.plugin_instance_id,
            self.tree_path_config_dict[interp_ctx.interp_tree_context.interp_tree_path],
            interp_ctx,
            self.func_paths,
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
    func_paths: dict[str, list[list[str]]],
):
    """
    Find maximum path length.
    """
    max_len: int = 0
    for func_paths_list in func_paths.values():
        for func_path in func_paths_list:
            max_len = max(max_len, len(func_path))
    return max_len
