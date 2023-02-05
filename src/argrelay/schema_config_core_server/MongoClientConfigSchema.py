from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoClientConfig import MongoClientConfig

client_connection_string_ = "client_connection_string"


class MongoClientConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    client_connection_string = fields.String()
    """
    See: https://www.mongodb.com/docs/manual/reference/connection-string/

    Full format:
    mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]

    The simplest:
    mongodb://localhost
    """

    @post_load
    def make_object(self, input_dict, **kwargs):
        return MongoClientConfig(
            client_connection_string = input_dict[client_connection_string_],
        )


mongo_client_config_desc = TypeDesc(
    dict_schema = MongoClientConfigSchema(),
    ref_name = MongoClientConfigSchema.__name__,
    dict_example = {
        client_connection_string_: "mongodb://localhost",
    },
    default_file_path = "",
)
