from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FuncEnvelopeSchema import (
    func_envelope_desc,
)

func_envelope_ = "func_envelope"
fill_control_list_ = "fill_control_list"


class FuncConfigSchema(Schema):
    """
    Part of FS_49_96_50_77 config_only_plugins implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    fill_control_list = fields.List(
        fields.Dict(
            keys = fields.String(),
            values = fields.String(),
            required = True,
        ),
        required = False,
    )
    """
    FS_49_96_50_77 Config-only delegator implementation to compute default values:
    A `list` of `dict`-s with each list item corresponds to the `search_control_list_`.
    Each `dict` controls setting default values (based on already found `data_envelope`-s):
    *   Each key is a prop name to set default value for.
    *   Each value is an expression for prop value which may refer to already prev `envelope_container`-s.
    """

    func_envelope = fields.Nested(func_envelope_desc.dict_schema)


func_config_desc = TypeDesc(
    dict_schema = FuncConfigSchema(),
    ref_name = FuncConfigSchema.__name__,
    dict_example = {
        fill_control_list_: [
            {
            },
            {
            },
            {
                "severity_level": "{envelope_containers[1].data_envelopes[0]['severity_level']}",
                "exit_code": "{envelope_containers[1].data_envelopes[0]['exit_code']}",
            },
        ],
        func_envelope_: func_envelope_desc.dict_example,
    },
    default_file_path = "",
)
