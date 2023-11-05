from __future__ import annotations

from argrelay.plugin_interp.FuncTreeInterp import FuncTreeInterp
from argrelay.plugin_interp.InterpTreeContext import InterpTreeContext
from argrelay.runtime_context.InterpContext import InterpContext


class JumpTreeInterp(FuncTreeInterp):

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
        func_paths: dict[str, list[list[str]]],
        path_to_path: dict[tuple[str, ...], tuple[str, ...]],
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
            func_paths,
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = path_to_path

    def select_next_interp_tree_context(self):
        if self.interp_ctx.interp_tree_context.interp_tree_path in self.paths_to_jump:
            # FS_91_88_07_23 jump tree: replace current `interp_tree_path` with another one based on config:
            self.interp_ctx.interp_tree_context = InterpTreeContext(
                interp_tree_path = self.paths_to_jump[self.interp_ctx.interp_tree_context.interp_tree_path],
            )
