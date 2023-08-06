from argrelay.plugin_interp.TreePathInterp import TreePathInterp
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterp(TreePathInterp):
    """
    Dispatch command line interpretation to the next interpreter based on the command_id.

    `FirstArgInterp` was re-implemented in terms of `TreePathInterp` (FS_01_89_09_24).

    Implements FS_42_76_93_51.
    """

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
        )
