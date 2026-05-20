from marshmallow import (
    fields,
    RAISE,
)

from argrelay_app_mcp_proxy.mcp_proxy.McpProxyConfig import McpProxyConfig
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc

log_dir_rel_path_ = "log_dir_rel_path"
heartbeat_interval_sec_ = "heartbeat_interval_sec"


class McpProxyConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = McpProxyConfig

    __comment__ = fields.String(
        required=False,
        load_default="",
    )

    log_dir_rel_path = fields.String(
        required=False,
        load_default="./logs",
    )

    heartbeat_interval_sec = fields.Float(
        required=False,
        load_default=5.0,
    )


mcp_proxy_config_desc = TypeDesc(
    dict_schema=McpProxyConfigSchema(),
    ref_name=McpProxyConfigSchema.__name__,
    dict_example={
        log_dir_rel_path_: "./logs",
    },
    default_file_path="argrelay_mcp_proxy.json",
)
