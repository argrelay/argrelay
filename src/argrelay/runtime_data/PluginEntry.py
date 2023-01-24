from dataclasses import dataclass

from argrelay.enum_desc.PluginType import PluginType


@dataclass(frozen = True)
class PluginEntry:
    plugin_module_name: str
    plugin_class_name: str
    plugin_type: PluginType
    plugin_config: dict
