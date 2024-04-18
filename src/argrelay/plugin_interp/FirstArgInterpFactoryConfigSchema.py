from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import ignored_func_ids_list_

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

    # TODO: FS_42_76_93_51: See todo on the same field in `InterpTreeInterpFactoryConfigSchema`:
    ignored_func_ids_list = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )


first_arg_interp_factory_config_example = {
    first_arg_vals_to_next_interp_factory_ids_: {
        "some_command": InterpTreeInterpFactory.__name__,
    },
    ignored_func_ids_list_: [
        "some_ignored_func",
    ],
}
first_arg_interp_factory_config_desc = TypeDesc(
    dict_schema = FirstArgInterpFactoryConfigSchema(),
    ref_name = FirstArgInterpFactoryConfigSchema.__name__,
    dict_example = first_arg_interp_factory_config_example,
    default_file_path = "",
)
