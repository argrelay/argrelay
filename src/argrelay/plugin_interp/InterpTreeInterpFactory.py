from __future__ import annotations

import contextlib

from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.InterpTreeInterp import InterpTreeInterp
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import (
    tree_path_interp_factory_config_desc,
    interp_selector_tree_,
)
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig, assert_plugin_instance_id


class InterpTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_01_89_09_24 interp tree.
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
        self.is_recursive_func_load = False

    def validate_config(
        self,
    ):
        tree_path_interp_factory_config_desc.validate_dict(self.config_dict)

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        server_config: ServerConfig,
    ):
        with self._is_recursive_load() as is_recursive_load:
            if is_recursive_load:
                return
            self._load_func_envelopes(
                interp_tree_abs_path,
                server_config,
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
        server_config: ServerConfig,
    ):
        super().load_func_envelopes(
            interp_tree_abs_path,
            server_config,
        )
        tree_walker: TreeWalker = TreeWalker(
            "interp",
            self.config_dict[interp_selector_tree_],
        )
        # Walk configured interp tree and call `load_func_envelopes` with `interp_tree_abs_path` for each interp.
        interp_rel_paths: dict[str, list[list[str]]] = tree_walker.build_str_leaves_paths()
        for interp_plugin_id in interp_rel_paths:
            for interp_rel_path in interp_rel_paths[interp_plugin_id]:
                assert_plugin_instance_id(
                    server_config,
                    interp_plugin_id,
                    PluginType.InterpFactoryPlugin,
                )
                interp_factory: AbstractInterpFactory = server_config.interp_factories[interp_plugin_id]
                sub_interp_tree_abs_path = interp_tree_abs_path + tuple(interp_rel_path)

                interp_factory.load_func_envelopes(
                    sub_interp_tree_abs_path,
                    server_config,
                )

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
