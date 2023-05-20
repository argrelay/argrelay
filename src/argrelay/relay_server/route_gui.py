from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig
from argrelay.server_spec.const_int import (
    ARGRELAY_GUI_PATH,
    API_SPEC_PATH,
    API_DOCS_PATH,
)
from flask import Blueprint
from flask import render_template


def create_blueprint_gui(
    argrelay_version: str,
    gui_banner_config: GuiBannerConfig,
):
    blueprint_gui = Blueprint(
        name = "blueprint_gui",
        import_name = __name__,
    )

    # TODO: test and think if it is the right place
    @blueprint_gui.route(ARGRELAY_GUI_PATH)
    def basic_ui():
        return render_template(
            "argrelay_main.html",
            argrelay_version = argrelay_version,
            argrelay_api_docs_path = API_DOCS_PATH,
            argrelay_api_spec_path = API_SPEC_PATH,
            header_html = gui_banner_config.header_html,
            footer_html = gui_banner_config.footer_html,
        )

    return blueprint_gui
