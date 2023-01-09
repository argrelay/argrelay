from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc


class NoopInvocator(AbstractInvocator):

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:
        invocation_input = InvocationInput(
            invocator_plugin_entry = server_config.plugin_dict[self.__class__.__name__],
            function_envelope = data_envelope_desc.dict_example,
            assigned_types_to_values_per_envelope = [],
            interp_result = {},
            extra_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        # Do nothing:
        pass
