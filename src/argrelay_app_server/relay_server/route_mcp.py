from __future__ import annotations

from json import dumps

from flask import (
    Blueprint,
    Response,
)

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_app_server.handler_request.McpToolsServerRequestHandler import (
    McpToolsServerRequestHandler,
)
from argrelay_app_server.relay_server.LocalServer import LocalServer


def create_blueprint_mcp(local_server: LocalServer):
    blueprint_mcp = Blueprint("blueprint_mcp", __name__)

    mcp_tools_handler = McpToolsServerRequestHandler(local_server)

    @blueprint_mcp.route(MCP_TOOLS_PATH, methods=["get"])
    def mcp_tools():
        response_dict = mcp_tools_handler.handle_request()
        return Response(dumps(response_dict), mimetype="application/json")

    return blueprint_mcp
