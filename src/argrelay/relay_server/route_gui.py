from flask import Blueprint
from flask import render_template

from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig
from argrelay.server_spec.const_int import ARGRELAY_GUI_PATH


def create_blueprint_gui(gui_banner_config: GuiBannerConfig):
    blueprint_gui = Blueprint(
        name = "blueprint_gui",
        import_name = __name__,
    )

    # TODO: test and think if it is the right place
    @blueprint_gui.route(ARGRELAY_GUI_PATH)
    def basic_ui():
        return render_template(
            "argrelay_main.html",
            custom_html = gui_banner_config.custom_html,
        )

    return blueprint_gui
