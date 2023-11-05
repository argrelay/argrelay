import contextlib

from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.InterpTreeContext import InterpTreeContext
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
        interp_tree_context: InterpTreeContext,
        server_config: ServerConfig,
    ):
        with self._is_recursive_load() as is_recursive_load:
            if is_recursive_load:
                return
            self._load_func_envelopes(
                interp_tree_context,
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
        interp_tree_context: InterpTreeContext,
        server_config: ServerConfig,
    ):
        super().load_func_envelopes(
            interp_tree_context,
            server_config,
        )
        tree_walker: TreeWalker = TreeWalker(
            "interp",
            self.config_dict[interp_selector_tree_],
        )
        # Walk configured interp tree and call `load_func_envelopes` with `InterpTreeContext` for each interp.
        interp_paths: dict[str, list[list[str]]] = tree_walker.build_str_leaves_paths()
        for interp_plugin_id in interp_paths:
            for interp_path in interp_paths[interp_plugin_id]:
                assert_plugin_instance_id(
                    server_config,
                    interp_plugin_id,
                    PluginType.InterpFactoryPlugin,
                )
                interp_factory: AbstractInterpFactory = server_config.interp_factories[interp_plugin_id]
                sub_context: InterpTreeContext = InterpTreeContext(
                    interp_tree_path = interp_tree_context.interp_tree_path + tuple(interp_path)
                )

                interp_factory.load_func_envelopes(
                    sub_context,
                    server_config,
                )

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> InterpTreeInterp:
        """
        Each `InterpTreeInterpFactory` serves a subtree,
        but it only stores config of per its plug points
        (interp tree paths where it was invoked on func load).
        If next interp with its plugin id is created, but the specified path is within its subtree,
        chop off the last step in the path until it matches path to its subtree.
        """
        mine_subtree_paths = self.tree_path_config_dict.keys()
        orig_subtree_path = interp_ctx.interp_tree_context.interp_tree_path
        curr_subtree_path = orig_subtree_path
        while curr_subtree_path not in mine_subtree_paths:
            if len(curr_subtree_path) == 0:
                raise ValueError(
                    f"path `{curr_subtree_path}` is not subpath of `{mine_subtree_paths}` paths"
                )
            curr_subtree_path = orig_subtree_path[:-1]
        return InterpTreeInterp(
            self.plugin_instance_id,
            self.tree_path_config_dict[curr_subtree_path],
            interp_ctx,
        )
