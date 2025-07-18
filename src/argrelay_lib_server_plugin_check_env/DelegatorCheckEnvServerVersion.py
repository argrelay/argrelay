from __future__ import annotations

import argrelay
from argrelay_api_plugin_server_abstract.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.CheckEnvField import CheckEnvField
from argrelay_lib_root.enum_desc.CheckEnvFunc import CheckEnvFunc
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_server_plugin_check_env.DelegatorCheckEnvBase import (
    DelegatorCheckEnvBase,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
    search_control_list_,
)


class DelegatorCheckEnvServerVersion(DelegatorCheckEnvBase):
    """
    Implements `CheckEnvFunc.func_id_get_server_argrelay_version` for FS_36_17_84_44 `check_env`.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [
            {
                instance_data_: {
                    func_id_: CheckEnvFunc.func_id_get_server_argrelay_version.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: (
                    CheckEnvFunc.func_id_get_server_argrelay_version.name
                ),
                ReservedPropName.func_state.name: FuncState.fs_alpha.name,
                ReservedPropName.func_id.name: CheckEnvFunc.func_id_get_server_argrelay_version.name,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == CheckEnvFunc.func_id_get_server_argrelay_version.name

        server_version = argrelay.__version__
        custom_plugin_data = {
            CheckEnvField.server_version.name: server_version,
        }

        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry=local_server.plugin_config.server_plugin_instances[
                self.plugin_instance_id
            ],
            custom_plugin_data=custom_plugin_data,
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == CheckEnvFunc.func_id_get_server_argrelay_version.name

        print(
            f"{invocation_input.custom_plugin_data[CheckEnvField.server_version.name]}"
        )
