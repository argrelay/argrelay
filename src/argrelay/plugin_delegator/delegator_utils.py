"""
"""
from __future__ import annotations

from typing import Callable, Any, Union

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.plugin_config.ConfiguratorAbstract import ConfiguratorAbstract
from argrelay.runtime_data.AssignedValue import AssignedValue


def set_default_to(
    prop_name,
    prop_value,
    envelope_container,
) -> bool:
    """
    Assign a default `prop_value` to the given `prop_name`:
    *   Ensure that this `prop_name` is valid for `envelope_container`.
    *   Ensure that this `prop_value` is actually one of the remaining ones.
    """

    if prop_name in envelope_container.search_control.types_to_keys_dict:
        if prop_name not in envelope_container.assigned_types_to_values:
            if prop_name in envelope_container.remaining_types_to_values:
                if prop_value in envelope_container.remaining_types_to_values[prop_name]:
                    del envelope_container.remaining_types_to_values[prop_name]
                    envelope_container.assigned_types_to_values[prop_name] = AssignedValue(
                        prop_value,
                        ArgSource.DefaultValue,
                    )
                    return True
        else:
            # Setting `ArgSource.DefaultValue`: it cannot override any, right? No point to handle assigned case:
            pass
    return False


def get_config_value_once(
    server_configurators,
    value_getter: Callable[[ConfiguratorAbstract], Any],
    default_value: Any,
) -> Any:
    config_value: Union[Any, None] = None
    server_configurator: ConfiguratorAbstract
    for server_configurator in server_configurators.values():
        if config_value is None:
            config_value = value_getter(server_configurator)
        else:
            if value_getter(server_configurator) is not None:
                # Only one `PluginType.ConfiguratorPlugin` providing
                # same type of value is supported to avoid confusion:
                raise RuntimeError

    if config_value is None:
        config_value = default_value
    return config_value
