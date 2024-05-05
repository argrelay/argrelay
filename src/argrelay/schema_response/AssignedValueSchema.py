from marshmallow import fields, RAISE

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.AssignedValue import AssignedValue

arg_value_ = "arg_value"
arg_source_ = "arg_source"


class AssignedValueSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = AssignedValue

    arg_value = fields.String(
        required = True,
    )

    arg_source = fields.Enum(
        ArgSource,
        by_value = False,
        required = True,
    )


assigned_value_desc = TypeDesc(
    dict_schema = AssignedValueSchema(),
    ref_name = AssignedValueSchema.__name__,
    dict_example = {
        arg_value_: "value_1",
        arg_source_: ArgSource.ImplicitValue.name,
    },
    default_file_path = "",
)
