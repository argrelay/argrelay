from argrelay.enum_desc.CompType import CompType

from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import invocator_plugin_id_
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc


class RelayLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server,
        )

    def handle_request(self, input_ctx: InputContext) -> dict:
        assert input_ctx.comp_type == CompType.InvokeAction

        self.interpret_command(self.local_server, input_ctx)
        ElapsedTime.measure("after_interpret_command")

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        if self.interp_ctx.last_found_envelope_ipos < 0:
            # TODO: Think how to pass info about failure - customize ErrorInvocator:
            invocator_plugin_id = ErrorInvocator.__name__
        else:
            invocator_plugin_id = self.interp_ctx.envelope_containers[0].data_envelope[
                instance_data_
            ][
                invocator_plugin_id_
            ]
        invocator_plugin: AbstractInvocator = self.local_server.server_config.action_invocators[invocator_plugin_id]
        invocation_input: InvocationInput = invocator_plugin.populate_invocation_input(
            self.local_server.server_config,
            self.interp_ctx,
        )
        response_dict = invocation_input_desc.dict_schema.dump(invocation_input)
        return response_dict
