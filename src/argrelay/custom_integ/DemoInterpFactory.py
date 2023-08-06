from argrelay.custom_integ.DemoInterp import DemoInterp
from argrelay.custom_integ.DemoInterpFactoryConfigSchema import demo_interp_factory_config_desc
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.runtime_context.InterpContext import InterpContext


class DemoInterpFactory(AbstractInterpFactory):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        demo_interp_factory_config_desc.validate_dict(config_dict)

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> DemoInterp:
        return DemoInterp(
            self.plugin_instance_id,
            self.config_dict,
            interp_ctx,
        )
