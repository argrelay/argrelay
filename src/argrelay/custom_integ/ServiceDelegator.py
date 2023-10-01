from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.value_constants import (
    goto_host_funct_,
    goto_service_funct_,
    list_service_func_,
    list_host_func_,
)
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.plugin_delegator.AbstractDelegator import (
    AbstractDelegator,
    get_func_name,
    get_func_name_from_containers,
)
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import (
    error_message_,
    error_code_,
    error_delegator_custom_data_desc,
    error_delegator_stub_custom_data_example,
)
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import populate_query_dict
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_response.InvocationInput import InvocationInput

host_container_ipos_ = 1
service_container_ipos_ = 1
access_container_ipos_ = 2


def set_default_to(arg_type, arg_val, envelope_container):
    if arg_type in envelope_container.search_control.types_to_keys_dict.keys():
        if arg_type not in envelope_container.assigned_types_to_values.keys():
            if arg_type in envelope_container.remaining_types_to_values:
                if arg_val in envelope_container.remaining_types_to_values[arg_type]:
                    del envelope_container.remaining_types_to_values[arg_type]
                    envelope_container.assigned_types_to_values[arg_type] = AssignedValue(
                        arg_val,
                        ArgSource.DefaultValue,
                    )
        else:
            # Setting `ArgSource.DefaultValue`: it cannot override any, right? No point to handle assigned case:
            pass


def redirect_to_no_func_error(
    interp_ctx,
    server_config,
):
    return redirect_to_error(
        interp_ctx,
        server_config,
        "ERROR: objects cannot be searched until function is fully qualified",
        1,
    )


def redirect_to_error(
    interp_ctx,
    server_config,
    error_message,
    error_code,
):
    # Redirect to `ErrorDelegator`:
    delegator_plugin_instance_id = ErrorDelegator.__name__
    custom_plugin_data = {
        error_message_: error_message,
        error_code_: error_code,
    }
    error_delegator_custom_data_desc.validate_dict(custom_plugin_data)
    invocation_input = InvocationInput(
        all_tokens = interp_ctx.parsed_ctx.all_tokens,
        consumed_tokens = interp_ctx.consumed_tokens,
        envelope_containers = interp_ctx.envelope_containers,
        tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
        tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
        delegator_plugin_entry = server_config.plugin_dict[delegator_plugin_instance_id],
        custom_plugin_data = custom_plugin_data,
    )
    return invocation_input


class ServiceDelegator(AbstractDelegator):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )

    def run_fill_control(
        self,
        interp_ctx: "InterpContext",
    ):
        func_name = get_func_name(interp_ctx)
        if func_name in [
            goto_host_funct_,
            goto_service_funct_,
        ]:
            assert host_container_ipos_ == service_container_ipos_
            object_container_ipos = host_container_ipos_

            # If need to specify `AccessType` `data_envelope`:
            if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + access_container_ipos_:
                # Take object found so far:
                data_envelope = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + object_container_ipos
                )].data_envelopes[0]

                access_container = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + access_container_ipos_
                )]

                # Select default value to search `AccessType` `data_envelope` based on `CodeMaturity`:
                code_arg_type = ServiceArgType.CodeMaturity.name
                if code_arg_type in data_envelope:
                    code_arg_val = data_envelope[code_arg_type]
                    if code_arg_val == "prod":
                        set_default_to(ServiceArgType.AccessType.name, "ro", access_container)
                    else:
                        set_default_to(ServiceArgType.AccessType.name, "rw", access_container)

        elif func_name in [
            list_host_func_,
            list_service_func_,
        ]:
            pass
        else:
            raise RuntimeError

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        func_name = get_func_name(interp_ctx)

        vararg_container_ipos = host_container_ipos_
        assert vararg_container_ipos == host_container_ipos_ == service_container_ipos_

        if func_name in [
            goto_host_funct_,
            goto_service_funct_,
        ]:
            # Even if these functions do not support varargs, when `redirect_to_error`, query all:
            vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]
            query_dict = populate_query_dict(vararg_container)
            vararg_container.data_envelopes = local_server.get_query_engine().query_data_envelopes(query_dict)

            # Actual implementation is not defined for demo:
            return redirect_to_error(
                interp_ctx,
                local_server.server_config,
                error_delegator_stub_custom_data_example[error_message_],
                error_delegator_stub_custom_data_example[error_code_],
            )
        elif func_name in [
            list_host_func_,
            list_service_func_,
        ]:
            # Verify that func is selected and all what is left to do is to query 0...N objects:
            if interp_ctx.curr_container_ipos >= vararg_container_ipos:
                # Search `data_envelope`-s based on existing args on command line:
                vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]
                query_dict = populate_query_dict(vararg_container)
                vararg_container.data_envelopes = local_server.get_query_engine().query_data_envelopes(query_dict)

                # Plugin to invoke on client side:
                delegator_plugin_instance_id = ServiceDelegator.__name__
                # Package into `InvocationInput` payload object:
                invocation_input = InvocationInput(
                    all_tokens = interp_ctx.parsed_ctx.all_tokens,
                    consumed_tokens = interp_ctx.consumed_tokens,
                    envelope_containers = interp_ctx.envelope_containers,
                    tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
                    tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
                    delegator_plugin_entry = local_server.server_config.plugin_dict[delegator_plugin_instance_id],
                    custom_plugin_data = {},
                )
                return invocation_input
            else:
                return redirect_to_no_func_error(
                    interp_ctx,
                    local_server.server_config,
                )
        else:
            # Plugin is given a function name it does not know:
            raise RuntimeError

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        """
        Print `data_envelope`-s received from server on client side.
        """

        func_name = get_func_name_from_containers(invocation_input.envelope_containers)
        if func_name == list_host_func_:
            for data_envelope in invocation_input.envelope_containers[host_container_ipos_].data_envelopes:
                print(data_envelope)
        elif func_name == list_service_func_:
            for data_envelope in invocation_input.envelope_containers[service_container_ipos_].data_envelopes:
                print(data_envelope)
        else:
            raise RuntimeError
