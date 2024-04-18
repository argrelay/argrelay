from __future__ import annotations

from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    func_id_,
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_response.InvocationInput import InvocationInput


class EchoDelegator(AbstractDelegator):
    """
    Implements FS_43_50_57_71 `echo_args` func.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.echo_args_func.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: (
                f"Print command line args `{InvocationInput.__name__}`"
            ),
            ReservedArgType.FuncId.name: SpecialFunc.echo_args_func.name,
        }]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                self.plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        print(" ".join(invocation_input.all_tokens))
