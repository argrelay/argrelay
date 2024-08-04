from __future__ import annotations

import contextlib

from argrelay.composite_forest.CompositeForestExtractor import extract_interp_tree
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker, sequence_starts_with
from argrelay.enum_desc.PluginType import PluginType
from argrelay.misc_helper_common import eprint
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.InterpTreeInterp import InterpTreeInterp
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import (
    tree_path_interp_factory_config_desc,
    interp_selector_tree_,
)
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig, assert_plugin_instance_id


class InterpTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_01_89_09_24 interp tree.
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
        self.is_recursive_func_load = False

        self._compare_config_with_composite_forest()

    # TODO: TODO_10_72_28_05: This will go away together with switch to FS_33_76_82_84 composite forest config:
    def _compare_config_with_composite_forest(
        self,
    ):
        expected_dict = self.plugin_config_dict[interp_selector_tree_]
        actual_dict = extract_interp_tree(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_instance_id,
        )
        eprint(f"expected_dict: {expected_dict}")
        eprint(f"actual_dict: {actual_dict}")
        assert expected_dict == actual_dict

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return tree_path_interp_factory_config_desc.dict_from_input_dict(plugin_config_dict)

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor:
        #       At the moment, `InterpTreeInterpFactory` is not plugged into main interp tree -
        #       it is plugged into `first_arg_vals_to_next_interp_factory_ids` of `FirstArgInterpFactory`.
        #
        #       When this func is called for `InterpTreeInterpFactory`, it cannot be found plugged inside
        #       `interp_selector_tree` - instead, it walks the `interp_selector_tree` and
        #       invokes this func for other interps in there.

        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.interp_tree,
            self.plugin_config_dict[interp_selector_tree_],
        )
        # Walk configured interp tree and call `load_interp_tree_abs_paths` with `interp_tree_abs_path` for each interp.
        all_interp_tree_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()
        for interp_factory_instance_id in all_interp_tree_abs_paths:
            assert_plugin_instance_id(
                self.server_config,
                interp_factory_instance_id,
                PluginType.InterpFactoryPlugin,
            )
            interp_factory: AbstractInterpFactory = self.server_config.interp_factories[interp_factory_instance_id]
            interp_factory.load_interp_tree_abs_paths([
                tuple(list_abs_path)
                for list_abs_path in all_interp_tree_abs_paths[interp_factory_instance_id]
            ])

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        with self._is_recursive_load() as is_recursive_load:
            # TODO: FS_33_76_82_84 composite forest: add validation that same interp tree interp is not loaded twice - is it required (given that plugin instances can be reused)?
            if is_recursive_load:
                return []
            return self._load_func_envelopes(
                interp_tree_abs_path,
                func_ids_to_func_envelopes,
            )

    @contextlib.contextmanager
    def _is_recursive_load(self):
        """
        Auto-reset flag `self.is_recursive_func_load` on exit from `with` section.
        """
        try:
            if not self.is_recursive_func_load:
                self.is_recursive_func_load = True
                is_recursive_load = False
            else:
                is_recursive_load = True
            yield is_recursive_load
        finally:
            self.is_recursive_func_load = False

    def _load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        mapped_func_ids: list[str] = super().load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )
        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.interp_tree,
            self.plugin_config_dict[interp_selector_tree_],
        )
        # Walk configured interp tree and call `load_func_envelopes` with `interp_tree_abs_path` for each interp.
        all_interp_tree_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()
        for interp_factory_instance_id in all_interp_tree_abs_paths:
            for sub_interp_tree_abs_path in all_interp_tree_abs_paths[interp_factory_instance_id]:
                if not sequence_starts_with(sub_interp_tree_abs_path, interp_tree_abs_path):
                    # skip: other `interp_tree_abs_path`-s are going to be separate calls to this func:
                    continue
                assert_plugin_instance_id(
                    self.server_config,
                    interp_factory_instance_id,
                    PluginType.InterpFactoryPlugin,
                )
                interp_factory: AbstractInterpFactory = self.server_config.interp_factories[interp_factory_instance_id]

                mapped_func_ids.extend(interp_factory.load_func_envelopes(
                    tuple(sub_interp_tree_abs_path),
                    func_ids_to_func_envelopes,
                ))
        return mapped_func_ids

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> InterpTreeInterp:
        """
        Each `InterpTreeInterpFactory` serves a subtree,
        but it only stores config of per its plug points
        (interp tree abs paths where it was invoked on `load_func_envelopes`).
        If next interp with its plugin id is created, but the specified path is within its subtree,
        chop off the last step in the path until it matches path to its subtree to select one.
        For example:
        ```
        # Current path within interp tree:
        interp_ctx.interp_tree_abs_path = ('l1', 'l2', 'l3', 'l4', )
        # Plug point of this factory within the interp tree:
        self.interp_tree_abs_paths_to_node_configs = {
            ('l1', 'l2', ): {},
            ('x1', 'x2', 'x3', ): {},
        }
        # Keep trying to cut of the last step in the path until it matches one of the key:
        ('l1', 'l2', 'l3', 'l4', )
        ('l1', 'l2', 'l3', )
        ('l1', 'l2', )
        # Done.
        ```
        """
        orig_subtree_abs_path = interp_ctx.interp_tree_abs_path
        curr_subtree_abs_path = orig_subtree_abs_path
        while curr_subtree_abs_path not in self.interp_tree_abs_paths_to_node_configs:
            if len(curr_subtree_abs_path) == 0:
                raise ValueError(
                    f"path `{orig_subtree_abs_path}` is not subpath of `{self.interp_tree_abs_paths_to_node_configs.keys()}` paths"
                )
            curr_subtree_abs_path = curr_subtree_abs_path[:-1]
        return InterpTreeInterp(
            self.plugin_instance_id,
            self.interp_tree_abs_paths_to_node_configs[curr_subtree_abs_path],
            interp_ctx,
        )
