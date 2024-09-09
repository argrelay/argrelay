"""
"""
from __future__ import annotations

from typing import Callable, Any, Union

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.plugin_config.ConfiguratorAbstract import ConfiguratorAbstract
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import (
    error_message_,
    error_code_,
    error_delegator_custom_data_desc,
)
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.schema_response.InvocationInput import InvocationInput


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


def redirect_to_error(
    interp_ctx,
    plugin_config: PluginConfig,
    error_message,
    error_code,
):
    # Redirect to `ErrorDelegator`:
    # TODO: TODO_62_75_33_41: Do not hardcode plugin instance id (instance of `ErrorDelegator`):
    delegator_plugin_instance_id = f"{ErrorDelegator.__name__}.default"
    custom_plugin_data = {
        error_message_: error_message,
        error_code_: error_code,
    }
    error_delegator_custom_data_desc.validate_dict(custom_plugin_data)
    invocation_input = InvocationInput.with_interp_context(
        interp_ctx,
        delegator_plugin_entry = plugin_config.plugin_instance_entries[delegator_plugin_instance_id],
        custom_plugin_data = custom_plugin_data,
    )
    return invocation_input


def redirect_to_no_func_error(
    interp_ctx,
    plugin_config,
):
    return redirect_to_error(
        interp_ctx,
        plugin_config,
        "ERROR: objects cannot be searched until function is fully qualified",
        1,
    )
