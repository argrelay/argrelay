import sys

from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class ErrorInvocator(AbstractInvocator):

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:
        invocator_plugin_entry = server_config.plugin_dict[self.__class__.__name__]
        data_envelopes = interp_ctx.get_data_envelopes()
        invocation_input = InvocationInput(
            invocator_plugin_entry = invocator_plugin_entry,
            data_envelopes = data_envelopes,
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        # TODO: Make `ErrorInvocator` customizable to throw configured errors - as of now, it's a stub:
        sys.exit("INFO: command executed: this is a stub")
