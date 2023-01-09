from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

is_enabled_ = "is_enabled"
base_path_ = "base_path"


class GitRepoLoaderConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    is_enabled = fields.Boolean()
    base_path = fields.String()


git_repo_loader_config_desc = TypeDesc(
    dict_schema = GitRepoLoaderConfigSchema(),
    ref_name = GitRepoLoaderConfigSchema.__name__,
    dict_example = {
        is_enabled_: False,
        base_path_: "~",
    },
    default_file_path = "",
)
