import subprocess

from argrelay.custom_integ.value_constants import desc_repo_func_, desc_commit_func_
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_data_envelopes
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_envelope_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_, envelope_id_, instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import delegator_plugin_instance_id_

repo_envelope_ipos_ = 1


class GitRepoDelegator(AbstractDelegator):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_envelope = interp_ctx.envelope_containers[function_envelope_ipos_]
        delegator_plugin_instance_id = function_envelope.data_envelope[instance_data_][delegator_plugin_instance_id_]
        invocation_input = InvocationInput(
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            delegator_plugin_entry = local_server.server_config.plugin_dict[delegator_plugin_instance_id],
            data_envelopes = get_data_envelopes(interp_ctx),
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if invocation_input.data_envelopes[function_envelope_ipos_][envelope_id_] == desc_repo_func_:
            repo_envelope = invocation_input.data_envelopes[repo_envelope_ipos_]
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
        if invocation_input.data_envelopes[function_envelope_ipos_][envelope_id_] == desc_commit_func_:
            raise RuntimeError("not implemented")
