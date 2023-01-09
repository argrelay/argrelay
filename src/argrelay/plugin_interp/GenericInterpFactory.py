from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory
from argrelay.plugin_interp.GenericInterp import GenericInterp
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.GenericInterpConfigSchema import generic_interp_config_desc


class GenericInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        generic_interp_config_desc.dict_schema.validate(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> GenericInterp:
        raise NotImplementedError
