import importlib
import os
from typing import Type

import pkg_resources
from flasgger import Swagger
from flask import Flask

from argrelay import relay_server
from argrelay.data_schema.ServerConfigSchema import server_config_desc
from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.loader_plugin.AbstractLoader import AbstractLoader
from argrelay.meta_data.PluginType import PluginType
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.misc_helper import eprint
from argrelay.mongo_data import MongoClient
from argrelay.mongo_data.MongoServer import MongoServer
from argrelay.relay_server.path_config import create_blueprint
from argrelay.server_spec.const_int import API_SPEC
from argrelay.server_spec.server_data_schema import API_DOCS_UI_PATH

# Set this here (because `require` function may fail in other contexts):
server_version = pkg_resources.require("argrelay")[0].version
server_title = relay_server.__name__

# Delay config load until `load_config()` is called.
# This is to avoid loading it on import which, in turn, allows setting up test env with mocks for config file access.
server_config: ServerConfig

mongo_server = MongoServer()


def load_config():
    global server_config
    server_config = server_config_desc.from_default_file()


def run_plugins():
    """
    Calls each plugin to update :class:`StaticData`.
    """

    eprint(f"plugin_list: {server_config.plugin_list}")

    for plugin_entry in server_config.plugin_list:
        eprint(f"using: {plugin_entry}")
        plugin_module = importlib.import_module(plugin_entry.plugin_module_name)

        if plugin_entry.plugin_type == PluginType.LoaderPlugin:
            plugin_class: Type[AbstractLoader] = getattr(
                plugin_module,
                plugin_entry.plugin_class_name,
            )
            plugin_object: AbstractLoader = plugin_class(plugin_entry.plugin_config)
            # Use loader to update data:
            server_config.static_data = plugin_object.update_static_data(server_config.static_data)
            server_config_desc.object_schema.validate(server_config.static_data)

        if plugin_entry.plugin_type == PluginType.InterpFactoryPlugin:
            plugin_class: Type[AbstractInterpFactory] = getattr(
                plugin_module,
                plugin_entry.plugin_class_name,
            )
            plugin_object: AbstractInterpFactory = plugin_class(plugin_entry.plugin_config)
            # Store instance of factory under specified id for future use:
            server_config.interp_factories[plugin_entry.plugin_id] = plugin_object


def create_app():
    """
    The function prevents running the code inside it on import - necessary for pre-test mocking.
    Note that Flask may rely on specific name `create_app` to find this factory:
    https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/#using-applications
    """

    flask_app = Flask(relay_server.__name__)

    load_config()
    run_plugins()
    mongo_server.start_mongo_server(server_config.mongo_config)

    mongo_client = MongoClient.get_mongo_client(server_config.mongo_config)
    mongo_db = mongo_client[server_config.mongo_config.database_name]
    MongoClient.store_objects(mongo_db, server_config.static_data)

    swagger_template = {
        "info": {
            "title": server_title,
            "version": server_version,
            "description": f"{os.getcwd()}: python -m argrelay.relay_server",
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

    root_blueprint = create_blueprint(server_config, mongo_db)
    flask_app.register_blueprint(root_blueprint)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    # noinspection PyUnboundLocalVariable
    app.run(
        # Contrary to the intention, if IDE debug is needed, set `debug` to `False` to avoid reloader:
        # https://stackoverflow.com/questions/28241989/flask-app-restarting-with-stat/53790400#53790400
        # TODO: Disabled debug to make sure reloader does not restart server (which does not work with Mongo DB):
        debug = False,
        host = server_config.connection_config.server_host_name,
        port = server_config.connection_config.server_port_number,
    )
