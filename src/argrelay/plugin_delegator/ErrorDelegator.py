import sys

from argrelay.misc_helper import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_data_envelopes
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_message_, error_code_
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext


class ErrorDelegator(AbstractDelegator):

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        delegator_plugin_entry = local_server.server_config.plugin_dict[self.__class__.__name__]
        data_envelopes = get_data_envelopes(interp_ctx)
        invocation_input = InvocationInput(
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            delegator_plugin_entry = delegator_plugin_entry,
            data_envelopes = data_envelopes,
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
