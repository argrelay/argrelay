from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.DemoInterpFactory import DemoInterpFactory

first_arg_vals_to_next_interp_factory_ids_ = "first_arg_vals_to_next_interp_factory_ids"


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
    first_arg_vals_to_next_interp_factory_ids_: {
        "some_command": DemoInterpFactory.__name__,
    },
}
first_arg_interp_config_desc = TypeDesc(
    dict_schema = FirstArgInterpConfigSchema(),
    ref_name = FirstArgInterpConfigSchema.__name__,
    dict_example = first_arg_interp_config_example,
    default_file_path = "",
)
