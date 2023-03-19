from __future__ import annotations

import os
import subprocess

from git import Repo

from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.custom_integ.GitRepoDelegator import GitRepoDelegator
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoLoaderConfigSchema import base_path_, git_repo_loader_config_desc, is_plugin_enabled_
from argrelay.custom_integ.value_constants import desc_repo_func_, desc_commit_func_
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper import eprint
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_id_,
    envelope_payload_,
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_, envelope_class_


class GitRepoLoader(AbstractLoader):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        git_repo_loader_config_desc.validate_dict(config_dict)

    def update_static_data(self, static_data: StaticData) -> StaticData:
        """
        Scan `base_path` recursively and load metadata about all Git repos found.
        """

        if not self.config_dict:
            return static_data
        if not self.config_dict[is_plugin_enabled_]:
            return static_data

        base_path = os.path.normpath(os.path.expanduser(self.config_dict[base_path_]))
        # Map Git abs path to Git rel path:
        git_repo_paths = {}
        # Collect Git root paths under `base_path` from config:
        for root_path, ignored_dirs, ignored_files in os.walk(base_path, followlinks = True):
            root_path = os.path.normpath(root_path)

            # Skip if sub-path of known Git (do not support Git repo under Git repo):
            is_sub_dir = False
            for abs_git_path in git_repo_paths.keys():
                if root_path.startswith(abs_git_path):
                    is_sub_dir = True
                    break
            if is_sub_dir:
                continue

            eprint(f"unknown root_path: {root_path}")

            # Query Git root path of curr dir:
            subproc = subprocess.run(
                [
                    "git",
                    "-C",
                    root_path,
                    "rev-parse",
                    "--show-toplevel",
                ],
                capture_output = True,
            )
            ret_code = subproc.returncode

            if ret_code == 0:
                # Walked into Git repo sub-dirs:
                abs_git_path = os.path.normpath(subproc.stdout.decode("utf-8").strip())
                # Deduplicate Git root paths:
                if abs_git_path not in git_repo_paths.keys():
                    git_repo_paths[abs_git_path] = os.path.relpath(abs_git_path, base_path)
            else:
                # Walked into dir outside of Git repo:
                continue

        # Init type keys (if they do not exist):
        for type_name in [enum_item.name for enum_item in GitRepoArgType]:
            if type_name not in static_data.known_arg_types:
                static_data.known_arg_types.append(type_name)

        data_envelopes = static_data.data_envelopes

        eprint("Git repos found:")
        for abs_git_path in git_repo_paths.keys():
            print(f"{abs_git_path}: {git_repo_paths[abs_git_path]}")

        for abs_git_path in git_repo_paths.keys():
            rel_git_path = git_repo_paths[abs_git_path]
            print(f"Git repo to load: {rel_git_path}")

            # Produce relative path, for example, if:
            # base_path_ = "/path/to/base/dir/"
            # abs_git_path = "/path/to/base/dir/rel/path/to/git/repo.git/"
            # then:
            # rel_git_path = "rel/path/to/git/repo.git/"
            # path_comp_list = [ "rel", "path", "to", "git", "repo" ]
            rel_git_path = git_repo_paths[abs_git_path]

            path_comp_list = []
            for rel_git_path_comp in rel_git_path.split(os.sep)[:-1]:
                if rel_git_path_comp not in path_comp_list:
                    path_comp_list.append(rel_git_path_comp)

            ############################################################################################################
            # repos

            repo_envelope = {
                envelope_id_: rel_git_path,
                envelope_payload_: {
                    "abs_repo_path": abs_git_path,
                },
                ReservedArgType.EnvelopeClass.name: GitRepoEnvelopeClass.ClassGitRepo.name,
                GlobalArgType.ObjectSelector.name: "repo",
                GitRepoArgType.GitRepoRelPath.name: rel_git_path,
                GitRepoArgType.GitRepoPathComp.name: path_comp_list,
                # TODO: FS_06_99_43_60: populate list of remotes:
                GitRepoArgType.GitRepoRemoteUrl.name: [],
                # TODO: FS_06_99_43_60: populate list of local branches:
                GitRepoArgType.GitRepoLocalBranch.name: [],
            }
            print(repo_envelope)
            data_envelopes.append(repo_envelope)

            git_repo = Repo(abs_git_path)
            for git_commit in git_repo.iter_commits():
                ########################################################################################################
                # commits

                commit_envelope = {
                    envelope_id_: f"{rel_git_path}:{git_commit.hexsha}",
                    envelope_payload_: {
                    },
                    ReservedArgType.EnvelopeClass.name: GitRepoEnvelopeClass.ClassGitCommit.name,
                    GlobalArgType.ObjectSelector.name: "commit",
                    GitRepoArgType.GitRepoRelPath.name: rel_git_path,
                    GitRepoArgType.GitRepoCommitId.name: git_commit.hexsha,
                    GitRepoArgType.GitRepoCommitAuthorName.name: git_commit.author.name,
                    GitRepoArgType.GitRepoCommitAuthorEmail.name: git_commit.author.email,
                    GitRepoArgType.GitRepoCommitMessage.name: git_commit.message,
                }
                print(commit_envelope)
                data_envelopes.append(commit_envelope)

        ###############################################################################################################
        # functions

        repo_search_control = {
            envelope_class_: GitRepoEnvelopeClass.ClassGitRepo.name,
            keys_to_types_list_: [
                {"part": GitRepoArgType.GitRepoPathComp.name},
                {"path": GitRepoArgType.GitRepoRelPath.name},
            ],
        }

        commit_search_control = {
            envelope_class_: GitRepoEnvelopeClass.ClassGitCommit.name,
            keys_to_types_list_: [
                {"path": GitRepoArgType.GitRepoRelPath.name},
                {"email": GitRepoArgType.GitRepoCommitAuthorEmail.name},
                {"hex": GitRepoArgType.GitRepoCommitId.name},
            ],
        }

        given_function_envelope = {
            envelope_id_: desc_repo_func_,
            instance_data_: {
                delegator_plugin_instance_id_: GitRepoDelegator.__name__,
                search_control_list_: [
                    repo_search_control,
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "Describe Git repository",
            GlobalArgType.FunctionCategory.name: "external",
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "repo",
        }
        data_envelopes.append(given_function_envelope)

        given_function_envelope = {
            envelope_id_: desc_commit_func_,
            instance_data_: {
                delegator_plugin_instance_id_: GitRepoDelegator.__name__,
                search_control_list_: [
                    commit_search_control,
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "Describe Git commit",
            GlobalArgType.FunctionCategory.name: "external",
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "commit",
        }
        data_envelopes.append(given_function_envelope)

        return static_data
