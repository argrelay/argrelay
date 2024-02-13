import logging
import os.path
from typing import Union, Callable, Any

import pkg_resources
from flasgger import Swagger
from flask import Flask, request, redirect

from argrelay import relay_server
from argrelay.custom_integ.git_utils import get_git_repo_root_path
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.plugin_config.AbstractConfigurator import AbstractConfigurator
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.route_api import create_blueprint_api
from argrelay.relay_server.route_gui import create_blueprint_gui
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.const_int import API_SPEC_PATH, API_DOCS_PATH, ARGRELAY_GUI_PATH

# Set this here (because `require` function may fail in other contexts):
server_version = pkg_resources.require("argrelay")[0].version
server_title = relay_server.__name__


class CustomFlaskApp(Flask):
    """
    This is an API-wrapper exposing `LocalServer` over the network.
    """

    def __init__(
        self,
        import_name: str,
        static_url_path = "/gui_static",
        static_folder = pkg_resources.resource_filename(relay_server.__name__, "gui_static"),
        template_folder = pkg_resources.resource_filename(relay_server.__name__, "gui_templates"),
    ):
        super().__init__(
            import_name = import_name,
            static_folder = static_folder,
            template_folder = template_folder,
            static_url_path = static_url_path,
        )
        self.local_server: LocalServer = LocalServer(server_config_desc.obj_from_default_file())

    def run_with_config(self):
        # Use custom logging at DEBUG level - see: `log_request` and `log_response:
        self.logger.setLevel(logging.DEBUG)
        # Log only at ERROR level by default logger:
        # https://stackoverflow.com/a/18379764/441652
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        self.run(
            # Contrary to "debug" keyword, if IDE debug is needed, set `debug` to `False` to avoid reloader:
            # https://stackoverflow.com/a/53790400/441652
            # NOTE: Disabled debug to make sure reloader does not restart server (which does not work with Mongo DB):
            debug = False,
            host = self.local_server.server_config.connection_config.server_host_name,
            port = self.local_server.server_config.connection_config.server_port_number,
        )


def create_app() -> CustomFlaskApp:
    """
    The function prevents running the code inside it on import - necessary for pre-test mocking.
    Note that Flask may rely on specific name `create_app` to find this factory:
    https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/#using-applications
    """

    flask_app = CustomFlaskApp(
        import_name = relay_server.__name__,
    )

    flask_app.local_server.start_local_server()

    swagger_template = {
        "info": {
            "title": server_title,
            "version": server_version,
            "description": f"See <a href=\"{ARGRELAY_GUI_PATH}\" target=\"_blank\">built-in GUI</a>.",
        },
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "relay_server",
                "route": API_SPEC_PATH,
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            },
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": API_DOCS_PATH,
    }

    Swagger(
        flask_app,
        template = swagger_template,
        config = swagger_config,
    )

    @flask_app.before_request
    def log_request():
        flask_app.logger.debug(
            "request: %s\n    source: %s\n    headers: %s\n    body: %s",
            request,
            request.remote_addr,
            request.headers.__repr__(),
            request.get_data(),
        )

    @flask_app.after_request
    def log_response(response):
        # Wrap into try/except because of this:
        # https://stackoverflow.com/q/64006669/441652
        # noinspection PyBroadException
        try:
            response_data = str(response.get_data())
        except Exception as e:
            response_data = str(e)
        flask_app.logger.debug(
            "response: %s\n    headers: %s\n    body: %s\n",
            response,
            response.headers.__repr__(),
            response_data,
        )
        return response

    @flask_app.route("/")
    def root_redirect():
        return redirect(ARGRELAY_GUI_PATH, code = 302)

    flask_app.register_blueprint(create_blueprint_api(flask_app.local_server))
    flask_app.register_blueprint(create_blueprint_gui(
        configure_project_title(flask_app.local_server.server_config.server_configurators),
        configure_project_page_url(flask_app.local_server.server_config.server_configurators),
        server_version,
        flask_app.local_server.server_config.gui_banner_config,
        flask_app.local_server.server_start_time,
        # TODO: make AbstractConfiguration expose only these final methods (and any concatenation of strings, validation, should be hidden inside DefaultConfigurator):
        configure_project_git_commit_time(flask_app.local_server.server_config.server_configurators),
        configure_project_git_commit_url(flask_app.local_server.server_config.server_configurators),
        configure_project_git_commit_display_string(flask_app.local_server.server_config.server_configurators),
        configure_project_git_conf_dir_url(flask_app.local_server.server_config.server_configurators),
        configure_project_git_conf_dir_display_string(flask_app.local_server.server_config.server_configurators),
    ))

    return flask_app


