from argrelay.data_schema.GenericInterpConfigSchema import generic_interp_config_desc
from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.interp_plugin.GenericInterp import GenericInterp
from argrelay.runtime_context.InterpContext import InterpContext


class GenericInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        generic_interp_config_desc.object_schema.validate(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> GenericInterp:
        raise NotImplementedError
