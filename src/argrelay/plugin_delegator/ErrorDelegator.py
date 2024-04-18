import sys

from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_message_, error_code_
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_response.InvocationInput import InvocationInput


class ErrorDelegator(AbstractDelegator):

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
            self.plugin_instance_id
        ]
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = delegator_plugin_entry,
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        error_message = "ERROR: unknown error"
        error_code = 1
        if invocation_input.custom_plugin_data:
            if error_message_ in invocation_input.custom_plugin_data:
                error_message = invocation_input.custom_plugin_data[error_message_]
            if error_code_ in invocation_input.custom_plugin_data:
                error_code = invocation_input.custom_plugin_data[error_code_]
        eprint(error_message)
        sys.exit(error_code)
