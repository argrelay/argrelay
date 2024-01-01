from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import (
    first_arg_interp_factory_config_desc,
    first_arg_vals_to_next_interp_factory_ids_,
)
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import (
    tree_path_interp_factory_config_desc,
    interp_selector_tree_,
)
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class FirstArgInterpFactory(InterpTreeInterpFactory):
    """
    `FirstArgInterp` was re-implemented in terms of `InterpTreeInterp` (FS_01_89_09_24).

    Implements FS_42_76_93_51 first interp.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        first_arg_interp_factory_config_desc.validate_dict(plugin_config_dict)
        converted_config = convert_FirstArgInterpConfig_to_InterpTreeInterpFactoryConfig(plugin_config_dict)
        super().__init__(
            server_config,
            plugin_instance_id,
            converted_config,
        )

    def activate_plugin(
        self,
    ):
        """
        # NOTE: FS_42_76_93_51 first interp special case:
        TODO: Think of anther way because `FirstArgInterp` is obsolete - this role here only extends its agony.
        `FirstArgInterp` is used as the root and single instance which
        triggers func loading of itself (and all others recursively).

        Takes part in implementation of FS_01_89_09_24 interp tree.
        """
        interp_tree_abs_path: tuple[str, ...] = tuple([])
        self.load_func_envelopes(
            interp_tree_abs_path,
        )

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> FirstArgInterp:
        return FirstArgInterp(
            self.plugin_instance_id,
            # FS_42_76_93_51 first interp special case:
            # We use multiple config clones (with customization) `tree_node_config_dict` for interps at
            # different location on the FS_01_89_09_24 interp tree - these configs get cloned on `load_func_envelopes`.
            # But first interp is always at the root of the interp tree.
            # More over, first interp is the only one who triggers cascading calls to `load_func_envelopes`,
            # but never receives such call itself.
            # Instead of using `interp_tree_node_config_dict`, use `plugin_config_dict` directly:
            self.plugin_config_dict,
            interp_ctx,
        )


def convert_FirstArgInterpConfig_to_InterpTreeInterpFactoryConfig(
    plugin_config_dict: dict,
) -> dict:
    """
    `FirstArgInterp` was re-implemented in terms of `InterpTreeInterp` (FS_01_89_09_24).
    """
    interp_selector_tree = {}
    for command_id, plugin_instance_id in plugin_config_dict[first_arg_vals_to_next_interp_factory_ids_].items():
        interp_selector_tree[command_id] = plugin_instance_id

    output_dict = {
        interp_selector_tree_: interp_selector_tree
    }

    tree_path_interp_factory_config_desc.validate_dict(output_dict)

    return output_dict
