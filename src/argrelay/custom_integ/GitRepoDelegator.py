from __future__ import annotations

import subprocess

from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.value_constants import goto_repo_func_, desc_commit_func_
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_func_id_from_invocation_input
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_data.ServerConfig import ServerConfig
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

repo_container_ipos_ = 1


class GitRepoDelegator(AbstractDelegator):
    """
    Implements FS_67_16_61_97 git_plugin.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        repo_search_control = populate_search_control(
            class_to_collection_map,
            GitRepoEnvelopeClass.ClassGitRepo.name,
            [
                {"alias": GitRepoArgType.GitRepoAlias.name},
                {"content": GitRepoArgType.GitRepoContentType.name},
                {"name": GitRepoArgType.GitRepoRootBaseName.name},
                {"path": GitRepoArgType.GitRepoRootRelPath.name},
                {"base": GitRepoArgType.GitRepoRootAbsPath.name},
                {"part": GitRepoArgType.GitRepoPathComp.name},
            ],
        )

        commit_search_control = populate_search_control(
            class_to_collection_map,
            GitRepoEnvelopeClass.ClassGitCommit.name,
            [
                {"name": GitRepoArgType.GitRepoRootBaseName.name},
                {"path": GitRepoArgType.GitRepoRootRelPath.name},
                {"base": GitRepoArgType.GitRepoRootAbsPath.name},
                {"email": GitRepoArgType.GitRepoCommitAuthorEmail.name},
                {"hex": GitRepoArgType.GitRepoCommitId.name},
            ],
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: goto_repo_func_,
                delegator_plugin_instance_id_: GitRepoDelegator.__name__,
                search_control_list_: [
                    repo_search_control,
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "Describe Git repository",
            ReservedArgType.FuncId.name: goto_repo_func_,
        }
        func_envelopes.append(given_function_envelope)

        given_function_envelope = {
            instance_data_: {
                func_id_: desc_commit_func_,
                delegator_plugin_instance_id_: GitRepoDelegator.__name__,
                search_control_list_: [
                    commit_search_control,
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "Describe Git commit",
            ReservedArgType.FuncId.name: desc_commit_func_,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_container = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_container.data_envelopes[0][instance_data_]
            [delegator_plugin_instance_id_]
        )
        invocation_input = InvocationInput(
            arg_values = interp_ctx.comp_suggestions,
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
            delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if get_func_id_from_invocation_input(invocation_input) == goto_repo_func_:
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
        if get_func_id_from_invocation_input(invocation_input) == desc_commit_func_:
            raise RuntimeError("not implemented")


repo_root_abs_path_: str = "repo_root_abs_path"
