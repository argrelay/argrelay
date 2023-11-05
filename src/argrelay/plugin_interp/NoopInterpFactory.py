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
        # `NoopInterpFactory` is not normally attached to any tree and `self.load_func_envelopes`
        # is not invoked to populate separate config (using `self.config_dict` directly) -
        # use `config_dict` directly if so:
        if interp_ctx.interp_tree_context.interp_tree_path not in self.tree_path_config_dict:
            config_dict = self.config_dict
        else:
            config_dict = self.tree_path_config_dict[interp_ctx.interp_tree_context.interp_tree_path]
        return NoopInterp(
            self.plugin_instance_id,
            config_dict,
            interp_ctx,
        )
