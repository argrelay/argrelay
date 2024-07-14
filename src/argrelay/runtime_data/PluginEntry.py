from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.PluginSide import PluginSide


@dataclass(frozen = True)
class PluginEntry:
    plugin_enabled: bool = field()
    plugin_side: PluginSide = field()
    plugin_module_name: str = field()
    plugin_class_name: str = field()
    plugin_dependencies: list[str] = field()
    plugin_config: dict = field()
