from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.NoopInterp import NoopInterp
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class NoopInterpFactory(AbstractInterpFactory):

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

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> NoopInterp:
        # `NoopInterpFactory` is not normally attached to any tree and
        # `load_func_envelopes` is not invoked to clone/populate separate configs
        # (which makes it use `plugin_config_dict` directly instead of `interp_tree_node_config_dict`) -
        # use `plugin_config_dict` directly if so:
        if interp_ctx.interp_tree_abs_path not in self.interp_tree_abs_paths_to_node_configs:
            plugin_config_dict = self.plugin_config_dict
        else:
            plugin_config_dict = self.interp_tree_abs_paths_to_node_configs[interp_ctx.interp_tree_abs_path]
        return NoopInterp(
            self.plugin_instance_id,
            plugin_config_dict,
            interp_ctx,
        )
