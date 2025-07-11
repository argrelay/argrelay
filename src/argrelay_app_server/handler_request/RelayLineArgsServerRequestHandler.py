from argrelay_api_plugin_server_abstract.DelegatorAbstract import DelegatorAbstract
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_api_server_cli.schema_response.InvocationInputSchema import (
    invocation_input_desc,
)
from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_server.handler_request.AbstractServerRequestHandler import (
    AbstractServerRequestHandler,
)
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import function_container_ipos_
from argrelay_lib_root.enum_desc.ClientExitCode import ClientExitCode
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorError import (
    DelegatorError,
)
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaCustomDataDelegatorError import (
    error_code_,
    error_delegator_custom_data_desc,
    error_message_,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
)


class RelayLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server=local_server,
        )

    def handle_request(
        self,
        call_ctx: CallContext,
    ) -> dict:
        assert call_ctx.server_action is ServerAction.RelayLineArgs
        self._store_usage_stats_entry(call_ctx)

        self.interpret_command(self.local_server, call_ctx)
        ElapsedTime.measure("after_interpret_command")
        is_error = False
        error_message = ""
        error_code = ClientExitCode.ClientSuccess.value

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.class_function` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        if self.interp_ctx.is_func_found():
            delegator_plugin_instance_id = self.interp_ctx.envelope_containers[
                function_container_ipos_
            ].data_envelopes[0][instance_data_][delegator_plugin_instance_id_]
        else:
            is_error = True
            error_message = "ERROR: Function is not selected, try help, or press Tab to complete selection."
            error_code = ClientExitCode.GeneralError.value
            # TODO: TODO_62_75_33_41: Do not hardcode plugin instance id (instance of `DelegatorError`):
            delegator_plugin_instance_id = f"{DelegatorError.__name__}.default"

        delegator_plugin: DelegatorAbstract = (
            self.local_server.server_config.action_delegators[
                delegator_plugin_instance_id
            ]
        )
        invocation_input: InvocationInput = delegator_plugin.run_invoke_control(
            self.interp_ctx,
            self.local_server,
        )

        if is_error:
            invocation_input.custom_plugin_data = {
                error_message_: error_message,
                error_code_: error_code,
            }
            error_delegator_custom_data_desc.validate_dict(
                invocation_input.custom_plugin_data
            )

        response_dict = invocation_input_desc.dict_schema.dump(invocation_input)
        return response_dict
