from __future__ import annotations

import asyncio

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

    def __init__(
        self,
        client_config: ClientConfig,
    ):
        server_conn = client_config.redundant_servers[0]
        from argrelay_api_server_cli.server_spec.const_int import BASE_URL_FORMAT

        self.server_url = BASE_URL_FORMAT.format(
            server_host_name=server_conn.server_host_name,
            server_port_number=server_conn.server_port_number,
        )
        self.http = requests.Session()
        self.mcp_server = mcp.server.Server("argrelay")
        self.tools: list[ToolDesc] = []
        self._tool_map: dict[str, ToolDesc] = {}

    def start(self) -> None:
        mcp_tools_resp = self.http.get(self.server_url + MCP_TOOLS_PATH)
        mcp_tools_resp.raise_for_status()
        self.tools = parse_mcp_tools_response(mcp_tools_resp.json())
        self._tool_map = {tool_desc.name: tool_desc for tool_desc in self.tools}

    def register_handlers(self) -> None:

        @self.mcp_server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [build_mcp_tool(tool_desc) for tool_desc in self.tools]

        @self.mcp_server.call_tool()
        async def call_tool(
            name: str,
            arguments: dict,
        ) -> list[types.TextContent]:
            tool_desc = self._tool_map.get(name)
            if tool_desc is None:
                raise ValueError(f"Unknown tool: {name!r}")
            command_line = build_command_line(tool_desc, arguments or {})
            relay_payload = {
                "server_action": ServerAction.RelayLineArgs.name,
                "command_line": command_line,
                "cursor_cpos": len(command_line),
                "comp_scope": CompScope.ScopeInitial.name,
                "is_debug_enabled": False,
            }
            relay_resp = self.http.post(
                self.server_url + ServerAction.RelayLineArgs.value,
                json=relay_payload,
            )
            relay_resp.raise_for_status()
            relay_result = relay_resp.json()
            remaining_args = extract_remaining(relay_result, tool_desc)
            result_text = format_tool_result(
                relay_result.get("custom_plugin_data", {}),
                remaining_args,
            )
            return [types.TextContent(type="text", text=result_text)]

    async def run_stdio(self) -> None:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream,
                write_stream,
                self.mcp_server.create_initialization_options(),
            )

    def run(self) -> None:
        asyncio.run(self.run_stdio())
