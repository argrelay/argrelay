from dataclasses import dataclass

from argrelay.meta_data.PluginEntry import PluginEntry


@dataclass
class InvocationInput:
    """
    See :class:`InvocationInputSchema`
    """

    invocator_plugin_entry: PluginEntry

    function_envelope: dict

    assigned_types_to_values_per_envelope: list

    interp_result: dict

    extra_data: dict
