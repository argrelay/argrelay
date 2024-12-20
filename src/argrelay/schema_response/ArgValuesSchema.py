from marshmallow import fields, RAISE

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_response.ArgValues import ArgValues

arg_values_ = "arg_values"

_arg_values_example = {
    arg_values_: [
        "arg_value_1",
        "arg_value_2",
        "arg_value_3",
    ],
}


class ArgValuesSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ArgValues

    arg_values = fields.List(
        fields.String(
            load_default = "",
        ),
        load_default = [],
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
