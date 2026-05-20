from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types

from argrelay_app_mcp_proxy.mcp_proxy.ArgrelayMcpProxy import ArgrelayMcpProxy
from argrelay_app_mcp_proxy.mcp_proxy.McpProxyConfig import McpProxyConfig
from argrelay_app_mcp_proxy.mcp_proxy.ToolBuilder import ToolDesc
from argrelay_lib_root.schema_config.ConnectionConfig import ConnectionConfig
from argrelay_schema_config_client.runtime_data_client_app.ClientConfig import (
    ClientConfig,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder
from argrelay_test_infra.test_infra.ServerOnlyTestClass import ServerOnlyTestClass

_func_id_prefix = "func_id_"


def _make_client_config(
    server_host_name: str,
    server_port_number: int,
) -> ClientConfig:
    return ClientConfig(
        __comment__="test",
        use_local_requests=False,
        optimize_completion_request=False,
        redundant_servers=[
            ConnectionConfig(
                server_host_name=server_host_name,
                server_port_number=server_port_number,
            ),
        ],
        show_pending_spinner=False,
        spinless_sleep_sec=0.0,
    )


class ThisTestClass(ServerOnlyTestClass):
    """
    Tests for ArgrelayMcpProxy.start() against in-process server.
    Mode #7-ext (FS_66_17_43_42 test_infra): server-in via Flask test_client,
    proxy HTTP calls intercepted to route through Flask test_client.
    """

    def setUp(self):
        super().setUp()
        self.create_server_in_mocked_env(
            ServerOnlyEnvMockBuilder().set_test_data_ids_to_load(["TD_63_37_05_36"])
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def _make_proxy(self) -> ArgrelayMcpProxy:
        client_config = _make_client_config("localhost", 8787)
        mcp_proxy_config = McpProxyConfig(
            __comment__="test",
            log_dir_rel_path="/tmp/argrelay_test_mcp_proxy_logs",
        )
        proxy = ArgrelayMcpProxy(client_config, mcp_proxy_config)

        test_client = self.test_client

        def _mock_http_get(url, **kwargs):
            path = url.replace("http://localhost:8787", "")
            flask_response = test_client.get(path)
            mock_resp = MagicMock()
            mock_resp.json.return_value = json.loads(flask_response.data)
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        proxy.http.get = _mock_http_get
        return proxy

    def test_start_populates_tools(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        assert len(proxy.tools) > 0

    def test_start_populates_tool_map(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        assert len(proxy._tool_map) > 0

    def test_start_tool_map_keys_match_tool_names(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        for tool_desc in proxy.tools:
            assert tool_desc.name in proxy._tool_map
            assert proxy._tool_map[tool_desc.name].name == tool_desc.name

    def test_start_tools_are_tool_desc_instances(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        for tool_desc in proxy.tools:
            assert isinstance(tool_desc, ToolDesc)

    def test_start_tool_names_have_no_func_id_prefix(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        for tool_desc in proxy.tools:
            assert not tool_desc.name.startswith(
                _func_id_prefix
            ), f"tool name must not start with {_func_id_prefix!r}: {tool_desc.name!r}"

    def test_start_tool_desc_has_command_path(self):
        # given:
        proxy = self._make_proxy()

        # when:
        proxy.start()

        # then:
        for tool_desc in proxy.tools:
            assert isinstance(tool_desc.command_path, list)
            assert len(tool_desc.command_path) > 0

    def test_register_handlers_does_not_throw(self):
        # given:
        proxy = self._make_proxy()
        proxy.start()

        # when/then:
        proxy.register_handlers()

    def _make_started_proxy(
        self,
        log_dir_rel_path: str,
    ) -> ArgrelayMcpProxy:
        """Proxy with GET and POST mocked, started and handlers registered."""
        client_config = _make_client_config("localhost", 8787)
        mcp_proxy_config = McpProxyConfig(
            __comment__="test",
            log_dir_rel_path=log_dir_rel_path,
        )
        proxy = ArgrelayMcpProxy(client_config, mcp_proxy_config)
        test_client = self.test_client

        def _mock_http_get(url, **kwargs):
            path = url.replace("http://localhost:8787", "")
            flask_response = test_client.get(path)
            mock_resp = MagicMock()
            mock_resp.json.return_value = json.loads(flask_response.data)
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        def _mock_http_post(url, json=None, **kwargs):
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "custom_plugin_data": {},
                "envelope_containers": [],
            }
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        proxy.http.get = _mock_http_get
        proxy.http.post = _mock_http_post
        proxy.start()
        proxy.register_handlers()
        return proxy

    async def _run_call_tool(
        self,
        proxy: ArgrelayMcpProxy,
        tool_name: str,
        tool_arguments: dict,
    ):
        """Invoke call_tool handler with mocked subprocess and request context."""
        from mcp.server.lowlevel.server import request_ctx
        from mcp.shared.context import RequestContext

        proxy._invoke_lock = asyncio.Lock()

        mock_proc = MagicMock()
        mock_proc.stdin.drain = AsyncMock()
        mock_proc.wait = AsyncMock()
        mock_proc.returncode = 0

        mock_session = MagicMock()
        mock_ctx = RequestContext(
            request_id="test-1",
            meta=None,
            session=mock_session,
            lifespan_context=None,
        )
        ctx_token = request_ctx.set(mock_ctx)
        try:
            with patch(
                "asyncio.create_subprocess_exec",
                new=AsyncMock(return_value=mock_proc),
            ):
                req = types.CallToolRequest(
                    params=types.CallToolRequestParams(
                        name=tool_name,
                        arguments=tool_arguments,
                    ),
                )
                handler = proxy.mcp_server.request_handlers[types.CallToolRequest]
                return await handler(req)
        finally:
            request_ctx.reset(ctx_token)

    def test_call_tool_unknown_tool_is_error(self):
        with tempfile.TemporaryDirectory() as log_dir:
            proxy = self._make_started_proxy(log_dir)

            server_result = asyncio.run(
                self._run_call_tool(proxy, "nonexistent_tool_xyz", {})
            )

        assert server_result.root.isError is True

    def test_call_tool_known_tool_is_not_error(self):
        with tempfile.TemporaryDirectory() as log_dir:
            proxy = self._make_started_proxy(log_dir)
            tool_name = proxy.tools[0].name

            server_result = asyncio.run(self._run_call_tool(proxy, tool_name, {}))

        assert server_result.root.isError is False

    def test_call_tool_activity_log_records_name_and_arguments(self):
        with tempfile.TemporaryDirectory() as log_dir:
            proxy = self._make_started_proxy(log_dir)
            tool_name = proxy.tools[0].name
            tool_arguments = {}

            asyncio.run(self._run_call_tool(proxy, tool_name, tool_arguments))

            activity_log_files = list(Path(log_dir).glob("*.activity.log"))
            assert len(activity_log_files) == 1
            log_content = activity_log_files[0].read_text()

        assert f"name={tool_name!r}" in log_content
        assert f"arguments={tool_arguments!r}" in log_content
