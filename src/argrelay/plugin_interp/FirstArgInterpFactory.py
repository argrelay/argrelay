from __future__ import annotations

from argrelay.composite_forest.CompositeForestExtractor import extract_zero_arg_interp_tree
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import (
    ignored_func_ids_list_,
)
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
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
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )
        # Unlike base `InterpTreeInterpFactory` which uses `CompositeInfoType.interp_tree` for `interp_selector_tree`,
        # `interp_selector_tree` for `FirstArgInterpFactory` is `CompositeInfoType.zero_arg_interp_tree`:
        assert self.interp_selector_tree == {}, "`InterpTreeInterpFactory` is supposed to extract nothing by `plugin_instance_id` for `FirstArgInterpFactory`."
        self.interp_selector_tree = extract_zero_arg_interp_tree(
            server_config.server_plugin_control.composite_forest,
        )

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
                func_id = func_envelope[ReservedPropName.func_id.name]
                if func_id in func_ids_to_func_envelopes:
                    raise RuntimeError(
                        f"plugin_instance_id='{self.plugin_instance_id}': func_id='{func_id}' is published more than once by delegator_plugin_id='{delegator_plugin_id}'"
                    )
                func_ids_to_func_envelopes[func_id] = func_envelope

        self.load_interp_tree_abs_paths([])

        interp_tree_abs_path: tuple[str, ...] = tuple([])
        mapped_func_ids: list[str] = self.load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )

        ignored_func_ids_list = self.plugin_config_dict.get(ignored_func_ids_list_, [])
        for func_id in func_ids_to_func_envelopes.keys():
            # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
            if func_id not in mapped_func_ids:
                if func_id not in ignored_func_ids_list:
                    raise RuntimeError(
                        f"plugin_instance_id=`{self.plugin_instance_id}`: func_id=`{func_id}` is neither mapped anywhere nor is in `{ignored_func_ids_list_}`"
                    )
                else:
                    # This `func_id` is ignored - skip:
                    continue
            else:
                if func_id in ignored_func_ids_list:
                    raise RuntimeError(
                        f"plugin_instance_id=`{self.plugin_instance_id}`: func_id=`{func_id}` is already mapped but still listed in `{ignored_func_ids_list_}`"
                    )
                else:
                    # This `func_id` is mapped - skip:
                    continue

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor:
        #       At the moment, `FirstArgInterpFactory` is not plugged into any tree
        #       (while it should be part of composite forest likely as `CompositeNodeType.zero_arg_node`).
        #       Instead, it is selected via `first_interp_factory_id` in server config.
        #
        #       When this func is called for `FirstArgInterpFactory`, it cannot be found plugged anywhere
        #       within interp tree - instead, it walks the tree and invokes this func for other interps.
        super().load_interp_tree_abs_paths([])

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
            self.interp_selector_tree,
        )
