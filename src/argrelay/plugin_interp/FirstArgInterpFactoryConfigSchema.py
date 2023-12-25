from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory

first_arg_vals_to_next_interp_factory_ids_ = "first_arg_vals_to_next_interp_factory_ids"


class FirstArgInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    first_arg_vals_to_next_interp_factory_ids = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


first_arg_interp_factory_config_example = {
    first_arg_vals_to_next_interp_factory_ids_: {
        "some_command": InterpTreeInterpFactory.__name__,
    },
}
first_arg_interp_factory_config_desc = TypeDesc(
    dict_schema = FirstArgInterpFactoryConfigSchema(),
    ref_name = FirstArgInterpFactoryConfigSchema.__name__,
    dict_example = first_arg_interp_factory_config_example,
    default_file_path = "",
)
