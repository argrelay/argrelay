from argrelay.data_schema.FirstArgInterpFactorySchema import first_arg_interp_config_desc
from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.interp_plugin.FirstArgInterp import FirstArgInterp
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        first_arg_interp_config_desc.object_schema.validate(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> FirstArgInterp:
        return FirstArgInterp(interp_ctx, self.config_dict)
