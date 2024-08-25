from __future__ import annotations

from typing import Union

from argrelay.composite_forest.CompositeForestExtractor import extract_tree_abs_path_to_interp_id
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_delegator.AbstractJumpDelegatorConfigSchema import (
    abstract_jump_delegator_config_desc,
    single_func_id_,
)
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterp
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractJumpDelegator(AbstractDelegator):

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

        extracted_dict = extract_tree_abs_path_to_interp_id(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_config_dict[single_func_id_],
        )
        dict_tree_walker = DictTreeWalker(
            CompositeInfoType.tree_abs_path_to_interp_id,
            extracted_dict,
        )
        # Temporary (reversed) map which contains path per id (instead of id per path):
        temporary_id_to_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()

        # Reverse temporary path per id map into id per path map:
        self.tree_path_to_next_interp_plugin_instance_id: dict[tuple[str, ...], str] = {}
        for interp_factory_instance_id, tree_abs_paths in temporary_id_to_paths.items():
            for tree_abs_path in tree_abs_paths:
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
        # TODO_10_72_28_05: support special funcs for all commands:
        #                   Delegator must select next `interp_factory_id` based on `interp_tree_abs_path` via `tree_abs_path_to_interp_id` (not based on single plugin id specified)
        #                   because delegator can be accessible through multiple tree paths.
        #                   Delegator should map specific tree path using the tree path they are accessed through to specific `interp_plugin_instance_id`.
        #                   The next interp selection is a double jump:
        #                   *   the first jump here (in delegator) is based on selected func via its delegator to interp,
        #                   *   the second jump there (in jump tree interp) from jump interp via jump tree.
        # TODO: This must be special interpreter which is configured only to search functions (without their args).
        #       NEXT TODO: Why not support function args for special interp (e.g. `intercept` or `help` with format params)?
        #                  The interp_control is only run when func and all its args are selected and there should be next interp to continue.
        if curr_interp.interp_ctx.interp_tree_abs_path in self.tree_path_to_next_interp_plugin_instance_id:
            return self.tree_path_to_next_interp_plugin_instance_id[curr_interp.interp_ctx.interp_tree_abs_path]
        else:
            return None
