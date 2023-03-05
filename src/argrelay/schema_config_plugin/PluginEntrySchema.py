from marshmallow import Schema, fields, RAISE, post_load, pre_dump

from argrelay.enum_desc.PluginType import PluginType
from argrelay.misc_helper import ensure_value_is_enum
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.plugin_loader.NoopLoader import NoopLoader
from argrelay.runtime_data.PluginEntry import PluginEntry

plugin_config_ = "plugin_config"
plugin_module_name_ = "plugin_module_name"
plugin_class_name_ = "plugin_class_name"
plugin_type_ = "plugin_type"

_plugin_entry_example = {
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

    plugin_module_name = fields.String(
        required = True,
    )

    plugin_class_name = fields.String(
        required = True,
    )

    plugin_type = fields.Enum(
        PluginType,
        by_value = False,
        required = True,
    )

    plugin_config = fields.Dict(
        required = True,
    )

    @pre_dump
    def make_dict(self, input_object: PluginEntry, **kwargs):
        # TODO: figure out to populate all automatically and reduce duplication - this is error-prone:
        if isinstance(input_object, PluginEntry):
            return {
                plugin_module_name_: input_object.plugin_module_name,
                plugin_class_name_: input_object.plugin_class_name,
                plugin_type_: ensure_value_is_enum(input_object.plugin_type, PluginType),
                plugin_config_: input_object.plugin_config,
            }
        else:
            # Assuming it is as dict:
            return {
                plugin_module_name_: input_object[plugin_module_name_],
                plugin_class_name_: input_object[plugin_class_name_],
                plugin_type_: ensure_value_is_enum(input_object[plugin_type_], PluginType),
                plugin_config_: input_object[plugin_config_],
            }

    @post_load
    def make_object(self, input_dict, **kwargs):
        return PluginEntry(
            plugin_module_name = input_dict[plugin_module_name_],
            plugin_class_name = input_dict[plugin_class_name_],
            plugin_type = ensure_value_is_enum(input_dict[plugin_type_], PluginType),
            plugin_config = input_dict[plugin_config_],
        )


plugin_entry_desc = TypeDesc(
    dict_schema = PluginEntrySchema(),
    ref_name = PluginEntrySchema.__name__,
    dict_example = _plugin_entry_example,
    default_file_path = "",
)
