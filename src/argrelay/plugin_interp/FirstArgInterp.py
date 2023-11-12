from argrelay.plugin_interp.InterpTreeInterp import InterpTreeInterp
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterp(InterpTreeInterp):
    """
    Dispatch command line interpretation to the next interpreter based on the command_id.

    `FirstArgInterp` was re-implemented in terms of `InterpTreeInterp` (FS_01_89_09_24).

    Implements FS_42_76_93_51 first interp.
    """

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            interp_tree_node_config_dict,
            interp_ctx,
        )
