from __future__ import annotations

import os
import subprocess

from git import Repo

from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.meta_data.StaticData import StaticData
from argrelay.misc_helper import eprint
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_demo.GitRepoArgType import GitRepoArgType
from argrelay.relay_demo.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.relay_demo.GitRepoInvocator import GitRepoInvocator
from argrelay.relay_demo.GitRepoLoaderConfigSchema import base_path_, git_repo_loader_config_desc, is_enabled_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_, envelope_class_, envelope_payload_
from argrelay.schema_config_interp.FunctionEnvelopePayloadSchema import accept_envelope_classes_, invocator_plugin_id_


class GitRepoLoader(AbstractLoader):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        # validate:
        git_repo_loader_config_desc.from_input_dict(config_dict)

    def update_static_data(self, static_data: StaticData) -> StaticData:
        """
        Scan `base_path` recursively and load metadata about all Git repos found.
        """

        if not self.config_dict:
            return static_data
        if not self.config_dict[is_enabled_]:
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
            if type_name not in static_data.types_to_values.keys():
                static_data.types_to_values[type_name] = []

        data_envelopes = static_data.data_envelopes

        eprint("Git repos found:")
        for abs_git_path in git_repo_paths.keys():
            print(f"{abs_git_path}: {git_repo_paths[abs_git_path]}")

        for abs_git_path in git_repo_paths.keys():
            rel_git_path = git_repo_paths[abs_git_path]
            print(f"Git repo to load: {rel_git_path}")
            # TODO: `types_to_values` should be updated automatically after loading all envelopes:
            static_data.types_to_values[GitRepoArgType.GitRepoRelPath.name].append(rel_git_path)

            # Produce relative path, for example, if:
            # base_path_ = "/path/to/base/dir/"
            # abs_git_path = "/path/to/base/dir/rel/path/to/git/repo.git/"
            # then:
            # rel_git_path = "rel/path/to/git/repo.git/"
            # path_comp_list = [ "rel", "path", "to", "git", "repo" ]
            rel_git_path = git_repo_paths[abs_git_path]
            # TODO: `types_to_values` should be updated automatically after loading all envelopes:
            path_comp_list = static_data.types_to_values[GitRepoArgType.GitRepoPathComp.name]
            for rel_git_path_comp in rel_git_path.split(os.sep)[:-1]:
                if rel_git_path_comp not in path_comp_list:
                    path_comp_list.append(rel_git_path_comp)

            ############################################################################################################
            # repos

            repo_envelope = {
                envelope_id_: rel_git_path,
                envelope_class_: GitRepoEnvelopeClass.ClassGitRepo.name,
                envelope_payload_: {
                    "abs_repo_path": abs_git_path,
                    # TODO: Add anything extra (beyond top-level keys with meta data) required for some function
                },
                GlobalArgType.ObjectSelector.name: "repo",
                GitRepoArgType.GitRepoRelPath.name: rel_git_path,
                GitRepoArgType.GitRepoPathComp.name: path_comp_list,
                # TODO: populate list of remotes:
                GitRepoArgType.GitRepoRemoteUrl.name: [],
                # TODO: populate list of local branches:
                GitRepoArgType.GitRepoLocalBranch.name: [],
            }
            print(repo_envelope)
            data_envelopes.append(repo_envelope)

            git_repo = Repo(abs_git_path)
            for git_commit in git_repo.iter_commits():
                # TODO: `types_to_values` should be updated automatically after loading all envelopes:
                static_data.types_to_values[
                    GitRepoArgType.GitRepoCommitId.name
                ].append(git_commit.hexsha)
                static_data.types_to_values[
                    GitRepoArgType.GitRepoCommitAuthorEmail.name
                ].append(git_commit.author.email)

                ########################################################################################################
                # commits

                commit_envelope = {
                    envelope_id_: git_commit.hexsha,
                    envelope_class_: GitRepoEnvelopeClass.ClassGitCommit.name,
                    envelope_payload_: {
                        # TODO: Add anything extra (beyond top-level keys with meta data) required for some function
                    },
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

        given_function_envelope = {
            envelope_id_: "desc_repo",
            envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
            envelope_payload_: {
                invocator_plugin_id_: GitRepoInvocator.__name__,
                accept_envelope_classes_: [
                    GitRepoEnvelopeClass.ClassGitRepo.name,
                ],
            },
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "repo",
        }
        self._merge_function_envelopes(data_envelopes, given_function_envelope)

        given_function_envelope = {
            envelope_id_: "desc_commit",
            envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
            envelope_payload_: {
                invocator_plugin_id_: GitRepoInvocator.__name__,
                accept_envelope_classes_: [
                    GitRepoEnvelopeClass.ClassGitCommit.name,
                ],
            },
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "commit",
        }
        self._merge_function_envelopes(data_envelopes, given_function_envelope)

        return static_data

    # noinspection PyMethodMayBeStatic
    def _merge_function_envelopes(self, data_envelopes: list, given_func_envelope):

        is_found = False
        for data_envelope in data_envelopes:
            if (
                (envelope_id_ in data_envelope)
                and
                (data_envelope[envelope_id_] == given_func_envelope[envelope_id_])
                and
                (envelope_class_ in data_envelope)
                and
                (data_envelope[envelope_class_] == given_func_envelope[envelope_class_])
            ):
                # Update existing function envelope:
                if not is_found:
                    is_found = True

                    # Can we really support any other `envelope class`-es for this function?
                    assert len(data_envelope[envelope_payload_][accept_envelope_classes_]) == 0
                    data_envelope[envelope_payload_][accept_envelope_classes_].extend(
                        given_func_envelope[envelope_payload_][accept_envelope_classes_]
                    )

                    assert data_envelope[GlobalArgType.ActionType.name] == given_func_envelope[
                        GlobalArgType.ActionType.name]
                    data_envelope[GlobalArgType.ObjectSelector.name] = given_func_envelope[
                        GlobalArgType.ObjectSelector.name]

                else:
                    raise RuntimeError
        if not is_found:
            # Insert given function envelope:
            data_envelopes.append(given_func_envelope)
