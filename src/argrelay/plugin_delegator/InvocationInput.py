from __future__ import annotations

from dataclasses import dataclass

from argrelay.runtime_data.PluginEntry import PluginEntry


# TODO: Combine InterpResult and InvocationInput - only one need to exits
@dataclass
class InvocationInput:
    """
    See :class:`InvocationInputSchema`
    """

    all_tokens: list[str]
    """
    Copy from `ParsedContext.all_tokens` - command line args.
    """

    consumed_tokens: list[int]
    """
    Copy from `InterpContext.consumed_tokens` -
    indexes into `all_tokens` pointing to tokens consumed during interpretation.
    """

    delegator_plugin_entry: PluginEntry
    """
    The `PluginEntry` taken from config on the server side to let client invoke that plugin.

    It is assumed that server and client code, if not of the same version, at least, compatible.
    """

    data_envelopes: list[dict]
    """
    Envelopes copied from `InterpContext` at the end of command line interpretation on the server side.
    """

    custom_plugin_data: dict
    """
    A placeholder dict for exclusive use by plugin.

    Whatever plugin server side needs to tell its plugin peer on the client side.
    """
