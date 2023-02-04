from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.schema_config_core_server.MongoClientConfigSchema import mongo_client_config_desc
from argrelay.schema_config_core_server.MongoServerConfigSchema import mongo_server_config_desc

use_mongomock_only_ = "use_mongomock_only"
mongo_client_ = "mongo_client"
mongo_server_ = "mongo_server"


class MongoConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    use_mongomock_only = fields.Boolean()
    """
    It might be the case that (test) `mongomock` lib actually provides necessary functionality and meet
    non-function requirements for many (prod) workloads without need to deploy and administer MongoDB.
    https://github.com/mongomock/mongomock
    """

    mongo_client = fields.Nested(mongo_client_config_desc.dict_schema)

    mongo_server = fields.Nested(mongo_server_config_desc.dict_schema)

    @post_load
    def make_object(self, input_dict, **kwargs):
        return MongoConfig(
            use_mongomock_only = input_dict[use_mongomock_only_],
            mongo_client = input_dict[mongo_client_],
            mongo_server = input_dict[mongo_server_],
        )


mongo_config_desc = TypeDesc(
    dict_schema = MongoConfigSchema(),
    ref_name = MongoConfigSchema.__name__,
    dict_example = {
        use_mongomock_only_: True,
        mongo_client_: mongo_client_config_desc.dict_example,
        mongo_server_: mongo_server_config_desc.dict_example,
    },
    default_file_path = "",
)
