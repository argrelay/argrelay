from dataclasses import dataclass

from argrelay.runtime_data.PluginEntry import PluginEntry


@dataclass
class InvocationInput:
    """
    See :class:`InvocationInputSchema`
    """

    invocator_plugin_entry: PluginEntry
    """
    The `PluginEntry` taken from config on the server side to let client invoke that plugin.

    It is assumed that server and client code, if not of the same version, at least, compatible.
    """

    data_envelopes: list
    """
    Envelopes copied from `InterpContext` at the end of command line interpretation on the server side.
    """

    custom_plugin_data: dict
    """
    A placeholder dict for exclusive use by plugin.

    Whatever plugin server side needs to tell its plugin peer on the client side.
    """
