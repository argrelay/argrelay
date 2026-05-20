from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import mcp.server
import mcp.server.stdio
import mcp.types as types
import requests

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_lib_root.misc_helper_common import get_argrelay_dir
from argrelay_app_mcp_proxy.mcp_proxy.McpProxyConfig import McpProxyConfig
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


async def _send_heartbeat(
    server_session,
    progress_token,
    interval_sec: float,
    invoke_logger: logging.Logger,
) -> None:
    elapsed_sec = 0.0
    while True:
        await asyncio.sleep(interval_sec)
        elapsed_sec += interval_sec
        invoke_logger.info("call_tool: heartbeat; elapsed_sec=%.0f", elapsed_sec)
        await server_session.send_progress_notification(
            progress_token,
            elapsed_sec,
            None,
            f"running {elapsed_sec:.0f}s",
        )


class ArgrelayMcpProxy:

    def __init__(
        self,
        client_config: ClientConfig,
        mcp_proxy_config: McpProxyConfig,
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
        self._log_dir = Path(mcp_proxy_config.log_dir_rel_path)
        self._heartbeat_interval_sec: float = mcp_proxy_config.heartbeat_interval_sec
        # _invoke_lock created inside run_stdio() (inside asyncio.run()) to ensure
        # it binds to the correct event loop on all Python versions.
        self._invoke_lock: asyncio.Lock | None = None
        self._proxy_logger: logging.Logger | None = None

    def start(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        proxy_log_path = self._log_dir / "argrelay_mcp_proxy.proxy.log"
        handler = logging.FileHandler(proxy_log_path, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger = logging.getLogger("argrelay_mcp_proxy")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        self._proxy_logger = logger
        self._proxy_logger.info("proxy start: server_url=%s", self.server_url)
        mcp_tools_resp = self.http.get(self.server_url + MCP_TOOLS_PATH)
        mcp_tools_resp.raise_for_status()
        self.tools = parse_mcp_tools_response(mcp_tools_resp.json())
        self._tool_map = {tool_desc.name: tool_desc for tool_desc in self.tools}
        self._proxy_logger.info("proxy start: loaded %d tools", len(self.tools))

    def register_handlers(self) -> None:

        @self.mcp_server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [build_mcp_tool(tool_desc) for tool_desc in self.tools]

        @self.mcp_server.call_tool()
        async def call_tool(
            name: str,
            arguments: dict,
        ) -> list[types.TextContent]:
            self._proxy_logger.info("call_tool: name=%r arguments=%r", name, arguments)
            tool_desc = self._tool_map.get(name)
            if tool_desc is None:
                self._proxy_logger.error("call_tool: unknown tool %r", name)
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

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            stdout_path = self._log_dir / f"argrelay_mcp_proxy.{timestamp}.stdout.log"
            stderr_path = self._log_dir / f"argrelay_mcp_proxy.{timestamp}.stderr.log"
            activity_path = (
                self._log_dir / f"argrelay_mcp_proxy.{timestamp}.activity.log"
            )

            invoke_logger = logging.getLogger(f"argrelay_mcp_proxy.{timestamp}")
            invoke_logger.setLevel(logging.DEBUG)
            invoke_logger.propagate = False
            invoke_handler = logging.FileHandler(
                activity_path, mode="w", encoding="utf-8"
            )
            invoke_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            invoke_logger.addHandler(invoke_handler)

            try:
                invoke_logger.info("call_tool: name=%r arguments=%r", name, arguments)
                invoke_logger.info("call_tool: command_line=%r", command_line)
                request_ctx = self.mcp_server.request_context
                progress_token = (
                    request_ctx.meta.progressToken if request_ctx.meta else None
                )
                invoke_logger.info(
                    "call_tool: acquiring invoke_lock; progress_token=%r heartbeat_interval_sec=%r stdout_log=%s stderr_log=%s activity_log=%s",
                    progress_token,
                    self._heartbeat_interval_sec,
                    stdout_path,
                    stderr_path,
                    activity_path,
                )
                async with self._invoke_lock:
                    invoke_logger.info("call_tool: lock acquired; starting subprocess")
                    sub_env = os.environ.copy()
                    sub_env["ARGRELAY_DIR"] = get_argrelay_dir()
                    with (
                        open(stdout_path, "wb") as stdout_file,
                        open(stderr_path, "wb") as stderr_file,
                    ):
                        sub_proc = await asyncio.create_subprocess_exec(
                            sys.executable,
                            "-m",
                            "argrelay_app_mcp_proxy.mcp_proxy.InvocationRunner",
                            stdin=asyncio.subprocess.PIPE,
                            stdout=stdout_file,
                            stderr=stderr_file,
                            env=sub_env,
                        )
                        sub_proc.stdin.write(json.dumps(relay_result).encode())
                        await sub_proc.stdin.drain()
                        sub_proc.stdin.close()
                        heartbeat_task = None
                        if progress_token is not None:
                            heartbeat_task = asyncio.create_task(
                                _send_heartbeat(
                                    request_ctx.session,
                                    progress_token,
                                    self._heartbeat_interval_sec,
                                    invoke_logger,
                                )
                            )
                        try:
                            await sub_proc.wait()
                        finally:
                            if heartbeat_task is not None:
                                heartbeat_task.cancel()
                                try:
                                    await heartbeat_task
                                except asyncio.CancelledError:
                                    pass
                    exit_code = sub_proc.returncode
                    invoke_logger.info(
                        "call_tool: subprocess done; exit_code=%r", exit_code
                    )

                stdout_text = stdout_path.read_text()
                stderr_text = stderr_path.read_text()

                remaining_args = extract_remaining(relay_result, tool_desc)
                result_text = format_tool_result(
                    relay_result.get("custom_plugin_data", {}),
                    remaining_args,
                )
                result_text += f"\nexit_code: {exit_code}"
                result_text += f"\nstdout_log: {stdout_path}"
                result_text += f"\nstderr_log: {stderr_path}"
                result_text += f"\nactivity_log: {activity_path}"
                if stdout_text:
                    result_text += f"\nstdout:\n{stdout_text}"
                if stderr_text:
                    result_text += f"\nstderr:\n{stderr_text}"

                invoke_logger.info("call_tool: returning result")
            finally:
                invoke_handler.flush()
                invoke_handler.close()
                invoke_logger.removeHandler(invoke_handler)
            is_error = exit_code != 0
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)],
                isError=is_error,
            )

    async def run_stdio(self) -> None:
        # Create lock here — inside asyncio.run() — so it binds to the correct event loop.
        self._invoke_lock = asyncio.Lock()
        self._proxy_logger.info("run_stdio: starting stdio_server")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            self._proxy_logger.info("run_stdio: stdio_server open; running mcp_server")
            try:
                await self.mcp_server.run(
                    read_stream,
                    write_stream,
                    self.mcp_server.create_initialization_options(),
                )
            except BaseException:
                self._proxy_logger.exception("run_stdio: mcp_server.run raised")
                raise
            finally:
                self._proxy_logger.info("run_stdio: mcp_server.run exited")

    def run(self) -> None:
        asyncio.run(self.run_stdio())
