from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.FirstArgInterp import FirstArgInterp
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_core_server.FirstArgInterpFactorySchema import first_arg_interp_config_desc


class FirstArgInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        first_arg_interp_config_desc.validate_dict(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> FirstArgInterp:
        return FirstArgInterp(interp_ctx, self.config_dict)
