from marshmallow import Schema, fields, RAISE, post_load, pre_dump

from argrelay.enum_desc.CompType import CompType
from argrelay.misc_helper import ensure_value_is_enum
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_context.RequestContext import RequestContext

command_line_ = "command_line"
cursor_cpos_ = "cursor_cpos"
comp_type_ = "comp_type"
is_debug_enabled_ = "is_debug_enabled"

_sample_command_line = "some_command goto service "

_request_context_example = {
    command_line_: _sample_command_line,
    cursor_cpos_: len(_sample_command_line),
    comp_type_: CompType.PrefixShown.name,
    is_debug_enabled_: True,
}


class RequestContextSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    command_line = fields.String(
        required = True,
        metadata = {
            "example": _request_context_example[command_line_],
        },
    )
    cursor_cpos = fields.Integer(
        required = True,
        metadata = {
            "description": "Cursor position within command line (0 = before the first char)",
            "example": _request_context_example[cursor_cpos_],
        },
    )
    comp_type = fields.Enum(
        CompType,
        required = True,
        metadata = {
            "description": (
                "Name for a completion type - see " + CompType.__name__ + " enum "
                "(which maps into ASCII char sent by Bash to completion callback to indicate completion type)"
            ),
            "example": _request_context_example[comp_type_],
        },
    )
    is_debug_enabled = fields.Boolean(
        required = True,
        metadata = {
            "description": "Enable extra debug output",
            "example": _request_context_example[is_debug_enabled_],
        },
    )

    @pre_dump
    def make_dict(self, input_object: RequestContext, **kwargs):
        # TODO: figure out to populate all automatically and reduce duplication - this is error-prone:
        if isinstance(input_object, RequestContext):
            return {
                command_line_: input_object.command_line,
                cursor_cpos_: input_object.cursor_cpos,
                comp_type_: ensure_value_is_enum(input_object.comp_type, CompType),
                is_debug_enabled_: input_object.is_debug_enabled,
            }
        else:
            # Assuming it is as dict:
            return {
                command_line_: input_object[command_line_],
                cursor_cpos_: input_object[cursor_cpos_],
                comp_type_: ensure_value_is_enum(input_object[comp_type_], CompType),
                is_debug_enabled_: input_object[is_debug_enabled_],
            }

    @post_load
    def make_object(self, input_dict, **kwargs):
        return RequestContext(
            command_line = input_dict[command_line_],
            cursor_cpos = input_dict[cursor_cpos_],
            comp_type = ensure_value_is_enum(input_dict[comp_type_], CompType),
            is_debug_enabled = input_dict[is_debug_enabled_],
        )


request_context_desc = TypeDesc(
    dict_schema = RequestContextSchema(),
    ref_name = RequestContextSchema.__name__,
    dict_example = _request_context_example,
    default_file_path = "",
)
