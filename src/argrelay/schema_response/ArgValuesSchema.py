from marshmallow import Schema, fields, RAISE

from argrelay.misc_helper.TypeDesc import TypeDesc

arg_values_ = "arg_values"

_arg_values_example = {
    arg_values_: [
        "arg_value_1",
        "arg_value_2",
        "arg_value_3",
    ],
}


class ArgValuesSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    arg_values = fields.List(
        fields.String(default = ""),
        default = [],
        metadata = {
            "example": _arg_values_example[arg_values_],
        },
    )


arg_values_desc = TypeDesc(
    dict_schema = ArgValuesSchema(),
    ref_name = ArgValuesSchema.__name__,
    dict_example = _arg_values_example,
    default_file_path = "",
)
