from marshmallow import RAISE, Schema, fields

from argrelay.api_ext.relay_server.AbstractInterpFactory import AbstractInterpFactory
from argrelay.demo_unit.ServiceInterpFactory import ServiceInterpFactory
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_server.call_context import CommandContext
from argrelay.relay_server.line_interp import FirstArgInterp


class FirstArgInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    first_arg_vals_to_next_interp_factory_ids = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


first_arg_interp_config_example = {
    "first_arg_vals_to_next_interp_factory_ids": {
        "some_command": ServiceInterpFactory.__name__,
    },
}

first_arg_interp_config_desc = TypeDesc(
    object_schema = FirstArgInterpConfigSchema(),
    ref_name = FirstArgInterpConfigSchema.__name__,
    dict_example = first_arg_interp_config_example,
    default_file_path = "",
)


class FirstArgInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        first_arg_interp_config_desc.object_schema.validate(config_dict)

    def create_interp(self, command_context: CommandContext) -> FirstArgInterp:
        return FirstArgInterp(command_context, self.config_dict)
