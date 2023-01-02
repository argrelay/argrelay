from marshmallow import Schema, fields, RAISE, post_load

from argrelay.meta_data.PluginEntry import PluginEntry
from argrelay.meta_data.PluginType import PluginType
from argrelay.misc_helper.NoopLoader import NoopLoader
from argrelay.misc_helper.TypeDesc import TypeDesc

plugin_id_ = "plugin_id"
plugin_config_ = "plugin_config"
plugin_module_name_ = "plugin_module_name"
plugin_class_name_ = "plugin_class_name"
plugin_type_ = "plugin_type"

_plugin_entry_example = {
    plugin_id_: NoopLoader.__name__,
    plugin_module_name_: NoopLoader.__module__,
    plugin_class_name_: NoopLoader.__name__,
    plugin_type_: PluginType.LoaderPlugin.name,
    plugin_config_: {
    },
}


class PluginEntrySchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    plugin_id = fields.String(
        required = True,
    )
    plugin_module_name = fields.String(
        required = True,
    )
    plugin_class_name = fields.String(
        required = True,
    )
    plugin_type = fields.Enum(
        PluginType,
        required = True,
    )
    plugin_config = fields.Dict(
        required = True,
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return PluginEntry(
            plugin_id = input_dict[plugin_id_],
            plugin_module_name = input_dict[plugin_module_name_],
            plugin_class_name = input_dict[plugin_class_name_],
            plugin_type = input_dict[plugin_type_],
            plugin_config = input_dict[plugin_config_],
        )


plugin_entry_desc = TypeDesc(
    object_schema = PluginEntrySchema(),
    ref_name = PluginEntrySchema.__name__,
    dict_example = _plugin_entry_example,
    default_file_path = "",
)
