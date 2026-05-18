from __future__ import annotations

import json
import subprocess

from argrelay_lib_root.misc_helper_common import get_argrelay_dir
from argrelay_test_infra.test_infra.ClientServerTestClass import ClientServerTestClass


class ThisTestClass(ClientServerTestClass):
    """
    Smoke test: exe/argrelay_mcp_proxy connects to a live argrelay server.
    Mode #5 (FS_66_17_43_42 test_infra): server-out (started by ClientServerTestClass),
    proxy-out (subprocess with piped stdin/stdout).
    """

    def _run_proxy_with_stdin(
        self,
        stdin_lines: list[str],
        timeout_sec: int = 30,
    ) -> subprocess.CompletedProcess:
        proxy_stdin = "\n".join(stdin_lines) + "\n"
        return subprocess.run(
            args=[f"{get_argrelay_dir()}/exe/argrelay_mcp_proxy"],
            input=proxy_stdin.encode("utf-8"),
            capture_output=True,
            timeout=timeout_sec,
        )

    def test_mcp_proxy_responds_to_initialize(self):
        # given:
        init_msg = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test",
                        "version": "0",
                    },
                },
            }
        )

        # when:
        proxy_proc = self._run_proxy_with_stdin([init_msg])

        # then:
        stdout_text = proxy_proc.stdout.decode("utf-8").strip()
        assert len(stdout_text) > 0, "Expected at least one JSON-RPC response on stdout"
        first_line = stdout_text.splitlines()[0]
        response = json.loads(first_line)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert response.get("id") == 1

    def test_mcp_proxy_initialize_result_has_capabilities(self):
        # given:
        init_msg = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test",
                        "version": "0",
                    },
                },
            }
        )

        # when:
        proxy_proc = self._run_proxy_with_stdin([init_msg])

        # then:
        first_line = proxy_proc.stdout.decode("utf-8").strip().splitlines()[0]
        response = json.loads(first_line)
        result = response["result"]
        assert "capabilities" in result
        assert "serverInfo" in result

    def test_mcp_proxy_tools_list_returns_argrelay_tools(self):
        # given:
        init_msg = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test",
                        "version": "0",
                    },
                },
            }
        )
        initialized_notification = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }
        )
        tools_list_msg = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            }
        )

        # when:
        proxy_proc = self._run_proxy_with_stdin(
            [
                init_msg,
                initialized_notification,
                tools_list_msg,
            ]
        )

        # then:
        stdout_lines = proxy_proc.stdout.decode("utf-8").strip().splitlines()
        # First response is for initialize (id=1), second is for tools/list (id=2):
        tools_list_response = None
        for line in stdout_lines:
            parsed = json.loads(line)
            if parsed.get("id") == 2:
                tools_list_response = parsed
                break

        assert (
            tools_list_response is not None
        ), "Expected tools/list response (id=2) in proxy stdout"
        assert "result" in tools_list_response
        tools = tools_list_response["result"]["tools"]
        assert isinstance(tools, list)
        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        # At minimum, demo functions must be present:
        assert "goto_service" in tool_names
