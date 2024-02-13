from enum import Enum, auto


class PluginType(Enum):
    LoaderPlugin = auto()
    """
    See classes derived from `AbstractLoader`.
    """

    InterpFactoryPlugin = auto()
    """
    See classes derived from `AbstractInterpFactory`.
    """

    DelegatorPlugin = auto()
    """
    See classes derived from `AbstractLoader`.
    """

    ConfiguratorPlugin = auto()
    """
    See `AbstractConfigurator`.
    """

    def __str__(self):
        return self.name
