from __future__ import annotations

import subprocess

from argrelay.custom_integ.DelegatorGitRepoBase import repo_root_abs_path_, DelegatorGitRepoBase
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoPropName import GitRepoPropName
from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_invocation_input
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput

func_id_goto_git_repo_ = "func_id_goto_git_repo"

repo_container_ipos_ = 1


class DelegatorGitRepoGotoRepo(DelegatorGitRepoBase):
    """
    Implements `func_id_goto_git_repo_` for FS_67_16_61_97 git_plugin.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        repo_search_control = populate_search_control(
            GitRepoEnvelopeClass.class_git_repo.name,
            {
                ReservedPropName.envelope_class.name: GitRepoEnvelopeClass.class_git_repo.name,
            },
            [
                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                {"class": ReservedPropName.envelope_class.name},

                {"category": GitRepoPropName.git_repo_object_category.name},
                {"alias": GitRepoPropName.git_repo_alias.name},
                {"content": GitRepoPropName.git_repo_content_type.name},
                {"name": GitRepoPropName.git_repo_root_base_name.name},
                {"path": GitRepoPropName.git_repo_root_rel_path.name},
                {"base": GitRepoPropName.git_repo_root_abs_path.name},
            ],
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: func_id_goto_git_repo_,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    repo_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "Goto Git repository (`cd` to its path)",
            ReservedPropName.func_state.name: FuncState.fs_beta.name,
            ReservedPropName.func_id.name: func_id_goto_git_repo_,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        assert get_func_id_from_invocation_input(invocation_input) == func_id_goto_git_repo_
        prohibit_unconsumed_args(invocation_input)
        # TODO: TODO_20_61_16_31 `cardinality_hook`: run different funcs based on `data_envelope` set size
        # TODO: TODO_86_57_50_38: make this behavior (require singled-out `data_envelope`) configure-able for all plugins:
        if len(invocation_input.envelope_containers[repo_container_ipos_].data_envelopes) != 1:
            eprint(f"ERROR: single repo is not selected (not disambiguated from multiple candidates)")
            exit(ClientExitCode.GeneralError.value)

        repo_envelope = invocation_input.envelope_containers[repo_container_ipos_].data_envelopes[0]
        repo_root_abs_path = repo_envelope[envelope_payload_][repo_root_abs_path_]
        eprint(f"INFO: starting subshell in: {repo_root_abs_path}")
        # List Git repo dir:
        sub_proc = subprocess.run(
            [
                "bash",
                "-l",
            ],
            cwd = repo_root_abs_path
        )
        exit_code = sub_proc.returncode
        if exit_code != 0:
            raise RuntimeError
