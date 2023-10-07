from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_response.InterpResult import InterpResult


@dataclass
class InvocationInput(InterpResult):
    """
    See also :class:`InvocationInputSchema`.

    Unlike `InterpResult` this class provides full list of `data_envelopes`
    because invocation is not latency-sensitive.

    Both `InterpResult` and `InvocationInput` might be combined in the future.
    """

    delegator_plugin_entry: PluginEntry = field()
    """
    The `PluginEntry` taken from config on the server side to let client invoke that plugin.

    It is assumed that server and client code, if not of the same version, at least, compatible.
    """

    custom_plugin_data: dict = field()
    """
    A placeholder dict for exclusive use by plugin.

    Whatever plugin server side needs to tell its plugin peer on the client side.
    """
