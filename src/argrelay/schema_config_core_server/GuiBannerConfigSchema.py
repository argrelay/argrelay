from marshmallow import fields, RAISE

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig

header_html_ = "header_html"
footer_html_ = "footer_html"


class GuiBannerConfigSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = GuiBannerConfig

    header_html = fields.String()
    footer_html = fields.String()


gui_banner_config_desc = TypeDesc(
    dict_schema = GuiBannerConfigSchema(),
    ref_name = GuiBannerConfigSchema.__name__,
    dict_example = {
        header_html_: "",
        footer_html_: "",
    },
    default_file_path = "",
)
