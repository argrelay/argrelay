from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoServerConfig import MongoServerConfig

database_name_ = "database_name"
start_server_ = "start_server"
server_start_command_ = "server_start_command"


class MongoServerConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = MongoServerConfig

    database_name = fields.String()

    start_server = fields.Boolean()

    server_start_command = fields.String()


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
