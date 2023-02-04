import os

import pkg_resources
from flasgger import Swagger
from flask import Flask

from argrelay import relay_server
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.path_config import create_blueprint
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.const_int import API_SPEC
from argrelay.server_spec.server_data_schema import API_DOCS_UI_PATH

# Set this here (because `require` function may fail in other contexts):
server_version = pkg_resources.require("argrelay")[0].version
server_title = relay_server.__name__


class CustomFlaskApp(Flask):
    """
    This is an API-wrapper exposing `LocalServer` over the network.
    """

    local_server: LocalServer

    def __init__(self, import_name: str):
        super().__init__(import_name)
        self.local_server = LocalServer(server_config_desc.from_default_file())

    def run_with_config(self):
        self.run(
            # Contrary to the intention, if IDE debug is needed, set `debug` to `False` to avoid reloader:
            # https://stackoverflow.com/questions/28241989/flask-app-restarting-with-stat/53790400#53790400
            # TODO: Disabled debug to make sure reloader does not restart server (which does not work with Mongo DB):
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

    flask_app = CustomFlaskApp(relay_server.__name__)

    flask_app.local_server.start_local_server()

    swagger_template = {
        "info": {
            "title": server_title,
            "version": server_version,
            "description": f"{os.getcwd()}: run_argrelay_server",
        },
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "relay_server",
                "route": API_SPEC,
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            },
        ],
        # TODO: Is this needed? If removed, apidocs do not show:
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": API_DOCS_UI_PATH,
    }

    Swagger(
        flask_app,
        template = swagger_template,
        config = swagger_config,
    )

    root_blueprint = create_blueprint(flask_app.local_server)
    flask_app.register_blueprint(root_blueprint)

    return flask_app
