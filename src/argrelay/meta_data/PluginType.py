from enum import Enum

from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.loader_plugin.AbstractLoader import AbstractLoader


class PluginType(Enum):
    LoaderPlugin = AbstractLoader
    InterpFactoryPlugin = AbstractInterpFactory

    def __str__(self):
        return self.name
