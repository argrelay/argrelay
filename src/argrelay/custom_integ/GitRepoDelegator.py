from __future__ import annotations

import subprocess

from argrelay.custom_integ.value_constants import goto_repo_func_, desc_commit_func_
from argrelay.misc_helper import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_, envelope_id_, instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import delegator_plugin_instance_id_
from argrelay.schema_response.InvocationInput import InvocationInput

repo_container_ipos_ = 1


class GitRepoDelegator(AbstractDelegator):
    """
    Implements FS_67_16_61_97 git_plugin.
    """

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
        function_container = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_container.data_envelopes[0][instance_data_]
            [delegator_plugin_instance_id_]
        )
        invocation_input = InvocationInput(
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
            delegator_plugin_entry = local_server.server_config.plugin_dict[delegator_plugin_instance_id],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if (
            invocation_input
                .envelope_containers[function_container_ipos_]
                .data_envelopes[0][envelope_id_]
            == goto_repo_func_
        ):
            repo_envelope = invocation_input.envelope_containers[repo_container_ipos_].data_envelopes[0]
            repo_root_abs_path = repo_envelope[envelope_payload_][repo_root_abs_path_]
            eprint(f"INFO: starting subshell in: {repo_root_abs_path}")
            # List Git repo dir:
            subproc = subprocess.run(
                [
                    "bash",
                    "-l",
                ],
                cwd = repo_root_abs_path
            )
            ret_code = subproc.returncode
            if ret_code != 0:
                raise RuntimeError
        if (
            invocation_input
                .envelope_containers[function_container_ipos_]
                .data_envelopes[0][envelope_id_]
            == desc_commit_func_
        ):
            raise RuntimeError("not implemented")


repo_root_abs_path_: str = "repo_root_abs_path"
