from __future__ import annotations

from marshmallow import fields, RAISE, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.CheckEnvPluginConfig import CheckEnvPluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.BasePluginConfigSchema import BasePluginConfigSchema, serialize_dag_to_list
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

check_env_plugin_instance_entries_ = "check_env_plugin_instance_entries"


class CheckEnvPluginConfigSchema(BasePluginConfigSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = CheckEnvPluginConfig

    check_env_plugin_instance_entries = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
        required = True,
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        # Build DAG:
        check_env_plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[check_env_plugin_instance_entries_]:
            plugin_entry: PluginEntry = input_dict[check_env_plugin_instance_entries_][plugin_instance_id]
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
        check_env_plugin_instance_entries_: {
            "some_check_env_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
    },
    default_file_path = "check_env_plugin.conf.yaml",
)