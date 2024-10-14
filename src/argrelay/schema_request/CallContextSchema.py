from marshmallow import fields, RAISE

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.server_spec.CallContext import CallContext

client_version_ = "client_version"
client_conf_target_ = "client_conf_target"
server_action_ = "server_action"
command_line_ = "command_line"
cursor_cpos_ = "cursor_cpos"
comp_scope_ = "comp_scope"
client_uid_ = "client_uid"
client_pid_ = "client_pid"
is_debug_enabled_ = "is_debug_enabled"
input_data_ = "input_data"

_sample_command_line = "some_command goto service "

_call_context_example = {
    client_version_: "",
    client_conf_target_: "",
    server_action_: ServerAction.DescribeLineArgs.name,
    command_line_: _sample_command_line,
    cursor_cpos_: len(_sample_command_line),
    comp_scope_: CompScope.ScopeInitial.name,
    client_uid_: "",
    client_pid_: 0,
    is_debug_enabled_: False,
    input_data_: None,
}


class CallContextSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        ordered = True

    model_class = CallContext

    client_version = fields.String(
        required = False,
        metadata = {
            "description": "client version of `argrelay` package (empty = not set)",
            "example": _call_context_example[client_version_],
        },
        load_default = "",
    )
    client_conf_target = fields.String(
        required = False,
        metadata = {
            "description": "target path of `@/conf` symlink (empty = not set)",
            "example": _call_context_example[client_conf_target_],
        },
        load_default = "",
    )
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
    client_uid = fields.String(
        required = False,
        metadata = {
            "description": "UID (user name) of the client user according to OS (empty = not set)",
            "example": _call_context_example[client_uid_],
        },
        load_default = "",
    )
    client_pid = fields.Integer(
        required = False,
        metadata = {
            "description": "PID of the client process local to the client host (0 = not set)",
            "example": _call_context_example[client_pid_],
        },
        load_default = 0,
    )
    is_debug_enabled = fields.Boolean(
        required = True,
        metadata = {
            "description": "Enable extra debug output",
            "example": _call_context_example[is_debug_enabled_],
        },
    )
    input_data = fields.String(
        required = False,
        load_default = None,
        metadata = {
            "description": "Enable extra debug output",
            "example": _call_context_example[input_data_],
        },
    )


call_context_desc = TypeDesc(
    dict_schema = CallContextSchema(),
    ref_name = CallContextSchema.__name__,
    dict_example = _call_context_example,
    default_file_path = "",
)
