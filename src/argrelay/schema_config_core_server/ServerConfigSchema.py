from __future__ import annotations

from marshmallow import fields, RAISE

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_config_core_server.GuiBannerConfigSchema import gui_banner_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.QueryCacheConfigSchema import query_cache_config_desc
from argrelay.schema_config_core_server.ServerPluginControlSchema import server_plugin_control_desc
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc

connection_config_ = "connection_config"
mongo_config_ = "mongo_config"
query_cache_config_ = "query_cache_config"
gui_banner_config_ = "gui_banner_config"
class_to_collection_map_ = "class_to_collection_map"
server_plugin_control_ = "server_plugin_control"
static_data_ = "static_data"


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

    # Related to FS_56_43_05_79 search diff collection:
    # Maps names of envelope classes to names of `EnvelopeCollection`.
    # Specifically, it allows to:
    # *   map classes to put all into single collection
    # *   map classes to put each into separate collection
    # Normally, if map entry is missing for one of the envelope class,
    # it uses envelope class name as collection name by default.
    class_to_collection_map = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )

    server_plugin_control = fields.Nested(
        server_plugin_control_desc.dict_schema,
        required = True,
    )

    # TODO_00_79_72_55: remove in the future:
    static_data = fields.Nested(
        static_data_desc.dict_schema,
        required = False,
        load_default = StaticData(
            envelope_collections = {},
        ),
    )


server_config_desc = TypeDesc(
    dict_schema = ServerConfigSchema(),
    ref_name = ServerConfigSchema.__name__,
    dict_example = {
        connection_config_: connection_config_desc.dict_example,
        mongo_config_: mongo_config_desc.dict_example,
        query_cache_config_: query_cache_config_desc.dict_example,
        gui_banner_config_: gui_banner_config_desc.dict_example,
        class_to_collection_map_: {
            ServiceEnvelopeClass.ClassCluster.name: ServiceEnvelopeClass.ClassCluster.name,
            ServiceEnvelopeClass.ClassHost.name: ServiceEnvelopeClass.ClassHost.name,
            ServiceEnvelopeClass.ClassService.name: ServiceEnvelopeClass.ClassService.name,
            ServiceEnvelopeClass.ClassAccessType.name: ServiceEnvelopeClass.ClassAccessType.name,
        },
        server_plugin_control_: server_plugin_control_desc.dict_example,
        static_data_: static_data_desc.dict_example,
    },
    default_file_path = "argrelay_server.yaml",
)
