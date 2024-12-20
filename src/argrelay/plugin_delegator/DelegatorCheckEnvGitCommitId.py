from __future__ import annotations

from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.enum_desc.CheckEnvFunc import CheckEnvFunc
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_delegator.DelegatorCheckEnvBase import DelegatorCheckEnvBase
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


class DelegatorCheckEnvGitCommitId(DelegatorCheckEnvBase):
    """
    Implements `CheckEnvFunc.func_id_get_server_project_git_commit_id` for FS_36_17_84_44 `check_env`.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [
            {
                instance_data_: {
                    func_id_: CheckEnvFunc.func_id_get_server_project_git_commit_id.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: (
                    CheckEnvFunc.func_id_get_server_project_git_commit_id.name
                ),
                ReservedPropName.func_state.name: FuncState.fs_alpha.name,
                ReservedPropName.func_id.name: CheckEnvFunc.func_id_get_server_project_git_commit_id.name,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == CheckEnvFunc.func_id_get_server_project_git_commit_id.name

        project_git_commit_id: str = get_config_value_once(
            self.server_config.server_configurators,
            lambda server_configurator: server_configurator.provide_project_git_commit_id(),
            None,
        )
        custom_plugin_data = {
            CheckEnvField.server_git_commit_id.name: project_git_commit_id,
        }

        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                self.plugin_instance_id
            ],
            custom_plugin_data = custom_plugin_data,
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == CheckEnvFunc.func_id_get_server_project_git_commit_id.name

        print(f"{invocation_input.custom_plugin_data[CheckEnvField.server_git_commit_id.name]}")
