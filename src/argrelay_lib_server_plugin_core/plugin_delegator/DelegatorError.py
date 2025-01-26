from argrelay_api_plugin_server_abstract.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.ClientExitCode import ClientExitCode
from argrelay_lib_root.misc_helper_common import eprint
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaCustomDataDelegatorError import (
    error_code_,
    error_message_,
)


class DelegatorError(DelegatorSingleFuncAbstract):
    """
    This delegator is routed to and invoked on the client side to report an error.

    There is no error `func_id` for DelegatorError (unlike for many other delegators), at least for now.
    Instead, other delegators can override themselves and provide error info to use it by the client.
    """

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
            self.plugin_instance_id
        ]
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = delegator_plugin_entry,
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        error_message = "ERROR: unknown error"
        error_code = ClientExitCode.GeneralError.value
        if invocation_input.custom_plugin_data:
            if error_message_ in invocation_input.custom_plugin_data:
                error_message = invocation_input.custom_plugin_data[error_message_]
            if error_code_ in invocation_input.custom_plugin_data:
                error_code = invocation_input.custom_plugin_data[error_code_]
        eprint(error_message)
        exit(error_code)
