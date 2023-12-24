from marshmallow import Schema, fields, RAISE, post_load, pre_dump

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common import ensure_value_is_enum
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.server_spec.CallContext import CallContext

server_action_ = "server_action"
command_line_ = "command_line"
cursor_cpos_ = "cursor_cpos"
comp_scope_ = "comp_scope"
is_debug_enabled_ = "is_debug_enabled"

_sample_command_line = "some_command goto service "

_call_context_example = {
    server_action_: ServerAction.DescribeLineArgs.name,
    command_line_: _sample_command_line,
    cursor_cpos_: len(_sample_command_line),
    comp_scope_: CompScope.ScopeInitial.name,
    is_debug_enabled_: False,
}


class CallContextSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    server_action = fields.Enum(
        ServerAction,
        required = True,
        metadata = {
            "description": (
                "Action to perform - see " + ServerAction.__name__ + " enum"
            ),
            "example": _call_context_example[server_action_],
        },
    )
    command_line = fields.String(
        required = True,
        metadata = {
            "example": _call_context_example[command_line_],
        },
    )
    cursor_cpos = fields.Integer(
        required = True,
        metadata = {
            "description": "Cursor position within command line (0 = before the first char)",
            "example": _call_context_example[cursor_cpos_],
        },
    )
    comp_scope = fields.Enum(
        CompScope,
        required = True,
        metadata = {
            "description": "Name for a completion scope - see " + CompScope.__name__ + " enum",
            "example": _call_context_example[comp_scope_],
        },
    )
    is_debug_enabled = fields.Boolean(
        required = True,
        metadata = {
            "description": "Enable extra debug output",
            "example": _call_context_example[is_debug_enabled_],
        },
    )

    @pre_dump
    def make_dict(
        self,
        input_object: CallContext,
        **kwargs,
    ):
        return {
            server_action_: input_object.server_action,
            command_line_: input_object.command_line,
            cursor_cpos_: input_object.cursor_cpos,
            comp_scope_: ensure_value_is_enum(input_object.comp_scope, CompScope),
            is_debug_enabled_: input_object.is_debug_enabled,
        }

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return CallContext(
            server_action = ensure_value_is_enum(input_dict[server_action_], ServerAction),
            command_line = input_dict[command_line_],
            cursor_cpos = input_dict[cursor_cpos_],
            # TODO: Is calling `ensure_value_is_enum` even required?
            comp_scope = ensure_value_is_enum(input_dict[comp_scope_], CompScope),
            is_debug_enabled = input_dict[is_debug_enabled_],
        )


call_context_desc = TypeDesc(
    dict_schema = CallContextSchema(),
    ref_name = CallContextSchema.__name__,
    dict_example = _call_context_example,
    default_file_path = "",
)
