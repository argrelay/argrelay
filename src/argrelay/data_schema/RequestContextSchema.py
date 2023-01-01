from marshmallow import Schema, fields, RAISE, post_load

from argrelay.meta_data.CompType import CompType
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_context.RequestContext import RequestContext

_request_context_example = {
    "command_line": "some_command prod",
    "cursor_cpos": str(16),
    "comp_type": CompType.PrefixShown.name,
    "is_debug_enabled": True,
}


class RequestContextSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    command_line = fields.String(
        required = True,
        metadata = {
            "example": _request_context_example["command_line"],
        },
    )
    cursor_cpos = fields.Integer(
        required = True,
        metadata = {
            "example": _request_context_example["cursor_cpos"],
        },
    )
    comp_type = fields.Enum(
        CompType,
        required = True,
        metadata = {
            "example": _request_context_example["comp_type"],
        },
    )
    is_debug_enabled = fields.Boolean(
        required = True,
        metadata = {
            "example": _request_context_example["is_debug_enabled"],
        },
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return RequestContext(
            command_line = input_dict["command_line"],
            cursor_cpos = input_dict["cursor_cpos"],
            comp_type = input_dict["comp_type"],
            is_debug_enabled = input_dict["is_debug_enabled"],
        )


request_context_desc = TypeDesc(
    object_schema = RequestContextSchema(),
    ref_name = RequestContextSchema.__name__,
    dict_example = _request_context_example,
    default_file_path = "",
)
