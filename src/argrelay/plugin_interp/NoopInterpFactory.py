from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.NoopInterp import NoopInterp
from argrelay.runtime_context.InterpContext import InterpContext


class NoopInterpFactory(AbstractInterpFactory):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> NoopInterp:
        # `NoopInterpFactory` is not normally attached to any tree and
        # `load_func_envelopes` is not invoked to clone/populate separate configs
        # (which makes it use `config_dict` directly instead of `interp_tree_node_config_dict`) -
        # use `config_dict` directly if so:
        if interp_ctx.interp_tree_abs_path not in self.interp_tree_abs_paths_to_node_configs:
            config_dict = self.config_dict
        else:
            config_dict = self.interp_tree_abs_paths_to_node_configs[interp_ctx.interp_tree_abs_path]
        return NoopInterp(
            self.plugin_instance_id,
            config_dict,
            interp_ctx,
        )
