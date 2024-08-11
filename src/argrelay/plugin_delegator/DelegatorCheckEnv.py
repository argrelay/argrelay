from __future__ import annotations

import argrelay
from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.enum_desc.CheckEnvFunc import CheckEnvFunc
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.AbstractDelegator import (
    AbstractDelegator,
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_delegator.delegator_utils import get_config_value_once
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    func_id_,
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_response.InvocationInput import InvocationInput


class DelegatorCheckEnv(AbstractDelegator):
    """
    Implements functions used by FS_36_17_84_44 `check_env`.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [
            {
                instance_data_: {
                    func_id_: CheckEnvFunc.func_id_get_server_argrelay_version.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: (
                    CheckEnvFunc.func_id_get_server_argrelay_version.name
                ),
                ReservedPropName.func_state.name: FuncState.fs_alpha.name,
                ReservedPropName.func_id.name: CheckEnvFunc.func_id_get_server_argrelay_version.name,
            },
            {
                instance_data_: {
                    func_id_: CheckEnvFunc.func_id_get_server_project_git_commit_id.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: (
                    CheckEnvFunc.func_id_get_server_project_git_commit_id.name
                ),
                ReservedPropName.func_state.name: FuncState.fs_alpha.name,
                ReservedPropName.func_id.name: CheckEnvFunc.func_id_get_server_project_git_commit_id.name,
            },
            {
                instance_data_: {
                    func_id_: CheckEnvFunc.func_id_get_server_start_time.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: (
                    CheckEnvFunc.func_id_get_server_start_time.name
                ),
                ReservedPropName.func_state.name: FuncState.fs_alpha.name,
                ReservedPropName.func_id.name: CheckEnvFunc.func_id_get_server_start_time.name,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        custom_plugin_data = {}

        if func_id == CheckEnvFunc.func_id_get_server_argrelay_version.name:
            server_version = argrelay.__version__
            custom_plugin_data = {
                CheckEnvField.server_version.name: server_version,
            }

        if func_id == CheckEnvFunc.func_id_get_server_project_git_commit_id.name:
            project_git_commit_id: str = get_config_value_once(
                self.server_config.server_configurators,
                lambda server_configurator: server_configurator.provide_project_git_commit_id(),
                None,
            )
            custom_plugin_data = {
                CheckEnvField.server_git_commit_id.name: project_git_commit_id,
            }

        if func_id == CheckEnvFunc.func_id_get_server_start_time.name:
            server_start_time: int = local_server.server_start_time
            custom_plugin_data = {
                CheckEnvField.server_start_time.name: server_start_time,
            }

        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.plugin_instance_entries[
                self.plugin_instance_id
            ],
            custom_plugin_data = custom_plugin_data,
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        func_id = get_func_id_from_invocation_input(invocation_input)

        if func_id == CheckEnvFunc.func_id_get_server_project_git_commit_id.name:
            print(f"{invocation_input.custom_plugin_data['project_git_commit_id']}")

        if func_id == CheckEnvFunc.func_id_get_server_start_time.name:
            print(f"{invocation_input.custom_plugin_data['server_start_time']}")
