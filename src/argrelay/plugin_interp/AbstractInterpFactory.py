from copy import deepcopy

from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.InterpTreeContext import InterpTreeContext
from argrelay.runtime_context.AbstractPlugin import AbstractPlugin
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractInterpFactory(AbstractPlugin):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        # Takes part in implementation of FS_01_89_09_24 interp tree:
        # TODO: rename to interp_tree_path_config_dicts:
        self.tree_path_config_dict: dict[tuple[str, ...], dict] = {}

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.InterpFactoryPlugin

    def load_func_envelopes(
        self,
        interp_tree_context: InterpTreeContext,
        server_config: ServerConfig,
    ):
        """
        Load func `data_envelope`-s taking into account `InterpTreeContext`.

        Takes part in implementation of FS_01_89_09_24 interp tree.
        """
        interp_tree_path = interp_tree_context.interp_tree_path
        if interp_tree_path in self.tree_path_config_dict:
            raise RuntimeError(f"`{interp_tree_path}` has already been loaded")
        else:
            self.tree_path_config_dict[interp_tree_path] = deepcopy(self.config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        raise NotImplementedError
