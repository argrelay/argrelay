from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoConfig import MongoConfig

client_connection_string_ = "client_connection_string"
database_name_ = "database_name"
start_server_ = "start_server"


class MongoConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    client_connection_string = fields.String()
    database_name = fields.String()
    start_server = fields.Boolean()
    server_start_command = fields.String()

    @post_load
    def make_object(self, input_dict, **kwargs):
        return MongoConfig(
            client_connection_string = input_dict[client_connection_string_],
            database_name = input_dict[database_name_],
            start_server = input_dict["start_server"],
            server_start_command = input_dict["server_start_command"],
        )


mongo_config_desc = TypeDesc(
    object_schema = MongoConfigSchema(),
    ref_name = MongoConfigSchema.__name__,
    dict_example = {
        # TODO: Can it be as simple as "mongodb://localhost:27017" or even "mongodb://localhost"?
        client_connection_string_: "mongodb://test:test@localhost/test?authSource=admin",
        database_name_: "test",
        start_server_: False,
        "server_start_command":
            "~/argrelay.git/temp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod"
            " --dbpath "
            "~/argrelay.git/temp/mongo/data",
    },
    default_file_path = "",
)
