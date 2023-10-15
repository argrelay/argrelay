from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.JumpTreeInterp import JumpTreeInterp
from argrelay.plugin_interp.JumpTreeInterpFactoryConfigSchema import (
    jump_tree_interp_config_desc,
    jump_tree_,
)
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.runtime_context.InterpContext import InterpContext


class JumpTreeInterpFactory(FuncTreeInterpFactory):
    """
    Implements FS_91_88_07_23 jump tree.
    """

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        # FS_91_88_07_23 jump tree
        tree_walker: TreeWalker = TreeWalker(
            "jump",
            self.config_dict[jump_tree_],
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = tree_walker.build_paths_to_paths()

    def validate_config(
        self,
    ):
        jump_tree_interp_config_desc.validate_dict(self.config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        return JumpTreeInterp(
            self.plugin_instance_id,
            self.tree_path_config_dict[interp_ctx.interp_tree_context.interp_tree_path],
            interp_ctx,
            self.func_paths,
            self.paths_to_jump,
        )
