from marshmallow import Schema, fields, RAISE, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig

header_html_ = "header_html"
footer_html_ = "footer_html"

class GuiBannerConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    header_html = fields.String()
    footer_html = fields.String()

    @post_load
    def make_object(self, input_dict, **kwargs):
        return GuiBannerConfig(
            header_html = input_dict[header_html_],
            footer_html = input_dict[footer_html_],
        )

gui_banner_config_desc = TypeDesc(
    dict_schema = GuiBannerConfigSchema(),
    ref_name = GuiBannerConfigSchema.__name__,
    dict_example = {
        header_html_: "",
        footer_html_: "",
    },
    default_file_path = "",
)
