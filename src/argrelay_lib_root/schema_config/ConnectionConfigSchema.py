from marshmallow import (
    fields,
    RAISE,
)

from argrelay_api_server_cli.server_spec.const_int import (
    DEFAULT_IP_ADDRESS,
    DEFAULT_PORT_NUMBER,
)
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_lib_root.schema_config.ConnectionConfig import ConnectionConfig

server_host_name_ = "server_host_name"
server_port_number_ = "server_port_number"


class ConnectionConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ConnectionConfig

    server_host_name = fields.String(
        load_default=DEFAULT_IP_ADDRESS,
    )

    server_port_number = fields.Integer(
        load_default=DEFAULT_PORT_NUMBER,
    )


connection_config_desc = TypeDesc(
    dict_schema=ConnectionConfigSchema(),
    ref_name=ConnectionConfigSchema.__name__,
    dict_example={
        server_host_name_: DEFAULT_IP_ADDRESS,
        server_port_number_: DEFAULT_PORT_NUMBER,
    },
    default_file_path="",
)
