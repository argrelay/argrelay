from __future__ import annotations

from marshmallow import fields, RAISE, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.BasePluginConfigSchema import BasePluginConfigSchema, serialize_dag_to_list
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

reusable_config_data_ = "reusable_config_data"
plugin_instance_entries_ = "plugin_instance_entries"


class PluginConfigSchema(BasePluginConfigSchema):
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

        return type(self).model_class(
            **input_dict,
            plugin_instance_id_activate_list = serialize_dag_to_list(
                plugin_instance_id_activate_order_dag,
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
    },
    default_file_path = "argrelay_plugin.yaml",
)
