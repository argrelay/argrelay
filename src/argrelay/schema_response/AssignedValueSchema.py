from marshmallow import Schema, fields, RAISE, post_load, pre_dump

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.misc_helper_common import ensure_value_is_enum
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.AssignedValue import AssignedValue

arg_value_ = "arg_value"
arg_source_ = "arg_source"


class AssignedValueSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    arg_value = fields.String(
        required = True,
    )

    arg_source = fields.Enum(
        ArgSource,
        by_value = False,
        required = True,
    )

    @pre_dump
    def make_dict(
        self,
        input_object: AssignedValue,
        **kwargs,
    ):
        return {
            arg_value_: input_object.arg_value,
            arg_source_: ensure_value_is_enum(input_object.arg_source, ArgSource),
        }

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return AssignedValue(
            arg_value = input_dict[arg_value_],
            arg_source = ensure_value_is_enum(input_dict[arg_source_], ArgSource),
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
