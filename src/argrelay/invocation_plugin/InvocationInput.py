from dataclasses import dataclass

from argrelay.meta_data.PluginEntry import PluginEntry


@dataclass
class InvocationInput:
    """
    See :class:`InvocationInputSchema`
    """

    invocator_plugin_entry: PluginEntry

    # TODO: make it clear that it is function object wrapper/meta (including payload), not just function object payload:
    function_object: dict

    assigned_types_to_values_per_object: list

    interp_result: dict

    extra_data: dict