def configure_project_title(
    server_configurators,
) -> str:
    return get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_title(),
        "[unknown]",
    )


def configure_project_page_url(
    server_configurators,
) -> str:
    return get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_page_url(),
        "",
    )


def configure_project_git_commit_time(
    server_configurators,
) -> int:
    return get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_commit_time(),
        0,
    )


def configure_project_git_commit_url(
    server_configurators,
) -> str:
    project_commit_id_url_prefix: str = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_commit_id_url_prefix(),
        None,
    )
    project_git_commit_id: str = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_commit_id(),
        None,
    )
    if (
        project_commit_id_url_prefix is not None
        and
        project_git_commit_id is not None
    ):
        return f"{project_commit_id_url_prefix}{project_git_commit_id}"
    else:
        return ""


def configure_project_git_commit_display_string(
    server_configurators,
) -> str:
    return get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_commit_display_string(),
        "[unknown]",
    )


def configure_project_git_conf_dir_url(
    server_configurators,
) -> Union[str, None]:
    """
    Full URL is going to be formed only if
    *   `project_current_config_path` points to the same Get repo root as `argrelay_dir`
    *   `project_current_config_path` points under `argrelay_dir`
    """
    project_git_files_by_commit_id_url_prefix = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_files_by_commit_id_url_prefix(),
        None,
    )
    project_git_commit_id: str = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_commit_id(),
        None,
    )
    project_git_repo_relative_argrelay_dir: str = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_git_repo_relative_argrelay_dir(),
        None,
    )
    project_current_config_path = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_current_config_path(),
        None,
    )

    # Validation:

    if (
        project_git_files_by_commit_id_url_prefix is None
        or
        project_git_commit_id is None
        or
        project_git_repo_relative_argrelay_dir is None
        or
        project_current_config_path is None
    ):
        return ""

    argrelay_dir_abs_path = os.path.realpath(os.path.abspath(get_argrelay_dir()))
    project_current_config_abs_path = os.path.realpath(os.path.abspath(os.path.join(
        argrelay_dir_abs_path,
        project_current_config_path
    )))

    # This may happen even if paths were joined
    # if `project_current_config_path` is a symlink pointing outside `argrelay_dir_abs_path`:
    if not project_current_config_abs_path.startswith(argrelay_dir_abs_path):
        return ""

    # This may happen if `@/conf` is a sub-dir, and it is another git repo:
    if (
        os.path.realpath(get_git_repo_root_path(argrelay_dir_abs_path))
        !=
        os.path.realpath(get_git_repo_root_path(project_current_config_abs_path))
    ):
        return ""

    # Compose URL:
    project_current_config_path = os.path.relpath(project_current_config_abs_path, argrelay_dir_abs_path)
    return f"{project_git_files_by_commit_id_url_prefix}{project_git_commit_id}{project_git_repo_relative_argrelay_dir}{project_current_config_path}"


def configure_project_git_conf_dir_display_string(
    server_configurators,
) -> str:
    project_current_config_path = get_config_value_once(
        server_configurators,
        lambda server_configurator: server_configurator.provide_project_current_config_path(),
        None,
    )
    if project_current_config_path is not None:
        return project_current_config_path
    else:
        return "[unknown]"


def get_config_value_once(
    server_configurators,
    value_getter: Callable[[AbstractConfigurator], Any],
    default_value: Any,
) -> Any:
    config_value: Union[Any, None] = None
    server_configurator: AbstractConfigurator
    for server_configurator in server_configurators.values():
        if config_value is None:
            config_value = value_getter(server_configurator)
        else:
            if value_getter(server_configurator) is not None:
                # Only one `PluginType.ConfiguratorPlugin` providing
                # same type of value is supported to avoid confusion:
                raise RuntimeError

    if config_value is None:
        config_value = default_value
    return config_value
