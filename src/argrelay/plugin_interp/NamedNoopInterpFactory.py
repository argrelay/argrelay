from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.NamedNoopInterp import NamedNoopInterp
from argrelay.runtime_context.InterpContext import InterpContext


class NamedNoopInterpFactory(AbstractInterpFactory):

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
    ) -> NamedNoopInterp:
        return NamedNoopInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )
