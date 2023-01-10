from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoClientConfig import MongoClientConfig

client_connection_string_ = "client_connection_string"


class MongoClientConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    client_connection_string = fields.String()

    @post_load
    def make_object(self, input_dict, **kwargs):
        return MongoClientConfig(
            client_connection_string = input_dict[client_connection_string_],
        )


mongo_client_config_desc = TypeDesc(
    dict_schema = MongoClientConfigSchema(),
    ref_name = MongoClientConfigSchema.__name__,
    dict_example = {
        # TODO: Can it be as simple as "mongodb://localhost:27017" or even "mongodb://localhost"?
        client_connection_string_: "mongodb://test:test@localhost/test?authSource=admin",
    },
    default_file_path = "",
)
