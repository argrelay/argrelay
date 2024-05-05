from marshmallow import fields, RAISE

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.PluginEntry import PluginEntry

plugin_enabled_ = "plugin_enabled"
plugin_config_ = "plugin_config"
plugin_module_name_ = "plugin_module_name"
plugin_class_name_ = "plugin_class_name"
plugin_dependencies_ = "plugin_dependencies"


class PluginEntrySchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = PluginEntry

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
