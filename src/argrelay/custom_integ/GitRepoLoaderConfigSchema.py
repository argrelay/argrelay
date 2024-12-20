from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.custom_integ.GitRepoEntryConfigSchema import git_repo_entry_config_desc
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.misc_helper_common.TypeDesc import TypeDesc

class_name_repo_ = "class_name_repo"
class_name_tag_ = "class_name_tag"
class_name_commit_ = "class_name_commit"

load_git_repos_default_ = "load_git_repos_default"
load_git_tags_default_ = "load_git_tags_default"
load_git_commits_default_ = "load_git_commits_default"

repo_entries_ = "repo_entries"


class GitRepoLoaderConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    class_name_repo = fields.String(
        required = False,
        load_default = GitRepoEnvelopeClass.class_git_repo.name,
    )

    class_name_tag = fields.String(
        required = False,
        load_default = GitRepoEnvelopeClass.class_git_tag.name,
    )

    class_name_commit = fields.String(
        required = False,
        load_default = GitRepoEnvelopeClass.class_git_commit.name,
    )

    load_git_repos_default = fields.Boolean(
        required = False,
        load_default = True,
    )

    load_git_tags_default = fields.Boolean(
        required = False,
        load_default = False,
    )

    load_git_commits_default = fields.Boolean(
        required = False,
        load_default = False,
    )

    # Maps `repo_base_path` to list of repo entries.
    # *   If `repo_base_path` starts with `/` (absolute), it is used verbatim.
    # *   If `repo_base_path` does not start with `/` (relative),
    #     it is converted to absolute assuming it is relative to `argrelay_dir` (`@/`).
    repo_entries = fields.Dict(
        keys = fields.String(),
        values = fields.List(
            fields.Nested(git_repo_entry_config_desc.dict_schema),
            required = True,
        ),
        required = True,
    )


git_repo_loader_config_desc = TypeDesc(
    dict_schema = GitRepoLoaderConfigSchema(),
    ref_name = GitRepoLoaderConfigSchema.__name__,
    dict_example = {
        class_name_repo_: GitRepoEnvelopeClass.class_git_repo.name,
        class_name_tag_: GitRepoEnvelopeClass.class_git_tag.name,
        class_name_commit_: GitRepoEnvelopeClass.class_git_commit.name,
        load_git_repos_default_: True,
        load_git_tags_default_: False,
        load_git_commits_default_: False,
        repo_entries_: {
            "~/repos": [
                git_repo_entry_config_desc.dict_example,
            ]
        },
    },
    default_file_path = "",
)
