from __future__ import annotations

from marshmallow import (
    fields,
    RAISE,
    Schema,
)

from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_lib_server_plugin_demo.demo_git.GitRepoPropName import GitRepoPropName

repo_rel_path_ = "repo_rel_path"
is_repo_enabled_ = "is_repo_enabled"

load_repo_entries_ = "load_repo_entries"
load_repo_tags_ = "load_repo_tags"
load_repo_commits_ = "load_repo_commits"

load_tags_last_days_ = "load_tags_last_days"
load_commits_max_count_ = "load_commits_max_count"
envelope_properties_ = "envelope_properties"


class GitRepoEntryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    repo_rel_path = fields.String(
        required=True,
    )

    load_repo_entries = fields.Boolean(
        required=False,
        load_default=None,
        allow_none=True,
    )

    load_repo_tags = fields.Boolean(
        required=False,
        load_default=None,
        allow_none=True,
    )

    load_repo_commits = fields.Boolean(
        required=False,
        load_default=None,
        allow_none=True,
    )

    load_tags_last_days = fields.Integer(
        required=False,
        load_default=300,
    )

    load_commits_max_count = fields.Integer(
        required=False,
        load_default=100,
    )

    is_repo_enabled = fields.Boolean(
        required=False,
        load_default=True,
    )

    # These `prop_name` and `prop_values` are copied into `data_envelope`:
    envelope_properties = fields.Dict(
        keys=fields.String(),
        values=fields.String(),
        required=True,
    )


git_repo_entry_config_desc = TypeDesc(
    dict_schema=GitRepoEntryConfigSchema(),
    ref_name=GitRepoEntryConfigSchema.__name__,
    dict_example={
        repo_rel_path_: "argrelay.git",
        is_repo_enabled_: True,
        load_repo_tags_: False,
        load_repo_commits_: False,
        load_tags_last_days_: 1,
        load_commits_max_count_: 10,
        envelope_properties_: {
            GitRepoPropName.git_repo_alias.name: "ar",
        },
    },
    default_file_path="",
)
