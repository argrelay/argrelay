from marshmallow import (
    fields,
    RAISE,
)

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc

prop_value_ = "prop_value"
value_source_ = "value_source"


class AssignedValueSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = AssignedValue

    prop_value = fields.String(
        required = True,
    )

    value_source = fields.Enum(
        ValueSource,
        by_value = False,
        required = True,
    )


assigned_value_desc = TypeDesc(
    dict_schema = AssignedValueSchema(),
    ref_name = AssignedValueSchema.__name__,
    dict_example = {
        prop_value_: "value_1",
        value_source_: ValueSource.implicit_value.name,
    },
    default_file_path = "",
)
