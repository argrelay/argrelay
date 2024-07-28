from __future__ import annotations

from marshmallow import fields, RAISE, post_load

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

reusable_config_data_ = "reusable_config_data"
plugin_instance_entries_ = "plugin_instance_entries"
check_env_plugin_instance_entries_ = "check_env_plugin_instance_entries"


class PluginConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = PluginConfig

    # This `dict` provides a place to store arbitrary data.
    # YAML allows reusing any (substantially complex) data via aliases:
    # https://stackoverflow.com/a/48946813/441652
    # But `marshmallow` does not allow arbitrary data by default
    # (and it is kept that way to let garbage slip through).
    # This `dict` is ignored on load -
    # the data is used by YAML loader before it even reaches the schema validation.
    # See also values merge:
    # https://stackoverflow.com/a/46644785/441652
    reusable_config_data = fields.Dict(
        required = False,
        load_default = {},
    )

    # Plugin config data: key = `plugin_instance_id`, value = `plugin_entry`:
    plugin_instance_entries = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
        required = True,
    )

    # TODO: Move it into separate file/schema:
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
        # TODO: avoid calling it on load - it is only needed by server, not by client:
        # Build DAG:
        plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[plugin_instance_entries_]:
            plugin_entry: PluginEntry = input_dict[plugin_instance_entries_][plugin_instance_id]
            plugin_instance_id_activate_order_dag[plugin_instance_id] = plugin_entry.plugin_dependencies

        # TODO: Move it into separate file/schema:
        check_env_plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[check_env_plugin_instance_entries_]:
            plugin_entry: PluginEntry = input_dict[check_env_plugin_instance_entries_][plugin_instance_id]
            check_env_plugin_instance_id_activate_order_dag[plugin_instance_id] = plugin_entry.plugin_dependencies

        return type(self).model_class(
            **input_dict,
            plugin_instance_id_activate_list = serialize_dag_to_list(
                plugin_instance_id_activate_order_dag,
            ),
            check_env_plugin_instance_id_activate_list = serialize_dag_to_list(
                check_env_plugin_instance_id_activate_order_dag,
            ),
        )


plugin_config_desc = TypeDesc(
    dict_schema = PluginConfigSchema(),
    ref_name = PluginConfigSchema.__name__,
    dict_example = {
        plugin_instance_entries_: {
            "some_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
        check_env_plugin_instance_entries_: {
            "some_check_env_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_check_env_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
    },
    default_file_path = "argrelay_plugin.yaml",
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
