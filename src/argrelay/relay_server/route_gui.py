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
    default_gui_command: str,
    server_start_time: int,
    project_git_commit_time: int,
    project_git_commit_url: str,
    project_git_commit_display_string: str,
    project_git_conf_dir_url: str,
    project_git_conf_dir_display_string: str,
):
    if default_gui_command is None or len(default_gui_command.strip()) == 0:
        default_gui_command = "lay goto"
    else:
        default_gui_command = default_gui_command.strip()

    blueprint_gui = Blueprint(
        name = "blueprint_gui",
        import_name = __name__,
    )

    @blueprint_gui.route(f"{ARGRELAY_GUI_PATH}")
    @blueprint_gui.route(f"{ARGRELAY_GUI_PATH}<path:command_line>")
    def basic_ui(
        command_line: str = "",
    ):
        if len(command_line) == 0:
            command_line = default_gui_command
        if len(command_line) > 0 and not command_line.endswith(" "):
            command_line += " "
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
            meter_html = gui_banner_config.meter_html,
            tagline_html = gui_banner_config.tagline_html,
            header_html = gui_banner_config.header_html,
            footer_html = gui_banner_config.footer_html,
            command_line = command_line,
        )

    return blueprint_gui


def unix_time_to_iso_utc(
    unix_time: int,
) -> str:
    return f"{datetime.utcfromtimestamp(unix_time).isoformat()}Z"
