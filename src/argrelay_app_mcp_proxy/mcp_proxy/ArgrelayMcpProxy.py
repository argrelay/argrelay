from __future__ import annotations

import asyncio
import json

import mcp.server
import mcp.server.stdio
import mcp.types as types
import requests

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_app_mcp_proxy.mcp_proxy.ToolBuilder import (
    ToolDesc,
    build_command_line,
    build_mcp_tool,
    extract_remaining,
    format_tool_result,
    parse_mcp_tools_response,
)
from argrelay_lib_root.enum_desc.CompScope import CompScope
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_schema_config_client.runtime_data_client_app.ClientConfig import (
    ClientConfig,
)


class ArgrelayMcpProxy:

    def __init__(self, client_config: ClientConfig):
        conn = client_config.redundant_servers[0]
        from argrelay_api_server_cli.server_spec.const_int import BASE_URL_FORMAT

        self.server_url = BASE_URL_FORMAT.format(
            server_host_name=conn.server_host_name,
            server_port_number=conn.server_port_number,
        )
        self.http = requests.Session()
        self.mcp_server = mcp.server.Server("argrelay")
        self.tools: list[ToolDesc] = []
        self._tool_map: dict[str, ToolDesc] = {}

    def start(self) -> None:
        resp = self.http.get(self.server_url + MCP_TOOLS_PATH)
        resp.raise_for_status()
        self.tools = parse_mcp_tools_response(resp.json())
        self._tool_map = {t.name: t for t in self.tools}

    def register_handlers(self) -> None:

        @self.mcp_server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [build_mcp_tool(t) for t in self.tools]

        @self.mcp_server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            tool = self._tool_map[name]
            command_line = build_command_line(tool, arguments or {})
            payload = {
                "server_action": ServerAction.RelayLineArgs.name,
                "command_line": command_line,
                "cursor_cpos": len(command_line),
                "comp_scope": CompScope.ScopeInitial.name,
                "is_debug_enabled": False,
            }
            resp = self.http.post(
                self.server_url + ServerAction.RelayLineArgs.value,
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            remaining = extract_remaining(result, tool)
            text = format_tool_result(result.get("custom_plugin_data", {}), remaining)
            return [types.TextContent(type="text", text=text)]

    async def run_stdio(self) -> None:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream,
                write_stream,
                self.mcp_server.create_initialization_options(),
            )

    def run(self) -> None:
        asyncio.run(self.run_stdio())
