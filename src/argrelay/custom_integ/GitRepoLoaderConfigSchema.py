from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.custom_integ.GitRepoEntryConfigSchema import git_repo_entry_config_desc
from argrelay.misc_helper_common.TypeDesc import TypeDesc

load_repo_commits_ = "load_repo_commits"
repo_entries_ = "repo_entries"


class GitRepoLoaderConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    load_repo_commits = fields.Boolean()

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
        load_repo_commits_: False,
        repo_entries_: {
            "~/repos": [
                git_repo_entry_config_desc.dict_example,
            ]
        },
    },
    default_file_path = "",
)
