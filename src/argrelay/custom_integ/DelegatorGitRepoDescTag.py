from __future__ import annotations

from argrelay.custom_integ.DelegatorGitRepoBase import DelegatorGitRepoBase
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoPropName import GitRepoPropName
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_invocation_input
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput

func_id_desc_git_tag_ = "func_id_desc_git_tag"

repo_container_ipos_ = 1


class DelegatorGitRepoDescTag(DelegatorGitRepoBase):
    """
    Implements `func_id_desc_git_tag_` for FS_67_16_61_97 git_plugin.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        tag_search_control = populate_search_control(
            GitRepoEnvelopeClass.class_git_tag.name,
            {
                ReservedPropName.envelope_class.name: GitRepoEnvelopeClass.class_git_tag.name,
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

                {"date": GitRepoPropName.git_repo_commit_date.name},
                {"tag": GitRepoPropName.git_repo_tag_name.name},
                {"time": GitRepoPropName.git_repo_commit_time.name},
                {"hex": GitRepoPropName.git_repo_short_commit_id.name},
            ],
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: func_id_desc_git_tag_,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    tag_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "Describe Git tag",
            ReservedPropName.func_state.name: FuncState.fs_demo.name,
            ReservedPropName.func_id.name: func_id_desc_git_tag_,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        assert get_func_id_from_invocation_input(invocation_input) == func_id_desc_git_tag_
        raise RuntimeError("ERROR: not implemented for demo")
