from marshmallow import Schema, RAISE, fields

from argrelay.api_ext.relay_server.AbstractInterpFactory import AbstractInterpFactory
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_server.call_context import CommandContext
from argrelay.relay_server.line_interp import GenericInterp


class GenericInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    keys_to_types = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


generic_interp_config_example = {
    "keys_to_types": {
        "type_a": "TypeA",
        "type_b": "TypeB",
    },
}

generic_interp_config_desc = TypeDesc(
    object_schema = GenericInterpConfigSchema(),
    ref_name = GenericInterpConfigSchema.__name__,
    dict_example = generic_interp_config_example,
    default_file_path = "",
)


class GenericInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        generic_interp_config_desc.object_schema.validate(config_dict)

    def create_interp(self, command_context: CommandContext) -> GenericInterp:
        raise NotImplementedError
