from marshmallow import (
    fields,
    RAISE,
)

from argrelay_lib_root.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_server.runtime_data_server_app.MongoConfig import MongoConfig
from argrelay_schema_config_server.schema_config_server_app.MongoClientConfigSchema import mongo_client_config_desc
from argrelay_schema_config_server.schema_config_server_app.MongoServerConfigSchema import mongo_server_config_desc

use_mongomock_ = "use_mongomock"
distinct_values_query_ = "distinct_values_query"
mongo_client_ = "mongo_client"
mongo_server_ = "mongo_server"


class MongoConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = MongoConfig

    use_mongomock = fields.Boolean()
    """
    It might be the case that (test) `mongomock` lib actually provides necessary functionality and meet
    non-function requirements for many (prod) workloads without a need to deploy and administer MongoDB.
    https://github.com/mongomock/mongomock
    """

    distinct_values_query = fields.Enum(
        DistinctValuesQuery,
        required = True,
    )
    """
    See `DistinctValuesQuery`.
    """

    mongo_client = fields.Nested(mongo_client_config_desc.dict_schema)

    mongo_server = fields.Nested(mongo_server_config_desc.dict_schema)


mongo_config_desc = TypeDesc(
    dict_schema = MongoConfigSchema(),
    ref_name = MongoConfigSchema.__name__,
    dict_example = {
        use_mongomock_: True,
        distinct_values_query_: DistinctValuesQuery.original_find_and_loop.name,
        mongo_client_: mongo_client_config_desc.dict_example,
        mongo_server_: mongo_server_config_desc.dict_example,
    },
    default_file_path = "",
)
