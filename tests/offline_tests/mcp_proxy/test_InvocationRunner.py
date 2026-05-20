from __future__ import annotations

import json
import subprocess
import sys
import unittest

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_lib_root.enum_desc.CompScope import CompScope
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder
from argrelay_test_infra.test_infra.ServerOnlyTestClass import ServerOnlyTestClass

_RUNNER_MODULE = "argrelay_app_mcp_proxy.mcp_proxy.InvocationRunner"
_ECHO_ARGS_TOOL_NAME = "echo_args"


def _run_runner(
    relay_result_dict: dict, timeout_sec: int = 30
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", _RUNNER_MODULE],
        input=json.dumps(relay_result_dict).encode(),
        capture_output=True,
        timeout=timeout_sec,
    )


class TestInvocationRunnerErrors(unittest.TestCase):
    """
    Error-handling tests — no server required.
    InvocationRunner must exit 1 and write traceback to stderr on bad input.
    """

    def test_exits_1_on_invalid_json(self):
        proc = subprocess.run(
            [sys.executable, "-m", _RUNNER_MODULE],
            input=b"not valid json{{",
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(1, proc.returncode)

    def test_stderr_has_traceback_on_invalid_json(self):
        proc = subprocess.run(
            [sys.executable, "-m", _RUNNER_MODULE],
            input=b"not valid json{{",
            capture_output=True,
            timeout=10,
        )
        self.assertGreater(len(proc.stderr), 0)
        self.assertIn(b"Traceback", proc.stderr)

    def test_exits_1_on_missing_required_fields(self):
        proc = _run_runner({})
        self.assertEqual(1, proc.returncode)

    def test_stderr_has_traceback_on_missing_required_fields(self):
        proc = _run_runner({})
        self.assertGreater(len(proc.stderr), 0)
        self.assertIn(b"Traceback", proc.stderr)

    def test_stdout_empty_on_error(self):
        proc = _run_runner({})
        self.assertEqual(b"", proc.stdout)


class TestInvocationRunnerWithServer(ServerOnlyTestClass):
    """
    Integration tests — InvocationRunner invoked with a real relay_result
    obtained from an in-process Flask server.
    """

    def setUp(self):
        super().setUp()
        self.create_server_in_mocked_env(
            ServerOnlyEnvMockBuilder().set_test_data_ids_to_load(["TD_63_37_05_36"])
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def _get_relay_result_for_echo_args(self) -> dict:
        mcp_resp = self.test_client.get(MCP_TOOLS_PATH)
        tools = mcp_resp.get_json()["tools"]
        echo_tool = next(t for t in tools if t["name"] == _ECHO_ARGS_TOOL_NAME)
        command_line = " ".join(echo_tool["command_path"])
        relay_payload = {
            "server_action": ServerAction.RelayLineArgs.name,
            "command_line": command_line,
            "cursor_cpos": len(command_line),
            "comp_scope": CompScope.ScopeInitial.name,
            "is_debug_enabled": False,
        }
        relay_resp = self.test_client.post(
            ServerAction.RelayLineArgs.value,
            json=relay_payload,
        )
        self.assertEqual(200, relay_resp.status_code)
        return relay_resp.get_json()

    def test_exits_0_for_echo_args(self):
        relay_result = self._get_relay_result_for_echo_args()
        proc = _run_runner(relay_result)
        self.assertEqual(0, proc.returncode)

    def test_stdout_contains_output_for_echo_args(self):
        relay_result = self._get_relay_result_for_echo_args()
        proc = _run_runner(relay_result)
        self.assertGreater(len(proc.stdout.strip()), 0)

    def test_stderr_empty_on_success(self):
        relay_result = self._get_relay_result_for_echo_args()
        proc = _run_runner(relay_result)
        self.assertEqual(b"", proc.stderr)

    def test_does_not_mutate_parent_sys_stdout(self):
        # Subprocess runs in isolated process — parent sys.stdout must not change.
        original_stdout = sys.stdout
        relay_result = self._get_relay_result_for_echo_args()
        _run_runner(relay_result)
        self.assertIs(original_stdout, sys.stdout)

    def test_does_not_mutate_parent_sys_stderr(self):
        original_stderr = sys.stderr
        relay_result = self._get_relay_result_for_echo_args()
        _run_runner(relay_result)
        self.assertIs(original_stderr, sys.stderr)
