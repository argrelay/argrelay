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
            args=[
                f"{get_argrelay_dir()}/exe/argrelay_mcp_proxy",
            ],
            input=proxy_stdin.encode("utf-8"),
            capture_output=True,
            timeout=timeout_sec,
        )

    def test_mcp_proxy_responds_to_initialize(self):
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

        proxy_proc = self._run_proxy_with_stdin([init_msg])

        stdout_text = proxy_proc.stdout.decode("utf-8").strip()
        self.assertTrue(
            len(stdout_text) > 0,
            "Expected at least one JSON-RPC response on stdout",
        )
        first_line = stdout_text.splitlines()[0]
        response = json.loads(first_line)
        self.assertEqual("2.0", response["jsonrpc"])
        self.assertIn("result", response)
        self.assertEqual(1, response.get("id"))

    def test_mcp_proxy_initialize_result_has_capabilities(self):
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

        proxy_proc = self._run_proxy_with_stdin([init_msg])

        first_line = proxy_proc.stdout.decode("utf-8").strip().splitlines()[0]
        response = json.loads(first_line)
        result = response["result"]
        self.assertIn("capabilities", result)
        self.assertIn("serverInfo", result)

    def test_mcp_proxy_tools_list_returns_argrelay_tools(self):
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

        proxy_proc = self._run_proxy_with_stdin(
            [
                init_msg,
                initialized_notification,
                tools_list_msg,
            ]
        )

        stdout_lines = proxy_proc.stdout.decode("utf-8").strip().splitlines()
        # First response is for initialize (id=1), second is for tools/list (id=2):
        tools_list_response = None
        for line in stdout_lines:
            parsed = json.loads(line)
            if parsed.get("id") == 2:
                tools_list_response = parsed
                break

        self.assertIsNotNone(
            tools_list_response,
            "Expected tools/list response (id=2) in proxy stdout",
        )
        self.assertIn("result", tools_list_response)
        tools = tools_list_response["result"]["tools"]
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        tool_names = [t["name"] for t in tools]
        # At minimum, demo functions must be present:
        self.assertIn("goto_service", tool_names)
