from __future__ import annotations

from marshmallow import Schema, fields, RAISE, post_load

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_config_core_server.GuiBannerConfigSchema import gui_banner_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.QueryCacheConfigSchema import query_cache_config_desc
from argrelay.schema_config_core_server.ServerPluginControlSchema import server_plugin_control_desc
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

connection_config_ = "connection_config"
mongo_config_ = "mongo_config"
query_cache_config_ = "query_cache_config"
gui_banner_config_ = "gui_banner_config"
class_to_collection_map_ = "class_to_collection_map"
server_plugin_control_ = "server_plugin_control"
plugin_instance_entries_ = "plugin_instance_entries"
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

    # Plugin config data: key = `plugin_instance_id`, value = `plugin_entry`:
    plugin_instance_entries = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
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

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        # Build DAG:
        plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[plugin_instance_entries_]:
            plugin_entry: PluginEntry = input_dict[plugin_instance_entries_][plugin_instance_id]
            plugin_instance_id_activate_order_dag[plugin_instance_id] = plugin_entry.plugin_dependencies

        return type(self).model_class(
            **input_dict,
            plugin_instance_id_activate_list = serialize_dag_to_list(
                plugin_instance_id_activate_order_dag,
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
        plugin_instance_entries_: {
            "some_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
        static_data_: static_data_desc.dict_example,
    },
    default_file_path = "argrelay_server.yaml",
)


def serialize_dag_to_list(
    entire_dag: dict[str, list[str]],
) -> list[str]:
    output_list: list[str] = list_sub_dag(
        [],
        entire_dag,
        [node_id for node_id in entire_dag],
    )
    return output_list


def list_sub_dag(
    curr_path: list[str],
    entire_dag: dict[str, list[str]],
    id_sub_list: list[str],
) -> list[str]:
    output_list: list[str] = []

    for node_id in id_sub_list:
        if node_id in curr_path:
            raise ValueError(f"cyclic ref to plugin id in path `{curr_path}` -> `{node_id}`")
        if node_id not in entire_dag:
            raise ValueError(f"plugin id in path `{curr_path}` -> `{node_id}` is not defined")
        if node_id in entire_dag:
            # plugin has dependencies:
            sub_list = list_sub_dag(
                curr_path + [node_id],
                entire_dag,
                entire_dag[node_id],
            )
            for sub_node_id in sub_list:
                if sub_node_id not in output_list:
                    output_list.append(sub_node_id)
        else:
            raise ValueError(f"plugin id in path `{curr_path}` -> `{node_id}` is not included for activation")

        if node_id not in output_list:
            output_list.append(node_id)

    return output_list
