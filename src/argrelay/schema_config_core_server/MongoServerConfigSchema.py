from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoServerConfig import MongoServerConfig

database_name_ = "database_name"
start_server_ = "start_server"
server_start_command_ = "server_start_command"


class MongoServerConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    database_name = fields.String()

    start_server = fields.Boolean()

    server_start_command = fields.String()

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return MongoServerConfig(
            database_name = input_dict[database_name_],
            start_server = input_dict[start_server_],
            server_start_command = input_dict[server_start_command_],
        )


mongo_server_config_desc = TypeDesc(
    dict_schema = MongoServerConfigSchema(),
    ref_name = MongoServerConfigSchema.__name__,
    dict_example = {
        database_name_: "argrelay",
        start_server_: False,
        server_start_command_:
            "~/argrelay.git/tmp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod"
            " --dbpath "
            "~/argrelay.git/tmp/mongo/data",
    },
    default_file_path = "",
)
