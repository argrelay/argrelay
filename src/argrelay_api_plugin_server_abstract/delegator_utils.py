"""
"""
from __future__ import annotations

from typing import (
    Any,
    Callable,
    Union,
)

from argrelay_api_plugin_server_abstract.ConfiguratorAbstract import ConfiguratorAbstract
from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_lib_root.enum_desc.ClientExitCode import ClientExitCode
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorError import DelegatorError
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaCustomDataDelegatorError import (
    error_code_,
    error_delegator_custom_data_desc,
    error_message_,
)
from argrelay_schema_config_server.runtime_data_server_plugin.PluginConfig import PluginConfig


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

    if prop_name in envelope_container.search_control.prop_name_to_arg_name_dict:
        if prop_name not in envelope_container.assigned_prop_name_to_prop_value:
            if prop_name in envelope_container.remaining_prop_name_to_prop_value:
                if prop_value in envelope_container.remaining_prop_name_to_prop_value[prop_name]:
                    del envelope_container.remaining_prop_name_to_prop_value[prop_name]
                    envelope_container.assigned_prop_name_to_prop_value[prop_name] = AssignedValue(
                        prop_value,
                        ValueSource.default_value,
                    )
                    return True
        else:
            # Setting `ValueSource.default_value`: it cannot override any, right? No point to handle assigned case:
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
    # Redirect to `DelegatorError`:
    # TODO: TODO_62_75_33_41: Do not hardcode plugin instance id (instance of `DelegatorError`):
    delegator_plugin_instance_id = f"{DelegatorError.__name__}.default"
    custom_plugin_data = {
        error_message_: error_message,
        error_code_: error_code,
    }
    error_delegator_custom_data_desc.validate_dict(custom_plugin_data)
    invocation_input = InvocationInput.with_interp_context(
        interp_ctx,
        delegator_plugin_entry = plugin_config.server_plugin_instances[delegator_plugin_instance_id],
        custom_plugin_data = custom_plugin_data,
    )
    return invocation_input


def redirect_to_not_disambiguated_error(
    interp_ctx,
    plugin_config,
    envelope_class,
):
    return redirect_to_error(
        interp_ctx,
        plugin_config,
        f"ERROR: `envelope_class` [{envelope_class}] is not fully qualified (not disambiguated)",
        ClientExitCode.GeneralError.value,
    )


def clean_prop_value(
    prop_value: str,
) -> str:
    if prop_value == SpecialChar.NoPropValue.value:
        return ""
    else:
        return prop_value
