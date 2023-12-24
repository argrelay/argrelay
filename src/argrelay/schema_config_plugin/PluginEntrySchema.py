from marshmallow import Schema, fields, RAISE, post_load, pre_dump

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginEntry import PluginEntry

plugin_enabled_ = "plugin_enabled"
plugin_config_ = "plugin_config"
plugin_module_name_ = "plugin_module_name"
plugin_class_name_ = "plugin_class_name"
plugin_dependencies_ = "plugin_dependencies"


class PluginEntrySchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    plugin_enabled = fields.Boolean(
        required = False,
        load_default = True,
    )

    plugin_module_name = fields.String(
        required = True,
    )

    plugin_class_name = fields.String(
        required = True,
    )

    # List of other plugin instance ids this plugin depends on:
    plugin_dependencies = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )

    plugin_config = fields.Dict(
        required = False,
        load_default = {},
    )

    @pre_dump
    def make_dict(
        self,
        input_object: PluginEntry,
        **kwargs,
    ):
        return {
            plugin_enabled_: input_object.plugin_enabled,
            plugin_module_name_: input_object.plugin_module_name,
            plugin_class_name_: input_object.plugin_class_name,
            plugin_dependencies_: input_object.plugin_dependencies,
            plugin_config_: input_object.plugin_config,
        }

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return PluginEntry(
            plugin_enabled = input_dict[plugin_enabled_],
            plugin_module_name = input_dict[plugin_module_name_],
            plugin_class_name = input_dict[plugin_class_name_],
            plugin_dependencies = input_dict[plugin_dependencies_],
            plugin_config = input_dict[plugin_config_],
        )


_plugin_entry_example = {
    plugin_enabled_: True,
    plugin_module_name_: "SomePluginModule",
    plugin_class_name_: "SomePluginClass",
    plugin_dependencies_: [],
    plugin_config_: {
    },
}

plugin_entry_desc = TypeDesc(
    dict_schema = PluginEntrySchema(),
    ref_name = PluginEntrySchema.__name__,
    dict_example = _plugin_entry_example,
    default_file_path = "",
)
