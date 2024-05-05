from marshmallow import RAISE, fields

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_config.DefaultConfiguratorConfig import DefaultConfiguratorConfig

"""
Schema for :class:`DefaultConfiguratorConfig`
"""

project_title_ = "project_title"

project_page_url_ = "project_page_url"

git_files_by_commit_id_url_prefix_ = "git_files_by_commit_id_url_prefix"

commit_id_url_prefix_ = "commit_id_url_prefix"


class DefaultConfiguratorConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        ordered = True

    model_class = DefaultConfiguratorConfig

    project_title = fields.String(
        required = False,
        load_default = None,
    )

    project_page_url = fields.String(
        required = False,
        load_default = None,
    )

    git_files_by_commit_id_url_prefix = fields.String(
        required = False,
        load_default = None,
    )

    commit_id_url_prefix = fields.String(
        required = False,
        load_default = None,
    )


default_configurator_config_desc = TypeDesc(
    dict_schema = DefaultConfiguratorConfigSchema(),
    ref_name = DefaultConfiguratorConfigSchema.__name__,
    dict_example = {
        project_title_: "relay_demo",
        project_page_url_: "https://argrelay.org",
        git_files_by_commit_id_url_prefix_: "https://github.com/argrelay/argrelay/tree/",
        commit_id_url_prefix_: "https://github.com/argrelay/argrelay/commit/",
    },
    default_file_path = "",
)
