from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import (
    error_message_,
    error_delegator_custom_data_desc,
    error_code_,
)
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import function_container_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import delegator_plugin_instance_id_
from argrelay.schema_response.InvocationInput import InvocationInput
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec.CallContext import CallContext


class RelayLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server,
        )

    def handle_request(
        self,
        call_ctx: CallContext,
    ) -> dict:
        assert call_ctx.server_action is ServerAction.RelayLineArgs

        self.interpret_command(self.local_server, call_ctx)
        ElapsedTime.measure("after_interpret_command")
        is_error = False
        error_message = ""
        error_code = 0

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        if self.interp_ctx.is_func_found():
            delegator_plugin_instance_id = (
                self
                .interp_ctx
                .envelope_containers[function_container_ipos_]
                .data_envelopes[0][instance_data_][delegator_plugin_instance_id_]
            )
        else:
            is_error = True
            error_message = "ERROR: Function is not selected, try help, or press Tab to complete selection."
            error_code = 1
            # TODO: Do not hardcode plugin id (instance of `ErrorDelegator`):
            delegator_plugin_instance_id = f"{ErrorDelegator.__name__}.default"

        delegator_plugin: AbstractDelegator = self.local_server.server_config.action_delegators[
            delegator_plugin_instance_id
        ]
        invocation_input: InvocationInput = delegator_plugin.run_invoke_control(
            self.interp_ctx,
            self.local_server,
        )

        if is_error:
            invocation_input.custom_plugin_data = {
                error_message_: error_message,
                error_code_: error_code,
            }
            error_delegator_custom_data_desc.validate_dict(invocation_input.custom_plugin_data)

        response_dict = invocation_input_desc.dict_schema.dump(invocation_input)
        return response_dict
