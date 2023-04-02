from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import (
    first_arg_interp_factory_config_desc,
    first_arg_vals_to_next_interp_factory_ids_,
)
from argrelay.plugin_interp.TreePathInterpFactory import TreePathInterpFactory
from argrelay.plugin_interp.TreePathInterpFactoryConfigSchema import (
    tree_path_interp_factory_config_desc,
    interp_selector_tree_,
)
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterpFactory(TreePathInterpFactory):
    """
    `FirstArgInterp` was re-implemented in terms of `TreePathInterp` (FS_01_89_09_24).

    Implements FS_42_76_93_51.
    """

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        first_arg_interp_factory_config_desc.validate_dict(config_dict)
        converted_config = convert_FirstArgInterpConfig_to_TreePathInterpFactoryConfig(config_dict)
        tree_path_interp_factory_config_desc.validate_dict(converted_config)
        super().__init__(
            plugin_instance_id,
            converted_config,
        )


    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> FirstArgInterp:
        return FirstArgInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )

def convert_FirstArgInterpConfig_to_TreePathInterpFactoryConfig(config_dict: dict) -> dict:
    """
    `FirstArgInterp` was re-implemented in terms of `TreePathInterp` (FS_01_89_09_24).
    """
    interp_selector_tree = {}
    for command_id, plugin_instance_id in config_dict[first_arg_vals_to_next_interp_factory_ids_].items():
        interp_selector_tree[command_id] = plugin_instance_id

    output_dict = {
        interp_selector_tree_: interp_selector_tree
    }

    tree_path_interp_factory_config_desc.validate_dict(output_dict)

    return output_dict
