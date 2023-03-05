from argrelay.enum_desc.CompType import CompType

from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.ErrorInvocatorCustomDataSchema import (
    error_message_,
    error_invocator_custom_data_desc,
    error_code_,
)
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.InterpContext import function_envelope_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import invocator_plugin_instance_id_
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
        is_error = False
        error_message = ""
        error_code = 0

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        if self.interp_ctx.is_funct_found():
            invocator_plugin_instance_id = self.interp_ctx.envelope_containers[function_envelope_ipos_].data_envelope[
                instance_data_
            ][
                invocator_plugin_instance_id_
            ]
        else:
            is_error = True
            error_message = "ERROR: function is not selected"
            error_code = 1
            invocator_plugin_instance_id = ErrorInvocator.__name__

        invocator_plugin: AbstractInvocator = self.local_server.server_config.action_invocators[
            invocator_plugin_instance_id
        ]
        invocation_input: InvocationInput = invocator_plugin.run_invoke_control(
            self.interp_ctx,
            self.local_server,
        )

        if is_error:
            invocation_input.custom_plugin_data = {
                error_message_: error_message,
                error_code_: error_code,
            }
            error_invocator_custom_data_desc.validate_dict(invocation_input.custom_plugin_data)

        response_dict = invocation_input_desc.dict_schema.dump(invocation_input)
        return response_dict
