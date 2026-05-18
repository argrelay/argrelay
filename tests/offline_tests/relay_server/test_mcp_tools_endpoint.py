from __future__ import annotations

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceInstanceGoto import (
    func_id_goto_service_,
)
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder
from argrelay_test_infra.test_infra.ServerOnlyTestClass import ServerOnlyTestClass

_func_id_prefix = "func_id_"


class ThisTestClass(ServerOnlyTestClass):
    """
    Tests for GET /mcp_tools/ endpoint (FS_66_17_43_42 test_infra / special test mode #7).

    Server runs in-process via Flask test_client.
    No argrelay client code involved.
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

    def test_mcp_tools_returns_200(self):
        response = self.test_client.get(MCP_TOOLS_PATH)

        self.assertEqual(200, response.status_code)

    def test_mcp_tools_content_type_is_json(self):
        response = self.test_client.get(MCP_TOOLS_PATH)

        self.assertIn("application/json", response.content_type)

    def test_mcp_tools_has_tools_list(self):
        response = self.test_client.get(MCP_TOOLS_PATH)
        response_json = response.get_json()

        self.assertIn("tools", response_json)
        self.assertIsInstance(response_json["tools"], list)
        self.assertGreater(len(response_json["tools"]), 0)

    def test_mcp_tools_each_tool_has_required_fields(self):
        response = self.test_client.get(MCP_TOOLS_PATH)
        tools = response.get_json()["tools"]

        test_cases = [
            (line_no(), tool_name) for tool_name in [t["name"] for t in tools]
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    tool_name,
                ) = test_case
                tool = next(t for t in tools if t["name"] == tool_name)
                self.assertIn("name", tool)
                self.assertIn("description", tool)
                self.assertIn("command_path", tool)
                self.assertIn("inputSchema", tool)
                self.assertIsInstance(tool["command_path"], list)
                self.assertIn("properties", tool["inputSchema"])

    def test_mcp_tools_names_have_no_func_id_prefix(self):
        response = self.test_client.get(MCP_TOOLS_PATH)
        tools = response.get_json()["tools"]

        for tool in tools:
            self.assertFalse(
                tool["name"].startswith(_func_id_prefix),
                f"tool name must not start with {_func_id_prefix!r}: {tool['name']!r}",
            )

    def test_mcp_tools_contains_goto_service(self):
        response = self.test_client.get(MCP_TOOLS_PATH)
        tools = response.get_json()["tools"]
        tool_names = [t["name"] for t in tools]

        expected_tool_name = func_id_goto_service_[len(_func_id_prefix) :]
        self.assertIn(expected_tool_name, tool_names)

        goto_service_tool = next(t for t in tools if t["name"] == expected_tool_name)
        # command_path ends with "goto" then "service":
        self.assertEqual("goto", goto_service_tool["command_path"][-2])
        self.assertEqual("service", goto_service_tool["command_path"][-1])
        # arg names from service search control:
        tool_properties = goto_service_tool["inputSchema"]["properties"]
        self.assertIn("code", tool_properties)
        self.assertIn("region", tool_properties)
        self.assertIn("service", tool_properties)

    def test_mcp_tools_arg_property_description_is_prop_name(self):
        """Verifies inputSchema.properties[arg_name].description carries the prop_name for remaining remapping."""
        response = self.test_client.get(MCP_TOOLS_PATH)
        tools = response.get_json()["tools"]
        expected_tool_name = func_id_goto_service_[len(_func_id_prefix) :]
        goto_service_tool = next(t for t in tools if t["name"] == expected_tool_name)
        tool_properties = goto_service_tool["inputSchema"]["properties"]

        self.assertEqual("code_maturity", tool_properties["code"]["description"])
        self.assertEqual("geo_region", tool_properties["region"]["description"])
