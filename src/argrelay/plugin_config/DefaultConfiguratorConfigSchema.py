from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_config.DefaultConfiguratorConfig import DefaultConfiguratorConfig

"""
Schema for :class:`DefaultConfiguratorConfig`
"""

project_title_ = "project_title"

project_page_url_ = "project_page_url"

git_files_by_commit_id_url_prefix_ = "git_files_by_commit_id_url_prefix"

commit_id_url_prefix_ = "commit_id_url_prefix"


class DefaultConfiguratorConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    project_title = fields.String(
        required = False,
    )

    project_page_url = fields.String(
        required = False,
    )

    git_files_by_commit_id_url_prefix = fields.String(
        required = False,
    )

    commit_id_url_prefix = fields.String(
        required = False,
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return DefaultConfiguratorConfig(
            project_title = input_dict.get(project_title_, None),
            project_page_url = input_dict.get(project_page_url_, None),
            git_files_by_commit_id_url_prefix = input_dict.get(git_files_by_commit_id_url_prefix_, None),
            commit_id_url_prefix = input_dict.get(commit_id_url_prefix_, None),
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
