from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.misc_helper_common.TypeDesc import TypeDesc

repo_base_path_ = "repo_base_path"
repo_rel_path_ = "repo_rel_path"
is_repo_enabled_ = "is_repo_enabled"
envelope_properties_ = "envelope_properties"


class GitRepoEntryConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    repo_base_path = fields.String()

    repo_rel_path = fields.String()

    is_repo_enabled = fields.Boolean(
        load_default = True,
        required = False,
    )

    # These key-values are copied into `data_envelope`:
    envelope_properties = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = True,
    )


git_repo_entry_config_desc = TypeDesc(
    dict_schema = GitRepoEntryConfigSchema(),
    ref_name = GitRepoEntryConfigSchema.__name__,
    dict_example = {
        repo_rel_path_: "argrelay.git",
        is_repo_enabled_: True,
        envelope_properties_: {
            GitRepoArgType.GitRepoAlias.name: "ar",
        }
    },
    default_file_path = "",
)
