from marshmallow import Schema, fields, RAISE, post_load

from argrelay.api_ext.meta_data.PluginType import PluginType
from argrelay.api_ext.relay_server.PluginEntry import PluginEntry
from argrelay.misc_helper.NoopLoader import NoopLoader
from argrelay.misc_helper.TypeDesc import TypeDesc

_plugin_entry_example = {
    "plugin_id": NoopLoader.__name__,
    "plugin_module_name": NoopLoader.__module__,
    "plugin_class_name": NoopLoader.__name__,
    "plugin_type": PluginType.LoaderPlugin.name,
    "plugin_config": {
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
            plugin_id = input_dict["plugin_id"],
            plugin_module_name = input_dict["plugin_module_name"],
            plugin_class_name = input_dict["plugin_class_name"],
            plugin_type = input_dict["plugin_type"],
            plugin_config = input_dict["plugin_config"],
        )


plugin_entry_desc = TypeDesc(
    object_schema = PluginEntrySchema(),
    ref_name = PluginEntrySchema.__name__,
    dict_example = _plugin_entry_example,
    default_file_path = "",
)
