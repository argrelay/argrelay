from __future__ import annotations

from typing import Union

from argrelay.composite_forest.CompositeForestExtractor import extract_tree_abs_path_to_interp_id
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker
from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.plugin_delegator.SchemaConfigDelegatorJumpAbstract import (
    abstract_jump_delegator_config_desc,
    single_func_id_,
)
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterp
from argrelay.runtime_data.ServerConfig import ServerConfig


class DelegatorJumpAbstract(DelegatorSingleFuncAbstract):
    """
    This delegator supports functionality of FS_91_88_07_23 jump tree.
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

        # Use configured `single_func_id` to extract all tree paths where it is used:
        extracted_dict = extract_tree_abs_path_to_interp_id(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_config_dict[single_func_id_],
        )
        dict_tree_walker = DictTreeWalker(
            CompositeInfoType.tree_abs_path_to_interp_id,
            extracted_dict,
        )
        # Temporary (reversed) 1-to-N map of id to paths (instead of path to id):
        temporary_id_to_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()

        # Reverse temporary 1-to-N map of id to paths into 1-to-1 map of path to id:
        self.tree_path_to_next_interp_plugin_instance_id: dict[tuple[str, ...], str] = {}
        for interp_factory_instance_id, tree_abs_paths in temporary_id_to_paths.items():
            for tree_abs_path in tree_abs_paths:
                assert tuple(tree_abs_path) not in self.tree_path_to_next_interp_plugin_instance_id
                self.tree_path_to_next_interp_plugin_instance_id[tuple(tree_abs_path)] = interp_factory_instance_id

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return abstract_jump_delegator_config_desc.dict_from_input_dict(plugin_config_dict)

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> Union[None, str]:
        """
        Select next interp for some of the `SpecialFunc`-s:
        *   `SpecialFunc.func_id_intercept_invocation`
        *   `SpecialFunc.func_id_help_hint`
        *   ...

        The next interp selection is a "double jump":
        *   the first "plugin_id" jump here (in delegator) to interp via delegator of the selected func
        *   the second "tree_path" jump there (in jump tree interp) from jump interp to new tree path via jump tree

        This delegator (its `single_func_id`) can be accessed through multiple tree paths.
        Therefore, it should map `interp_tree_abs_path` (how it is accessed) to
        the next `interp_plugin_instance_id` (the single interp).
        """
        if curr_interp.interp_ctx.interp_tree_abs_path in self.tree_path_to_next_interp_plugin_instance_id:
            return self.tree_path_to_next_interp_plugin_instance_id[curr_interp.interp_ctx.interp_tree_abs_path]
        else:
            return None
