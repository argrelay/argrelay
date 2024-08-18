from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import ignored_func_ids_list_


class FirstArgInterpFactoryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    # TODO: FS_42_76_93_51: See todo on the same field in `InterpTreeInterpFactoryConfigSchema`:
    ignored_func_ids_list = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )


first_arg_interp_factory_config_example = {
    ignored_func_ids_list_: [
        "func_id_some_ignored",
    ],
}
first_arg_interp_factory_config_desc = TypeDesc(
    dict_schema = FirstArgInterpFactoryConfigSchema(),
    ref_name = FirstArgInterpFactoryConfigSchema.__name__,
    dict_example = first_arg_interp_factory_config_example,
    default_file_path = "",
)
