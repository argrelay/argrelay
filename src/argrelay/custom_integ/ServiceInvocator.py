from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.value_constants import (
    goto_host_funct_,
    goto_service_funct_,
    list_service_func_,
    list_host_func_,
)
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.plugin_invocator.AbstractInvocator import (
    AbstractInvocator,
    get_data_envelopes,
    get_func_name_from_container,
    get_func_name_from_envelope,
)
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import populate_query_dict
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.AssignedValue import AssignedValue

cluster_envelope_ipos_ = 1
host_envelope_ipos_ = 2
service_envelope_ipos_ = 2
access_envelope_ipos_ = 3


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


def redirect_to_error(interp_ctx, server_config):
    # Redirect to `ErrorInvocator`:
    invocator_plugin_id = ErrorInvocator.__name__
    invocation_input = InvocationInput(
        invocator_plugin_entry = server_config.plugin_dict[invocator_plugin_id],
        data_envelopes = get_data_envelopes(interp_ctx.envelope_containers),
        custom_plugin_data = {},
    )
    return invocation_input


class ServiceInvocator(AbstractInvocator):

    def __init__(
        self,
        config_dict: dict,
    ):
        super().__init__(config_dict)

    def run_fill_control(
        self,
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        func_name = get_func_name_from_container(envelope_containers)
        if func_name in [
            goto_host_funct_,
            goto_service_funct_,
        ]:
            if curr_container_ipos == access_envelope_ipos_:
                cluster_envelope = envelope_containers[cluster_envelope_ipos_].data_envelope
                access_container = envelope_containers[access_envelope_ipos_]
                code_arg_type = ServiceArgType.CodeMaturity.name
                if code_arg_type in cluster_envelope:
                    code_arg_val = cluster_envelope[code_arg_type]
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
        local_server: LocalServer,
        interp_ctx: InterpContext,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        func_name = get_func_name_from_container(interp_ctx.envelope_containers)

        if func_name in [
            goto_host_funct_,
            goto_service_funct_,
        ]:
            return redirect_to_error(
                interp_ctx,
                local_server.server_config,
            )
        elif func_name in [
            list_host_func_,
            list_service_func_,
        ]:
            vararg_data_envelope_ipos = host_envelope_ipos_
            assert vararg_data_envelope_ipos == host_envelope_ipos_ == service_envelope_ipos_
            if interp_ctx.curr_container_ipos >= host_envelope_ipos_:
                query_dict = populate_query_dict(interp_ctx.envelope_containers[vararg_data_envelope_ipos])
                invocator_plugin_id = ServiceInvocator.__name__

                invocation_input = InvocationInput(
                    invocator_plugin_entry = local_server.server_config.plugin_dict[invocator_plugin_id],
                    data_envelopes = (
                        # existing envelopes (until vararg one):
                        get_data_envelopes(interp_ctx.envelope_containers)[:vararg_data_envelope_ipos]
                        +
                        # all envelopes in vararg set:
                        local_server.get_query_engine().query_data_envelopes(query_dict)
                    ),
                    custom_plugin_data = {},
                )
                return invocation_input
            else:
                return redirect_to_error(
                    interp_ctx,
                    local_server.server_config,
                )
        else:
            raise RuntimeError

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        func_name = get_func_name_from_envelope(invocation_input.data_envelopes)
        if func_name == list_host_func_:
            for data_envelope in invocation_input.data_envelopes[host_envelope_ipos_:]:
                print(data_envelope)
        if func_name == list_service_func_:
            for data_envelope in invocation_input.data_envelopes[service_envelope_ipos_:]:
                print(data_envelope)
        else:
            raise RuntimeError
