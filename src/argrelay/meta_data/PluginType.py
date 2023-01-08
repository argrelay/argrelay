from enum import Enum, auto


class PluginType(Enum):
    LoaderPlugin = auto()
    InterpFactoryPlugin = auto()
    InvocatorPlugin = auto()

    def __str__(self):
        return self.name
