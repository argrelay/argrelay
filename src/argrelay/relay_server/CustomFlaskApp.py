import logging
import os

import pkg_resources
from argrelay import relay_server
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.route_api import create_blueprint_api
from argrelay.relay_server.route_gui import create_blueprint_gui
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.const_int import API_SPEC_PATH, API_DOCS_PATH, ARGRELAY_GUI_PATH
from flasgger import Swagger
from flask import Flask, request, redirect

# Set this here (because `require` function may fail in other contexts):
server_version = pkg_resources.require("argrelay")[0].version
server_title = relay_server.__name__


class CustomFlaskApp(Flask):
    """
    This is an API-wrapper exposing `LocalServer` over the network.
    """

    local_server: LocalServer

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
        self.local_server = LocalServer(server_config_desc.from_default_file())

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
        server_version,
        flask_app.local_server.server_config.gui_banner_config,
    ))

    return flask_app
