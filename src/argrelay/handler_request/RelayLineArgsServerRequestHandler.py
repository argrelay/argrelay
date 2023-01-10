from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.meta_data.CompType import CompType
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.InterpContext import is_found_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from argrelay.schema_config_interp.FunctionEnvelopePayloadSchema import invocator_plugin_id_
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc


class RelayLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server
        )

    def handle_request(self, input_ctx: InputContext) -> dict:
        assert input_ctx.comp_type == CompType.InvokeAction

        self.interpret_command(self.local_server, input_ctx)

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopePayloadSchema` for its `envelope_payload`:
        function_envelope = self.interp_ctx.assigned_types_to_values_per_envelope[0]
        if not function_envelope[is_found_]:
            # TODO: Think how to pass info about failure - customize ErrorInvocator:
            invocator_plugin_id = ErrorInvocator.__name__
        else:
            invocator_plugin_id = function_envelope[envelope_payload_][invocator_plugin_id_]
        invocator_plugin: AbstractInvocator = self.local_server.server_config.action_invocators[invocator_plugin_id]
        invocation_input: InvocationInput = invocator_plugin.populate_invocation_input(
            self.local_server.server_config,
            self.interp_ctx,
        )
        response_dict = invocation_input_desc.dict_schema.dump(invocation_input)
        return response_dict
