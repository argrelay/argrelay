from datetime import datetime

from flask import Blueprint
from flask import render_template

from argrelay.relay_server.GuiBannerConfig import GuiBannerConfig
from argrelay.server_spec.const_int import (
    ARGRELAY_GUI_PATH,
    API_SPEC_PATH,
    API_DOCS_PATH,
)


def create_blueprint_gui(
    project_title: str,
    project_page_url: str,
    argrelay_version: str,
    gui_banner_config: GuiBannerConfig,
    server_start_time: int,
    project_git_commit_time: int,
    project_git_commit_url: str,
    project_git_commit_display_string: str,
    project_git_conf_dir_url: str,
    project_git_conf_dir_display_string: str,
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
            project_title = project_title,
            project_page_url = project_page_url,
            argrelay_version = argrelay_version,
            argrelay_api_docs_path = API_DOCS_PATH,
            argrelay_api_spec_path = API_SPEC_PATH,
            server_start_time = unix_time_to_iso_utc(server_start_time),
            project_git_commit_time = unix_time_to_iso_utc(project_git_commit_time),
            project_git_commit_url = project_git_commit_url,
            project_git_commit_display_string = project_git_commit_display_string,
            project_git_conf_dir_url = project_git_conf_dir_url,
            project_git_conf_dir_display_string = project_git_conf_dir_display_string,
            header_html = gui_banner_config.header_html,
            footer_html = gui_banner_config.footer_html,
        )

    return blueprint_gui


def unix_time_to_iso_utc(
    unix_time: int,
) -> str:
    return f"{datetime.utcfromtimestamp(unix_time).isoformat()}Z"
