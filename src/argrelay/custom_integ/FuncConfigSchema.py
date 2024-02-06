from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FuncEnvelopeSchema import (
    func_envelope_desc,
)

command_template_ = "command_template"
func_envelope_ = "func_envelope"

class FuncConfigSchema(Schema):
    """
    Part of FS_49_96_50_77 config_only_plugins implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    command_template = fields.String()

    func_envelope = fields.Nested(func_envelope_desc.dict_schema)


func_config_desc = TypeDesc(
    dict_schema = FuncConfigSchema(),
    ref_name = FuncConfigSchema.__name__,
    dict_example = {
        command_template_: "echo",
        func_envelope_: func_envelope_desc.dict_example,
    },
    default_file_path = "",
)
