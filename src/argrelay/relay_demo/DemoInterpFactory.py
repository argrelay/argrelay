from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.relay_demo.DemoInterp import DemoInterp
from argrelay.relay_demo.DemoInterpConfigSchema import demo_interp_config_desc
from argrelay.runtime_context.InterpContext import InterpContext


class DemoInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        demo_interp_config_desc.validate_dict(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> DemoInterp:
        return DemoInterp(interp_ctx, self.config_dict)
