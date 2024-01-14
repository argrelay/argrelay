from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_config.DefaultConfiguratorConfig import DefaultConfiguratorConfig

"""
Schema for :class:`DefaultConfiguratorConfig`
"""

commit_id_url_prefix_ = "commit_id_url_prefix"


class DefaultConfiguratorConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

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
            commit_id_url_prefix = input_dict.get(commit_id_url_prefix_, None),
        )


default_configurator_config_desc = TypeDesc(
    dict_schema = DefaultConfiguratorConfigSchema(),
    ref_name = DefaultConfiguratorConfigSchema.__name__,
    dict_example = {
        commit_id_url_prefix_: "https://github.com/argrelay/argrelay/commit/",
    },
    default_file_path = "",
)
