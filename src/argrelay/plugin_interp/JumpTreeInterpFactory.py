from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.JumpTreeInterp import JumpTreeInterp
from argrelay.plugin_interp.JumpTreeInterpFactoryConfigSchema import (
    jump_tree_interp_config_desc,
    jump_tree_,
)
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class JumpTreeInterpFactory(FuncTreeInterpFactory):
    """
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
        # FS_91_88_07_23 jump tree
        tree_walker: TreeWalker = TreeWalker(
            "jump_tree",
            self.plugin_config_dict[jump_tree_],
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = tree_walker.build_paths_to_paths()
        """
        Implements FS_91_88_07_23 jump tree:
        for given `interp_tree_abs_path` (FS_01_89_09_24) selects next `interp_tree_abs_path`.
        """

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        # TODO_74_03_78_60: Call `TypeDesc` API to do load (to populate defaults) -> dump automatically.
        return jump_tree_interp_config_desc.dict_schema.dump(
            jump_tree_interp_config_desc.dict_schema.load(
                plugin_config_dict
            )
        )

    def validate_config(
        self,
    ):
        jump_tree_interp_config_desc.validate_dict(self.plugin_config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        return JumpTreeInterp(
            self.plugin_instance_id,
            self.interp_tree_abs_paths_to_node_configs[interp_ctx.interp_tree_abs_path],
            interp_ctx,
            self.func_ids_to_func_rel_paths,
            self.paths_to_jump,
        )
