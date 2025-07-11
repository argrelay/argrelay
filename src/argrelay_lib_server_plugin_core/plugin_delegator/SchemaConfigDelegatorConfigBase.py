from __future__ import annotations

from marshmallow import (
    fields,
    RAISE,
    Schema,
)

from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_lib_server_plugin_core.plugin_delegator.FuncConfigSchema import (
    func_config_desc,
)
from argrelay_schema_config_server.schema_config_interp.FuncEnvelopeSchema import (
    func_id_some_func_,
)

func_configs_ = "func_configs"


class SchemaConfigDelegatorConfigBase(Schema):
    """
    Part of FS_49_96_50_77 config_only_delegator implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    func_configs = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(func_config_desc.dict_schema),
        required=True,
    )


base_config_delegator_config_desc = TypeDesc(
    dict_schema=SchemaConfigDelegatorConfigBase(),
    ref_name=SchemaConfigDelegatorConfigBase.__name__,
    dict_example={
        func_configs_: {
            func_id_some_func_: func_config_desc.dict_example,
        },
    },
    default_file_path="",
)
