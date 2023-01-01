from marshmallow import RAISE, Schema, fields

from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.interp_plugin.FirstArgInterp import FirstArgInterp
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.ServiceInterpFactory import ServiceInterpFactory
from argrelay.runtime_context.InterpContext import InterpContext


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

    def create_interp(self, interp_ctx: InterpContext) -> FirstArgInterp:
        return FirstArgInterp(interp_ctx, self.config_dict)
