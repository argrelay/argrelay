from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.value_constants import goto_host_funct_, goto_service_funct_
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import InterpContext, function_envelope_ipos_
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_

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
        func_data_envelope = envelope_containers[function_envelope_ipos_].data_envelope
        func_name = func_data_envelope[envelope_id_]
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
        else:
            raise RuntimeError

    def run_invoke_control(
        self,
        server_config: ServerConfig,
        interp_ctx: InterpContext,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        # Redirect to `ErrorInvocator`:
        invocator_plugin_id = ErrorInvocator.__name__
        invocation_input = InvocationInput(
            invocator_plugin_entry = server_config.plugin_dict[invocator_plugin_id],
            data_envelopes = interp_ctx.get_data_envelopes(),
            custom_plugin_data = {},
        )
        return invocation_input
