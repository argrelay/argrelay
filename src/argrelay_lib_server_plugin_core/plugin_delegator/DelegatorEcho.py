from __future__ import annotations

from argrelay_api_plugin_server_abstract.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialFunc import SpecialFunc
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
    search_control_list_,
)


class DelegatorEcho(DelegatorSingleFuncAbstract):
    """
    Implements FS_43_50_57_71 `echo_args` func.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.func_id_echo_args.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: (
                f"Print command line args `{InvocationInput.__name__}`"
            ),
            ReservedPropName.func_state.name: FuncState.fs_beta.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_echo_args.name,
        }]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                self.plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        print(" ".join(invocation_input.all_tokens))
