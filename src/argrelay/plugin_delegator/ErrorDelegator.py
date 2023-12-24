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
            self.__class__.__name__
        ]
        invocation_input = InvocationInput(
            arg_values = interp_ctx.comp_suggestions,
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
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
