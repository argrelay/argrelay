from dataclasses import dataclass

from argrelay.runtime_data.PluginEntry import PluginEntry


@dataclass
class InvocationInput:
    """
    See :class:`InvocationInputSchema`
    """

    invocator_plugin_entry: PluginEntry

    data_envelopes: list

    extra_data: dict
