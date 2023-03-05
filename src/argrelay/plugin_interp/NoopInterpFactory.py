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
        return NoopInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )
