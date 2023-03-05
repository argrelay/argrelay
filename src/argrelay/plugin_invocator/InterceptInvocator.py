from __future__ import annotations

from argrelay.custom_integ.DemoInterpFactory import DemoInterpFactory
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator, get_data_envelopes
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_envelope_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_, instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import invocator_plugin_instance_id_


class InterceptInvocator(AbstractInvocator):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )

    def run_search_control(
        self,
        function_data_envelope: dict,
    ) -> list[SearchControl]:
        # Nothing to search (only if next interpreter needs more, but this one is done):
        return []

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> str:
        # TODO: make it configurable:
        return DemoInterpFactory.__name__

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        # TODO: Fail (send to ErrorInvocator) if next function is not specified -
        #       showing the payload in this case is misleading.
        function_envelope = interp_ctx.envelope_containers[function_envelope_ipos_]
        invocator_plugin_instance_id = function_envelope.data_envelope[instance_data_][invocator_plugin_instance_id_]
        invocation_input = InvocationInput(
            invocator_plugin_entry = local_server.server_config.plugin_dict[invocator_plugin_instance_id],
            data_envelopes = get_data_envelopes(interp_ctx),
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.data_envelopes[function_envelope_ipos_][envelope_id_] == SpecialFunc.intercept_func.name:
            # TODO: Print without first function `data_envelope` belonging to `intercept` function:
            print(invocation_input)
