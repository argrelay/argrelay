from __future__ import annotations

from marshmallow import fields, RAISE

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_config_core_server.GuiBannerConfigSchema import gui_banner_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.QueryCacheConfigSchema import query_cache_config_desc
from argrelay.schema_config_core_server.ServerPluginControlSchema import server_plugin_control_desc

connection_config_ = "connection_config"
mongo_config_ = "mongo_config"
query_cache_config_ = "query_cache_config"
gui_banner_config_ = "gui_banner_config"
default_gui_command_ = "default_gui_command"
server_plugin_control_ = "server_plugin_control"


class ServerConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ServerConfig

    connection_config = fields.Nested(
        connection_config_desc.dict_schema,
        required = True,
    )

    mongo_config = fields.Nested(
        mongo_config_desc.dict_schema,
        required = True,
    )

    query_cache_config = fields.Nested(
        query_cache_config_desc.dict_schema,
        required = True,
    )

    gui_banner_config = fields.Nested(
        gui_banner_config_desc.dict_schema,
        required = True,
    )

    default_gui_command = fields.String(
        required = False,
        load_default = None,
    )

    server_plugin_control = fields.Nested(
        server_plugin_control_desc.dict_schema,
        required = True,
    )


server_config_desc = TypeDesc(
    dict_schema = ServerConfigSchema(),
    ref_name = ServerConfigSchema.__name__,
    dict_example = {
        connection_config_: connection_config_desc.dict_example,
        mongo_config_: mongo_config_desc.dict_example,
        query_cache_config_: query_cache_config_desc.dict_example,
        gui_banner_config_: gui_banner_config_desc.dict_example,
        server_plugin_control_: server_plugin_control_desc.dict_example,
    },
    default_file_path = "argrelay_server.yaml",
)
