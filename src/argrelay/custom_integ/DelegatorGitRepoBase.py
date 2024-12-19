from __future__ import annotations

from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

repo_container_ipos_ = 1

repo_root_abs_path_: str = "repo_root_abs_path"


class DelegatorGitRepoBase(DelegatorSingleFuncAbstract):
    """
    Implements base functionality for FS_67_16_61_97 git_plugin.
    """

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.class_function` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_container = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_container.data_envelopes[0][instance_data_]
            [delegator_plugin_instance_id_]
        )
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input
