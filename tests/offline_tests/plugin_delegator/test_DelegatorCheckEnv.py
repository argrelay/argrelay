from __future__ import annotations

from argrelay_lib_root.enum_desc.CheckEnvField import CheckEnvField
from argrelay_lib_root.enum_desc.CompScope import CompScope
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder
from argrelay_test_infra.test_infra.ServerOnlyTestClass import ServerOnlyTestClass


class ThisTestClass(ServerOnlyTestClass):
    """
    Verify run_invoke_control returns InvocationInput with custom_plugin_data populated.

    Bug: stray `return 0` before `return invocation_input` in run_invoke_control causes
    server to dump `{}` (int has no InvocationInput fields), client receives empty dict,
    custom_plugin_data is missing.
    """

    def setUp(self):
        super().setUp()
        self.create_server_in_mocked_env(
            ServerOnlyEnvMockBuilder().set_test_data_ids_to_load(["TD_63_37_05_36"])
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def _post_relay_line_args(self, command_line: str) -> dict:
        relay_payload = {
            "server_action": ServerAction.RelayLineArgs.name,
            "command_line": command_line,
            "cursor_cpos": len(command_line),
            "comp_scope": CompScope.ScopeInitial.name,
            "is_debug_enabled": False,
        }
        resp = self.test_client.post(
            ServerAction.RelayLineArgs.value,
            json=relay_payload,
        )
        self.assertEqual(200, resp.status_code)
        return resp.get_json()

    def test_server_version_relay_result_has_custom_plugin_data(self):
        relay_result = self._post_relay_line_args("argrelay.check_env server_version")
        self.assertIn("custom_plugin_data", relay_result)
        self.assertIn(
            CheckEnvField.server_version.name,
            relay_result["custom_plugin_data"],
        )

    def test_server_commit_relay_result_has_custom_plugin_data(self):
        relay_result = self._post_relay_line_args("argrelay.check_env server_commit")
        self.assertIn("custom_plugin_data", relay_result)
        self.assertIn(
            CheckEnvField.server_git_commit_id.name,
            relay_result["custom_plugin_data"],
        )

    def test_server_start_time_relay_result_has_custom_plugin_data(self):
        relay_result = self._post_relay_line_args(
            "argrelay.check_env server_start_time"
        )
        self.assertIn("custom_plugin_data", relay_result)
        self.assertIn(
            CheckEnvField.server_start_time.name,
            relay_result["custom_plugin_data"],
        )
