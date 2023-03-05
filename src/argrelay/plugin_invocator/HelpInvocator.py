from __future__ import annotations

from argrelay.custom_integ.DemoInterpFactory import DemoInterpFactory
from argrelay.custom_integ.ServiceInvocator import redirect_to_no_func_error
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_invocator.AbstractInvocator import get_data_envelopes
from argrelay.plugin_invocator.InterceptorInvocator import InterceptorInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import populate_query_dict
from argrelay.runtime_context.InterpContext import function_envelope_ipos_, InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_

subsequent_function_envelope_ipos_ = function_envelope_ipos_ + 1

# TODO: It inherits `InterceptorInvocator`, but it makes more sense to have common base class instead.
class HelpInvocator(InterceptorInvocator):

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> str:
        # TODO: This must be special interpreter which is configured only to search functions (without their args).
        # TODO: make it configurable:
        return DemoInterpFactory.__name__

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        if interp_ctx.curr_container_ipos >= subsequent_function_envelope_ipos_:
            query_dict = populate_query_dict(interp_ctx.envelope_containers[(
                subsequent_function_envelope_ipos_
            )])
            invocator_plugin_instance_id = HelpInvocator.__name__
            invocation_input = InvocationInput(
                invocator_plugin_entry = local_server.server_config.plugin_dict[invocator_plugin_instance_id],
                data_envelopes = (
                    # Envelope of `SpecialFunc.help_func`:
                    get_data_envelopes(interp_ctx)[:subsequent_function_envelope_ipos_]
                    +
                    # These must be function envelopes found via query:
                    local_server.get_query_engine().query_data_envelopes(query_dict)
                ),
                custom_plugin_data = {},
            )
            return invocation_input
        else:
            return redirect_to_no_func_error(
                interp_ctx,
                local_server.server_config,
            )

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.data_envelopes[function_envelope_ipos_][envelope_id_] == SpecialFunc.help_func.name:
            for data_envelope in invocation_input.data_envelopes[function_envelope_ipos_:]:
                print(data_envelope)
