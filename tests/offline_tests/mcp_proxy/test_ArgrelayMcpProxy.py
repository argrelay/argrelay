from __future__ import annotations

import json
from unittest.mock import MagicMock

from argrelay_app_mcp_proxy.mcp_proxy.ArgrelayMcpProxy import ArgrelayMcpProxy
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
            ServerOnlyEnvMockBuilder().set_test_data_ids_to_load(
                [
                    "TD_63_37_05_36",  # demo
                ]
            )
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def _make_proxy(self) -> ArgrelayMcpProxy:
        client_config = _make_client_config("localhost", 8787)
        proxy = ArgrelayMcpProxy(client_config)

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
        proxy = self._make_proxy()

        proxy.start()

        self.assertGreater(len(proxy.tools), 0)

    def test_start_populates_tool_map(self):
        proxy = self._make_proxy()

        proxy.start()

        self.assertGreater(len(proxy._tool_map), 0)

    def test_start_tool_map_keys_match_tool_names(self):
        proxy = self._make_proxy()

        proxy.start()

        for tool_desc in proxy.tools:
            self.assertIn(tool_desc.name, proxy._tool_map)
            self.assertEqual(tool_desc.name, proxy._tool_map[tool_desc.name].name)

    def test_start_tools_are_tool_desc_instances(self):
        proxy = self._make_proxy()

        proxy.start()

        for tool_desc in proxy.tools:
            self.assertIsInstance(tool_desc, ToolDesc)

    def test_start_tool_names_have_no_func_id_prefix(self):
        proxy = self._make_proxy()

        proxy.start()

        for tool_desc in proxy.tools:
            self.assertFalse(
                tool_desc.name.startswith(_func_id_prefix),
                f"tool name must not start with {_func_id_prefix!r}: {tool_desc.name!r}",
            )

    def test_start_tool_desc_has_command_path(self):
        proxy = self._make_proxy()

        proxy.start()

        for tool_desc in proxy.tools:
            self.assertIsInstance(tool_desc.command_path, list)
            self.assertGreater(len(tool_desc.command_path), 0)

    def test_register_handlers_does_not_throw(self):
        proxy = self._make_proxy()
        proxy.start()

        proxy.register_handlers()
