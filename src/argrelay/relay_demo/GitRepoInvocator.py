import subprocess

from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_, envelope_id_, instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import invocator_plugin_id_


class GitRepoInvocator(AbstractInvocator):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)

    def populate_invocation_input(self, server_config: ServerConfig, interp_ctx: InterpContext) -> InvocationInput:

        assert interp_ctx.last_found_envelope_ipos >= 0, "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_envelope = interp_ctx.envelope_containers[0]
        invocator_plugin_id = function_envelope.data_envelope[instance_data_][invocator_plugin_id_]
        invocation_input = InvocationInput(
            invocator_plugin_entry = server_config.plugin_dict[invocator_plugin_id],
            data_envelopes = interp_ctx.get_data_envelopes(),
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.data_envelopes[0][envelope_id_] == "desc_repo":
            # The 2nd envelope (`DataEnvelopeSchema`) is supposed to have `envelope_payload` in its `envelope_payload`:
            repo_envelope = invocation_input.data_envelopes[1]
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
