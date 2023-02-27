from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc


class NoopInvocator(AbstractInvocator):

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        invocation_input = InvocationInput(
            invocator_plugin_entry = local_server.server_config.plugin_dict[self.__class__.__name__],
            data_envelopes = [
                data_envelope_desc.dict_example,
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        # Do nothing:
        pass
