from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_vals_to_next_interp_factory_ids_
from argrelay.plugin_interp.TreePathInterp import TreePathInterp
from argrelay.plugin_interp.TreePathInterpFactoryConfigSchema import interp_selector_tree_, \
    tree_path_interp_factory_config_desc
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterp(TreePathInterp):
    """
    Dispatch command line interpretation to the next interpreter based on the command_id.

    `FirstArgInterp` was re-implemented in terms of `TreePathInterp` (FS_01_89_09_24).

    Implements FS_42_76_93_51.
    """

    command_name: str

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
