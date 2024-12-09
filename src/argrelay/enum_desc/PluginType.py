from enum import Enum

from argrelay.enum_desc.PluginSide import PluginSide


class PluginType(Enum):
    """
    See `AbstractPlugin.get_plugin_type`.
    """

    LoaderPlugin = PluginSide.PluginServerSideOnly
    """
    See classes derived from `AbstractLoader`.
    """

    InterpFactoryPlugin = PluginSide.PluginServerSideOnly
    """
    See classes derived from `AbstractInterpFactory`.
    """

    DelegatorPlugin = PluginSide.PluginServerSideOnly
    """
    See classes derived from `DelegatorAbstract`.

    Note that this plugin also implements client-side logic
    but it is not instantiated on the client-side -
    instead, static method is called directly on the plugin class.
    """

    ConfiguratorPlugin = PluginSide.PluginServerSideOnly
    """
    See `ConfiguratorAbstract`.
    """

    CheckEnvPlugin = PluginSide.PluginClientSideOnly
    """
    See classes derived from `PluginCheckEnvAbstract`.
    """

    def __new__(
        cls,
        plugin_side: PluginSide,
    ):
        enum_value = len(cls.__members__) + 1
        enum_obj = object.__new__(cls)
        enum_obj._value_ = enum_value
        return enum_obj

    def __init__(
        self,
        plugin_side: PluginSide,
    ):
        self.plugin_side = plugin_side

    def __str__(self):
        return self.name
