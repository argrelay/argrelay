from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.relay_server.QueryCacheConfig import QueryCacheConfig

enable_query_cache_ = "enable_query_cache"
query_cache_ttl_sec_ = "query_cache_ttl_sec"
query_cache_max_size_bytes_ = "query_cache_max_size_bytes"


class QueryCacheConfigSchema(ObjectSchema):
    """
    Config schema for FS_39_58_01_91 query cache.
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = QueryCacheConfig

    enable_query_cache = fields.Boolean()

    query_cache_ttl_sec = fields.Integer()

    query_cache_max_size_bytes = fields.Integer()


query_cache_config_desc = TypeDesc(
    dict_schema = QueryCacheConfigSchema(),
    ref_name = QueryCacheConfigSchema.__name__,
    dict_example = {
        enable_query_cache_: True,
        query_cache_ttl_sec_: 60,
        query_cache_max_size_bytes_: 1024 * 1024,
    },
    default_file_path = "",
)
