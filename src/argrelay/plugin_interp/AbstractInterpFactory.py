from __future__ import annotations

from copy import deepcopy

from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.AbstractPlugin import AbstractPlugin
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractInterpFactory(AbstractPlugin):

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
        # Takes part in implementation of FS_01_89_09_24 interp tree:
        self.interp_tree_abs_paths_to_node_configs: dict[tuple[str, ...], dict] = {}
        """
        Classes derived from `AbstractInterp` (which are not direct plugins, not configured directly) are created by
        classed derived from `AbstractInterpFactory` (which are plugins with configs).
        Each `AbstractInterp` instance will require its own config called `interp_tree_node_config_dict` which are
        cloned/populated by `load_func_envelopes` and indexed by
        the abs path to the interp tree node in this `interp_tree_abs_paths_to_node_configs`.
        """

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.InterpFactoryPlugin

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        """
        Load func `data_envelope`-s taking into account `interp_tree_abs_path`.

        Takes part in implementation of FS_01_89_09_24 interp tree.

        Returns list of mapped `func_id`-s.
        """
        if interp_tree_abs_path in self.interp_tree_abs_paths_to_node_configs:
            raise RuntimeError(f"`{interp_tree_abs_path}` has already been loaded")
        else:
            self.interp_tree_abs_paths_to_node_configs[interp_tree_abs_path] = deepcopy(self.plugin_config_dict)

        return []

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        raise NotImplementedError
