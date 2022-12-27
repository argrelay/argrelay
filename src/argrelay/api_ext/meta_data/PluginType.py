from enum import Enum

from argrelay.api_ext.relay_server.AbstractInterpFactory import AbstractInterpFactory
from argrelay.api_ext.relay_server.AbstractLoader import AbstractLoader


class PluginType(Enum):
    LoaderPlugin = AbstractLoader
    InterpFactoryPlugin = AbstractInterpFactory

    def __str__(self):
        return self.name
