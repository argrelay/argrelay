from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc


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
