from __future__ import annotations

from marshmallow import (
    fields,
    post_load,
    pre_load,
    RAISE,
)

from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_check_env.runtime_data_check_env_app.CheckEnvPluginConfig import CheckEnvPluginConfig
from argrelay_schema_config_server.runtime_data_server_plugin.PluginEntry import PluginEntry
from argrelay_schema_config_server.schema_config_server_plugin.BasePluginConfigSchema import (
    BasePluginConfigSchema,
    serialize_dag_to_list,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginEntrySchema import plugin_entry_desc

check_env_plugin_instances_ = "check_env_plugin_instances"


class CheckEnvPluginConfigSchema(BasePluginConfigSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = CheckEnvPluginConfig

    check_env_plugin_instances = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
        required = True,
    )

    @pre_load
    def adjust_before_validation(
        self,
        input_dict,
        **kwargs,
    ):
        # TODO: Temporary (for backward-compatibility until `check_env dry_run` gets deployed wider):
        #       allow old config schema to exist for a while:
        if check_env_plugin_instances_ not in input_dict:
            input_dict[check_env_plugin_instances_] = input_dict.pop("check_env_plugin_instance_entries")
        return input_dict

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        # Build DAG:
        check_env_plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[check_env_plugin_instances_]:
            plugin_entry: PluginEntry = input_dict[check_env_plugin_instances_][plugin_instance_id]
            check_env_plugin_instance_id_activate_order_dag[plugin_instance_id] = plugin_entry.plugin_dependencies

        return type(self).model_class(
            **input_dict,
            check_env_plugin_instance_id_activate_list = serialize_dag_to_list(
                check_env_plugin_instance_id_activate_order_dag,
            ),
        )


check_env_plugin_config_desc = TypeDesc(
    dict_schema = CheckEnvPluginConfigSchema(),
    ref_name = CheckEnvPluginConfigSchema.__name__,
    dict_example = {
        check_env_plugin_instances_: {
            "some_check_env_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
    },
    default_file_path = "check_env_plugin.conf.yaml",
)
