from __future__ import annotations

from copy import deepcopy

from marshmallow import fields, RAISE, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.BasePluginConfigSchema import BasePluginConfigSchema, serialize_dag_to_list
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc

server_plugin_instances_ = "server_plugin_instances"
server_plugin_instance_groups_ = "server_plugin_instance_groups"


class PluginConfigSchema(BasePluginConfigSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = PluginConfig

    # TODO: consider removing this and using only `server_plugin_instance_groups`:
    # Plugin config data: key = `plugin_instance_id`, value = `plugin_entry`:
    server_plugin_instances = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(plugin_entry_desc.dict_schema),
        required = False,
        load_default = {},
    )

    # TODO: consider removing `server_plugin_instances` and using this:
    # Same as `server_plugin_instances` but with extra `dict` level
    # to group plugin instances under that level.
    # This has no impact on the logic - it is purely a convenience for configuration
    # (e.g. to be able to `!include` entire group from another file - see FS_70_55_40_99 splitting config file).
    server_plugin_instance_groups = fields.Dict(
        keys = fields.String(),
        values = fields.Dict(
            keys = fields.String(),
            values = fields.Nested(plugin_entry_desc.dict_schema),
            required = True,
        ),
        required = False,
        load_default = {},
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        input_dict = self.adjust_for_unification(input_dict)

        # TODO: avoid calling it on load - it is only needed by server, not by client:
        # Build DAG:
        plugin_instance_id_activate_order_dag = {}
        for plugin_instance_id in input_dict[server_plugin_instances_]:
            plugin_entry: PluginEntry = input_dict[server_plugin_instances_][plugin_instance_id]
            plugin_instance_id_activate_order_dag[plugin_instance_id] = plugin_entry.plugin_dependencies

        return type(self).model_class(
            **input_dict,
            plugin_instance_id_activate_list = serialize_dag_to_list(
                plugin_instance_id_activate_order_dag,
            ),
        )

    # noinspection PyMethodMayBeStatic
    def adjust_for_unification(
        self,
        input_dict,
    ):
        # Make a `deepcopy` as `marshmallow` reuses instances specified in `load_default`:
        input_dict = deepcopy(input_dict)

        # Move all plugin instances from `server_plugin_instance_groups` to `server_plugin_instances`
        server_plugin_instance_groups = input_dict.pop(server_plugin_instance_groups_)
        dst_dict: dict = input_dict[server_plugin_instances_]
        src_dict: dict
        for src_dict in server_plugin_instance_groups.values():
            for plugin_instance_id, plugin_entry in src_dict.items():
                if plugin_instance_id in dst_dict:
                    raise AssertionError(
                        f"`plugin_instance_id` [{plugin_instance_id}] "
                        f"is already defined in `{server_plugin_instances_}` "
                    )
                dst_dict[plugin_instance_id] = plugin_entry
            src_dict.clear()
        return input_dict


plugin_config_desc = TypeDesc(
    dict_schema = PluginConfigSchema(),
    ref_name = PluginConfigSchema.__name__,
    dict_example = {
        server_plugin_instances_: {
            "some_plugin_instance_id": plugin_entry_desc.dict_example,
            "some_plugin_instance_id1": plugin_entry_desc.dict_example,
            "some_plugin_instance_id2": plugin_entry_desc.dict_example,
        },
    },
    default_file_path = "argrelay_plugin.yaml",
)
