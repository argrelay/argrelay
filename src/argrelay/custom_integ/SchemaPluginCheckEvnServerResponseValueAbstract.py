from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FuncEnvelopeSchema import (
    func_id_some_func_,
)

field_values_to_command_lines_ = "field_values_to_command_lines"


class SchemaPluginCheckEvnServerResponseValueAbstract(Schema):
    """
    Part of FS_36_17_84_44 `check_env` implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    # Configures field name to retrieve in response from command line.
    field_values_to_command_lines = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


schema_plugin_check_evn_server_response_abstract_desc = TypeDesc(
    dict_schema = SchemaPluginCheckEvnServerResponseValueAbstract(),
    ref_name = SchemaPluginCheckEvnServerResponseValueAbstract.__name__,
    dict_example = {
        field_values_to_command_lines_: {
            func_id_some_func_: CheckEnvField.server_git_commit_id.name,
        },
    },
    default_file_path = "",
)
