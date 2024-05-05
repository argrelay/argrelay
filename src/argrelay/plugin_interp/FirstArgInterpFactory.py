from argrelay.composite_tree.CompositeTreeWalker import extract_zero_arg_interp_tree
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper_common import eprint
from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import (
    first_arg_interp_factory_config_desc,
    first_arg_vals_to_next_interp_factory_ids_,
    ignored_func_ids_list_,
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

    # TODO_10_72_28_05: This will go away together with switch to FS_33_76_82_84 composite tree config:
    def _compare_config_with_composite_tree(
        self,
    ):
        expected_dict = self.plugin_config_dict[interp_selector_tree_]
        actual_dict = extract_zero_arg_interp_tree(
            self.server_config.server_plugin_control.composite_forest,
        )
        eprint(f"expected_dict: {expected_dict}")
        eprint(f"actual_dict: {actual_dict}")
        assert expected_dict == actual_dict

    def activate_plugin(
        self,
    ) -> None:
        """
        # NOTE: FS_42_76_93_51 first interp special case:
        TODO: Think of anther way because `FirstArgInterp` is obsolete - this role here only extends its agony.
        `FirstArgInterp` is used as the root and single instance which
        triggers func loading of itself (and all others recursively).

        Takes part in implementation of FS_01_89_09_24 interp tree.
        """

        # Build a map from `func_id` to `func_envelope`:
        func_ids_to_func_envelopes: dict[str, dict] = {}
        for delegator_plugin_id, action_delegator in self.server_config.action_delegators.items():
            func_envelopes = action_delegator.get_supported_func_envelopes()
            for func_envelope in func_envelopes:
                func_id = func_envelope[ReservedArgType.FuncId.name]
                if func_id in func_ids_to_func_envelopes:
                    raise RuntimeError(
                        f"plugin_instance_id='{self.plugin_instance_id}': func_id='{func_id}' is published more than once by delegator_plugin_id='{delegator_plugin_id}'"
                    )
                func_ids_to_func_envelopes[func_id] = func_envelope

        interp_tree_abs_path: tuple[str, ...] = tuple([])
        mapped_func_ids: list[str] = self.load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )

        ignored_func_ids_list = self.plugin_config_dict.get(ignored_func_ids_list_, [])
        for func_id in func_ids_to_func_envelopes.keys():
            if func_id not in mapped_func_ids:
                if func_id not in ignored_func_ids_list:
                    raise RuntimeError(
                        f"plugin_instance_id='{self.plugin_instance_id}': func_id='{func_id}' is neither mapped anywhere nor is in `{ignored_func_ids_list_}`"
                    )
                else:
                    # Func is ignored - skip:
                    continue

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
        interp_selector_tree_: interp_selector_tree,
        ignored_func_ids_list_: plugin_config_dict.get(ignored_func_ids_list_, []),
    }

    tree_path_interp_factory_config_desc.validate_dict(output_dict)

    return output_dict
