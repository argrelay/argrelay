from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig

custom_html_ = "custom_html"


class GuiBannerConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    custom_html = fields.String()

    @post_load
    def make_object(self, input_dict, **kwargs):
        return GuiBannerConfig(
            custom_html = input_dict[custom_html_],
        )

gui_banner_config_desc = TypeDesc(
    dict_schema = GuiBannerConfigSchema(),
    ref_name = GuiBannerConfigSchema.__name__,
    dict_example = {
        custom_html_: "",
    },
    default_file_path = "",
)
