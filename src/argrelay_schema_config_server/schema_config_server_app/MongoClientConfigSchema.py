from marshmallow import (
    fields,
    RAISE,
)

from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_server.runtime_data_server_app.MongoClientConfig import MongoClientConfig

client_connection_string_ = "client_connection_string"


class MongoClientConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = MongoClientConfig

    client_connection_string = fields.String()
    """
    See: https://www.mongodb.com/docs/manual/reference/connection-string/

    Full format:
    mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]

    The simplest:
    mongodb://localhost
    """


mongo_client_config_desc = TypeDesc(
    dict_schema = MongoClientConfigSchema(),
    ref_name = MongoClientConfigSchema.__name__,
    dict_example = {
        client_connection_string_: "mongodb://localhost",
    },
    default_file_path = "",
)
