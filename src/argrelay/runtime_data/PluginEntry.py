from dataclasses import dataclass, field

from argrelay.enum_desc.PluginType import PluginType


@dataclass(frozen = True)
class PluginEntry:
    plugin_module_name: str = field()
    plugin_class_name: str = field()
    plugin_type: PluginType = field()
    plugin_config: dict = field()
