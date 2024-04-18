from __future__ import annotations

import copy
import os
from datetime import timezone, datetime, timedelta

from git import Repo

from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.custom_integ.GitRepoDelegator import repo_root_abs_path_
from argrelay.custom_integ.GitRepoEntryConfigSchema import (
    repo_rel_path_,
    envelope_properties_,
    is_repo_enabled_,
    load_repo_commits_,
    load_repo_tags_,
    load_commits_max_count_,
    load_tags_last_days_,
)
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoLoaderConfigSchema import (
    git_repo_loader_config_desc,
    load_git_commits_default_,
    repo_entries_,
    load_git_tags_default_,
)
from argrelay.custom_integ.git_utils import is_git_repo
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper_common import eprint, get_argrelay_dir
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_id_,
    envelope_payload_,
)


class GitRepoLoader(AbstractLoader):
    """
    Implements FS_67_16_61_97 git_plugin.
    """

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return git_repo_loader_config_desc.dict_from_input_dict(plugin_config_dict)

    def update_static_data(
        self,
        static_data: StaticData,
    ) -> StaticData:

        if not self.plugin_config_dict:
            return static_data

        static_data = self.load_git_objects(static_data)

        return static_data

    def load_git_objects(
        self,
        static_data: StaticData,
    ) -> StaticData:
        """
        Scan `base_path` recursively and load metadata about all Git repos found.
        """

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        class_names = [
            GitRepoEnvelopeClass.ClassGitRepo.name,
            GitRepoEnvelopeClass.ClassGitTag.name,
            GitRepoEnvelopeClass.ClassGitCommit.name,
        ]

        init_envelop_collections(
            self.server_config,
            class_names,
            # Same index fields for all collections (can be fine-tuned later):
            lambda collection_name, class_name: [enum_item.name for enum_item in GitRepoArgType]
        )

        repo_envelopes = static_data.envelope_collections[
            class_to_collection_map[GitRepoEnvelopeClass.ClassGitRepo.name]
        ].data_envelopes
        tag_envelopes = static_data.envelope_collections[
            class_to_collection_map[GitRepoEnvelopeClass.ClassGitTag.name]
        ].data_envelopes
        commit_envelopes = static_data.envelope_collections[
            class_to_collection_map[GitRepoEnvelopeClass.ClassGitCommit.name]
        ].data_envelopes

        load_git_commits_default = self.plugin_config_dict[load_git_commits_default_]
        load_git_tags_default = self.plugin_config_dict[load_git_tags_default_]

        # List of registered Git abs paths:
        repo_root_abs_paths = []
        for repo_base_path in self.plugin_config_dict[repo_entries_]:

            repo_entries = self.plugin_config_dict[repo_entries_][repo_base_path]
            repo_base_path = os.path.expanduser(repo_base_path)
            if os.path.isabs(repo_base_path):
                repo_base_abs_path = repo_base_path
            else:
                repo_base_abs_path = os.path.join(get_argrelay_dir(), repo_base_path)

            # Process repo entries collecting `repo_root_rel_path` and `repo_root_abs_path`:
            for repo_entry in repo_entries:

                repo_root_rel_path: str = repo_entry[repo_rel_path_]
                repo_root_abs_path: str = os.path.join(repo_base_abs_path, repo_root_rel_path)

                if not repo_entry[is_repo_enabled_]:
                    eprint(f"INFO: disabled repo: {repo_root_abs_path}")
                    continue

                # Deduplicate Git root paths:
                if repo_root_abs_path not in repo_root_abs_paths:
                    # Register `repo_root_abs_path`:
                    repo_root_abs_paths.append(repo_root_abs_path)
                else:
                    eprint(f"ERROR: duplicate Git repo: {repo_root_abs_path}")
                    raise RuntimeError

                # Query Git root path of curr dir:
                if is_git_repo(
                    repo_root_abs_path,
                ):
                    pass
                else:
                    eprint(f"ERROR: not a Git repo: {repo_root_abs_path}")
                    # Walked into dir outside of Git repo:
                    continue

                repo_root_base_name = os.path.basename(repo_root_abs_path)

                ############################################################################################################
                # repos

                repo_envelope: dict = copy.deepcopy(repo_entry[envelope_properties_])

                repo_envelope.update({
                    envelope_id_: f"{repo_root_abs_path}:{GitRepoEnvelopeClass.ClassGitRepo.name}",
                    envelope_payload_: {
                        repo_root_abs_path_: repo_root_abs_path,
                    },
                    ReservedArgType.EnvelopeClass.name: GitRepoEnvelopeClass.ClassGitRepo.name,
                    GitRepoArgType.git_repo_root_rel_path.name: repo_root_rel_path,
                    GitRepoArgType.git_repo_root_abs_path.name: repo_root_abs_path,
                    GitRepoArgType.git_repo_root_base_name.name: repo_root_base_name,
                })
                self.enrich_git_repo_object(repo_envelope)
                repo_envelopes.append(repo_envelope)

                load_repo_tags = repo_entry[load_repo_tags_]
                if load_git_tags_default or load_repo_tags:

                    ########################################################################################################
                    # tags

                    load_tags_last_days = repo_entry[load_tags_last_days_]

                    earliest_ts_utc = (datetime.now() - timedelta(days = load_tags_last_days)).astimezone(timezone.utc)

                    git_repo = Repo(repo_root_abs_path)

                    for git_tag in git_repo.tags:

                        git_commit = git_tag.commit

                        (
                            commit_timestamp_utc,
                            commit_date_utc,
                            commit_time_utc,
                        ) = self.get_commit_date_and_time(git_commit)

                        if commit_timestamp_utc < earliest_ts_utc:
                            continue

                        tag_envelope: dict = copy.deepcopy(repo_entry[envelope_properties_])

                        tag_envelope.update({
                            envelope_id_: f"{repo_root_abs_path}:{GitRepoEnvelopeClass.ClassGitTag.name}:{git_tag.name}",
                            envelope_payload_: {
                            },
                            ReservedArgType.EnvelopeClass.name: GitRepoEnvelopeClass.ClassGitTag.name,
                            GitRepoArgType.git_repo_root_rel_path.name: repo_root_rel_path,
                            GitRepoArgType.git_repo_root_abs_path.name: repo_root_abs_path,
                            GitRepoArgType.git_repo_root_base_name.name: repo_root_base_name,
                            #
                            GitRepoArgType.git_repo_tag_name.name: git_tag.name,
                            #
                            GitRepoArgType.git_repo_commit_id.name: git_commit.hexsha,
                            GitRepoArgType.git_repo_short_commit_id.name: git_commit.hexsha[:7],
                            GitRepoArgType.git_repo_commit_author_name.name: git_commit.author.name,
                            GitRepoArgType.git_repo_commit_author_email.name: git_commit.author.email,
                            GitRepoArgType.git_repo_commit_message.name: git_commit.message,
                            GitRepoArgType.git_repo_commit_date.name: commit_date_utc,
                            GitRepoArgType.git_repo_commit_time.name: commit_time_utc,
                        })
                        self.enrich_git_repo_object(tag_envelope)
                        tag_envelopes.append(tag_envelope)

                load_repo_commits = repo_entry[load_repo_commits_]
                if load_git_commits_default or load_repo_commits:

                    ########################################################################################################
                    # commits

                    load_commits_max_count = repo_entry[load_commits_max_count_]

                    git_repo = Repo(repo_root_abs_path)
                    for git_commit in git_repo.iter_commits(max_count = load_commits_max_count):
                        (
                            commit_timestamp_utc,
                            commit_date_utc,
                            commit_time_utc,
                        ) = self.get_commit_date_and_time(git_commit)

                        commit_envelope: dict = copy.deepcopy(repo_entry[envelope_properties_])

                        commit_envelope.update({
                            envelope_id_: f"{repo_root_abs_path}:{GitRepoEnvelopeClass.ClassGitCommit.name}:{git_commit.hexsha}",
                            envelope_payload_: {
                            },
                            ReservedArgType.EnvelopeClass.name: GitRepoEnvelopeClass.ClassGitCommit.name,
                            GitRepoArgType.git_repo_root_rel_path.name: repo_root_rel_path,
                            GitRepoArgType.git_repo_root_abs_path.name: repo_root_abs_path,
                            GitRepoArgType.git_repo_root_base_name.name: repo_root_base_name,
                            #
                            GitRepoArgType.git_repo_commit_id.name: git_commit.hexsha,
                            GitRepoArgType.git_repo_short_commit_id.name: git_commit.hexsha[:7],
                            GitRepoArgType.git_repo_commit_author_name.name: git_commit.author.name,
                            GitRepoArgType.git_repo_commit_author_email.name: git_commit.author.email.lower(),
                            GitRepoArgType.git_repo_commit_message.name: git_commit.message,
                            GitRepoArgType.git_repo_commit_date.name: commit_date_utc,
                            GitRepoArgType.git_repo_commit_time.name: commit_time_utc,
                        })
                        self.enrich_git_repo_object(commit_envelope)
                        commit_envelopes.append(commit_envelope)

        return static_data

    # noinspection PyMethodMayBeStatic
    def get_commit_date_and_time(
        self,
        git_commit,
    ):
        commit_timestamp_utc = git_commit.committed_datetime.astimezone(timezone.utc)
        commit_date_utc = f"{commit_timestamp_utc.date().isoformat()}Z"
        commit_time_utc = f"{commit_timestamp_utc.time().isoformat()}Z"
        return (
            commit_timestamp_utc,
            commit_date_utc,
            commit_time_utc,
        )

    def enrich_git_repo_object(
        self,
        data_envelope: dict,
    ) -> None:
        object_categories: list[str] = self.categorize_git_object(data_envelope)

        if not object_categories:
            object_categories.append("UKNOWN_category")

        data_envelope.update({
            GitRepoArgType.git_repo_object_category.name: object_categories,
        })

    def categorize_git_object(
        self,
        data_envelope: dict,
    ) -> list[str]:
        object_class = data_envelope[ReservedArgType.EnvelopeClass.name]
        if object_class == GitRepoEnvelopeClass.ClassGitTag.name:
            return self.categorize_git_tag(data_envelope)
        return []

    def categorize_git_tag(
        self,
        data_envelope: dict,
    ) -> list[str]:
        tag_categories = []
        tag_name = data_envelope[GitRepoArgType.git_repo_tag_name.name]

        if ".dev" in tag_name:
            tag_categories.append("pre-release")
        if tag_name.endswith(".final"):
            tag_categories.append("release")

        if tag_name.startswith("v0."):
            tag_categories.append("unstable")
        else:
            tag_categories.append("stable")

        return tag_categories
