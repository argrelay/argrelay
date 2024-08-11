from marshmallow import fields, RAISE

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.relay_server.UsageStatsEntry import UsageStatsEntry
from argrelay.schema_request.CallContextSchema import (
    server_action_,
    command_line_,
    call_context_desc,
    comp_scope_,
    cursor_cpos_,
)

server_ts_ns_ = "server_ts_ns"
client_version_ = "client_version"
client_conf_target_ = "client_conf_target"
client_user_id_ = "client_user_id"


class UsageStatsEntrySchema(ObjectSchema):
    """
    Schema for FS_87_02_77_34: usage stats entry - see `UsageStatsEntry`.
    """

    class Meta:
        unknown = RAISE
        ordered = True

    model_class = UsageStatsEntry

    server_action = fields.Enum(
        ServerAction,
        required = True,
    )

    comp_scope = fields.Enum(
        CompScope,
        required = True,
    )

    server_ts_ns = fields.Integer(
        required = False,
        load_default = 0,
    )

    client_version = fields.String(
        required = False,
        load_default = "",
    )

    client_conf_target = fields.String(
        required = False,
        load_default = "",
    )

    client_user_id = fields.String(
        required = False,
        load_default = "",
    )

    command_line = fields.String(
        required = True,
    )

    cursor_cpos = fields.Integer(
        required = True,
    )


usage_stats_entry_desc = TypeDesc(
    dict_schema = UsageStatsEntrySchema(),
    ref_name = UsageStatsEntrySchema.__name__,
    dict_example = {
        server_action_: call_context_desc.dict_example[server_action_],
        comp_scope_: call_context_desc.dict_example[comp_scope_],
        server_ts_ns_: 0,
        client_version_: "",
        client_conf_target_: "",
        client_user_id_: "",
        command_line_: call_context_desc.dict_example[command_line_],
        cursor_cpos_: call_context_desc.dict_example[cursor_cpos_],
    },
    default_file_path = "",
)
