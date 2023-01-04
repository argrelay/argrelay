from __future__ import annotations

import os
import subprocess

from git import Repo

from argrelay.data_schema.DataObjectSchema import object_id_, object_class_, object_data_
from argrelay.data_schema.FunctionObjectDataSchema import accept_object_classes_
from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.meta_data.StaticData import StaticData
from argrelay.misc_helper import eprint
from argrelay.relay_demo.GitRepoArgType import GitRepoArgType
from argrelay.relay_demo.GitRepoLoaderConfigSchema import base_path_, git_repo_loader_config_desc, is_enabled_
from argrelay.relay_demo.GitRepoObjectClass import GitRepoObjectClass


class GitRepoLoader(AbstractLoader):
    config_object: dict

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        self.config_object = git_repo_loader_config_desc.from_input_dict(config_dict)

    def update_static_data(self, static_data: StaticData) -> StaticData:
        """
        Scan `base_path` recursively and load metadata about all Git repos found.
        """

        if not self.config_object:
            return static_data
        if not self.config_object[is_enabled_]:
            return static_data

        base_path = os.path.normpath(os.path.expanduser(self.config_object[base_path_]))
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

        data_objects = static_data.data_objects

        eprint("Git repos found:")
        for abs_git_path in git_repo_paths.keys():
            print(f"{abs_git_path}: {git_repo_paths[abs_git_path]}")

        for abs_git_path in git_repo_paths.keys():
            rel_git_path = git_repo_paths[abs_git_path]
            print(f"Git repo to load: {rel_git_path}")
            # TODO: `types_to_values` should be updated automatically after loading all objects:
            static_data.types_to_values[GitRepoArgType.GitRepoRelPath.name].append(rel_git_path)

            # Produce relative path, for example, if:
            # base_path_ = "/path/to/base/dir/"
            # abs_git_path = "/path/to/base/dir/rel/path/to/git/repo.git/"
            # then:
            # rel_git_path = "rel/path/to/git/repo.git/"
            # path_comp_list = [ "rel", "path", "to", "git", "repo" ]
            rel_git_path = git_repo_paths[abs_git_path]
            # TODO: `types_to_values` should be updated automatically after loading all objects:
            path_comp_list = static_data.types_to_values[GitRepoArgType.GitRepoPathComp.name]
            for rel_git_path_comp in rel_git_path.split(os.sep)[:-1]:
                if rel_git_path_comp not in path_comp_list:
                    path_comp_list.append(rel_git_path_comp)

            ############################################################################################################
            # repos

            repo_object = {
                object_id_: rel_git_path,
                object_class_: GitRepoObjectClass.ClassGitRepo.name,
                object_data_: {
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
            print(repo_object)
            data_objects.append(repo_object)

            git_repo = Repo(abs_git_path)
            for git_commit in git_repo.iter_commits():
                # TODO: `types_to_values` should be updated automatically after loading all objects:
                static_data.types_to_values[
                    GitRepoArgType.GitRepoCommitId.name
                ].append(git_commit.hexsha)
                static_data.types_to_values[
                    GitRepoArgType.GitRepoCommitAuthorEmail.name
                ].append(git_commit.author.email)

                ########################################################################################################
                # commits

                commit_object = {
                    object_id_: git_commit.hexsha,
                    object_class_: GitRepoObjectClass.ClassGitCommit.name,
                    object_data_: {
                        # TODO: Add anything extra (beyond top-level keys with meta data) required for some function
                    },
                    GlobalArgType.ObjectSelector.name: "commit",
                    GitRepoArgType.GitRepoRelPath.name: rel_git_path,
                    GitRepoArgType.GitRepoCommitId.name: git_commit.hexsha,
                    GitRepoArgType.GitRepoCommitAuthorName.name: git_commit.author.name,
                    GitRepoArgType.GitRepoCommitAuthorEmail.name: git_commit.author.email,
                    GitRepoArgType.GitRepoCommitMessage.name: git_commit.message,
                }
                print(commit_object)
                data_objects.append(commit_object)

        ###############################################################################################################
        # functions

        given_func_object = {
            object_id_: "desc_repo",
            object_class_: ReservedObjectClass.ClassFunction.name,
            object_data_: {
                accept_object_classes_: [
                    GitRepoObjectClass.ClassGitRepo.name,
                ],
            },
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "repo",
        }
        self._merge_function_object(data_objects, given_func_object)

        given_func_object = {
            object_id_: "desc_commit",
            object_class_: ReservedObjectClass.ClassFunction.name,
            object_data_: {
                accept_object_classes_: [
                    GitRepoObjectClass.ClassGitCommit.name,
                ],
            },
            GlobalArgType.ActionType.name: "desc",
            GlobalArgType.ObjectSelector.name: "commit",
        }
        self._merge_function_object(data_objects, given_func_object)

        return static_data

    # noinspection PyMethodMayBeStatic
    def _merge_function_object(self, data_objects: list, given_func_object):

        is_found = False
        for data_object in data_objects:
            if (
                (object_id_ in data_object) and (data_object[object_id_] == given_func_object[object_id_])
                and
                (object_class_ in data_object) and (data_object[object_class_] == given_func_object[object_class_])
            ):
                # Update existing function object:
                if not is_found:
                    is_found = True

                    # Can we really support any other object types for this function?
                    assert len(data_object[object_data_][accept_object_classes_]) == 0
                    data_object[object_data_][accept_object_classes_].extend(
                        given_func_object[object_data_][accept_object_classes_]
                    )

                    assert data_object[GlobalArgType.ActionType.name] == given_func_object[
                        GlobalArgType.ActionType.name]
                    data_object[GlobalArgType.ObjectSelector.name] = given_func_object[
                        GlobalArgType.ObjectSelector.name]

                else:
                    raise RuntimeError
        if not is_found:
            # Insert given function object:
            data_objects.append(given_func_object)
