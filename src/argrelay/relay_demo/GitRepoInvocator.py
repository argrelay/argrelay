import subprocess

from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_, envelope_id_
from argrelay.schema_config_interp.FunctionEnvelopePayloadSchema import invocator_plugin_id_


class GitRepoInvocator(AbstractInvocator):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:

        assert interp_ctx.last_found_envelope_ipos >= 0, "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopePayloadSchema` for its `envelope_payload`:
        function_envelope = interp_ctx.assigned_types_to_values_per_envelope[0]
        invocator_plugin_id = function_envelope[envelope_payload_][invocator_plugin_id_]
        invocation_input = InvocationInput(
            invocator_plugin_entry = server_config.plugin_dict[invocator_plugin_id],
            function_envelope = function_envelope,
            assigned_types_to_values_per_envelope = interp_ctx.assigned_types_to_values_per_envelope,
            interp_result = {},
            extra_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.function_envelope[envelope_id_] == "desc_repo":
            # The 2nd envelope (`DataEnvelopeSchema`) is supposed to have `envelope_payload` in its `envelope_payload`:
            repo_envelope = invocation_input.assigned_types_to_values_per_envelope[1]
            abs_repo_path = repo_envelope[envelope_payload_]["abs_repo_path"]
            # List Git repo dir:
            subproc = subprocess.run(
                [
                    "ls",
                    "-lrt",
                    abs_repo_path,
                ],
            )
            ret_code = subproc.returncode
            if ret_code != 0:
                raise RuntimeError
