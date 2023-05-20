import os

from marshmallow import Schema, fields, RAISE, post_load, validates_schema, ValidationError

from argrelay.misc_helper import get_config_path
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_config_core_server.GuiBannerConfigSchema import gui_banner_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.QueryCacheConfigSchema import query_cache_config_desc
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

connection_config_ = "connection_config"
mongo_config_ = "mongo_config"
query_cache_config_ = "query_cache_config"
gui_banner_config_ = "gui_banner_config"
plugin_instance_id_load_list_ = "plugin_instance_id_load_list"
plugin_dict_ = "plugin_dict"
static_data_ = "static_data"


class ServerConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

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

    # Lists `plugin_instance_id`-s to specify load order for the plugins and their activation.
    plugin_instance_id_load_list = fields.List(
        fields.String(),
        required = True,
    )

    # Plugin config data: key = `plugin_instance_id`, value = `plugin_entry`:
    plugin_dict = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
        required = True,
    )

    static_data = fields.Nested(
        static_data_desc.dict_schema,
        required = True,
    )

    # No interp_factories field for schema -
    # it is generated for ServerConfig internally based on `plugin_instance_id_load_list`.

    @post_load
    def make_object(self, input_dict, **kwargs):
        # Populate `plugin_instance_id` from `plugin_dict` into each
        return ServerConfig(
            connection_config = input_dict[connection_config_],
            mongo_config = input_dict[mongo_config_],
            query_cache_config = input_dict[query_cache_config_],
            gui_banner_config = input_dict[gui_banner_config_],
            plugin_instance_id_load_list = input_dict[plugin_instance_id_load_list_],
            plugin_dict = input_dict[plugin_dict_],
            static_data = input_dict[static_data_],
        )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        for plugin_instance_id in input_dict[plugin_instance_id_load_list_]:
            # Ensure every `plugin_instance_id` is defined in `plugin_dict`:
            if plugin_instance_id not in input_dict[plugin_dict_]:
                raise ValidationError(f"`{plugin_instance_id}` is not defined in `{plugin_dict_}`")


server_config_desc = TypeDesc(
    dict_schema = ServerConfigSchema(),
    ref_name = ServerConfigSchema.__name__,
    dict_example = {
        connection_config_: connection_config_desc.dict_example,
        mongo_config_: mongo_config_desc.dict_example,
        query_cache_config_: query_cache_config_desc.dict_example,
        gui_banner_config_: gui_banner_config_desc.dict_example,
        plugin_instance_id_load_list_: [
            "some_plugin_instance_id",
        ],
        plugin_dict_: {
            "some_plugin_instance_id": plugin_entry_desc.dict_example,
        },
        static_data_: static_data_desc.dict_example,
    },
    default_file_path = get_config_path("argrelay.server.yaml"),
)
