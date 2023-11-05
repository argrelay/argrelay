from __future__ import annotations

from argrelay.plugin_interp.FuncTreeInterp import FuncTreeInterp
from argrelay.runtime_context.InterpContext import InterpContext


class JumpTreeInterp(FuncTreeInterp):

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
        func_ids_to_func_rel_paths: dict[str, list[list[str]]],
        paths_to_jump: dict[tuple[str, ...], tuple[str, ...]],
    ):
        super().__init__(
            interp_factory_id,
            interp_tree_node_config_dict,
            interp_ctx,
            func_ids_to_func_rel_paths,
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = paths_to_jump

    def select_next_interp_tree_abs_path(self):
        if self.interp_ctx.interp_tree_abs_path in self.paths_to_jump:
            # FS_91_88_07_23 jump tree: replace current `interp_tree_abs_path` with another one based on config:
            self.interp_ctx.interp_tree_abs_path = self.paths_to_jump[self.interp_ctx.interp_tree_abs_path]
