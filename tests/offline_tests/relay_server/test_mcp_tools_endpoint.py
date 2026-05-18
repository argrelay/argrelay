from __future__ import annotations

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceInstanceGoto import (
    func_id_goto_service_,
)
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
            ServerOnlyEnvMockBuilder().set_test_data_ids_to_load(["TD_63_37_05_36"])
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_mcp_tools_returns_200(self):
        # given:

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        assert response.status_code == 200

    def test_mcp_tools_content_type_is_json(self):
        # given:

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        assert "application/json" in response.content_type

    def test_mcp_tools_has_tools_list(self):
        # given:

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        response_json = response.get_json()
        assert "tools" in response_json
        assert isinstance(response_json["tools"], list)
        assert len(response_json["tools"]) > 0

    def test_mcp_tools_each_tool_has_required_fields(self):
        # given:

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        tools = response.get_json()["tools"]
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "command_path" in tool
            assert "inputSchema" in tool
            assert isinstance(tool["command_path"], list)
            assert "properties" in tool["inputSchema"]

    def test_mcp_tools_names_have_no_func_id_prefix(self):
        # given:

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        tools = response.get_json()["tools"]
        for tool in tools:
            assert not tool["name"].startswith(
                _func_id_prefix
            ), f"tool name must not start with {_func_id_prefix!r}: {tool['name']!r}"

    def test_mcp_tools_contains_goto_service(self):
        # given:
        expected_tool_name = func_id_goto_service_[len(_func_id_prefix) :]

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        tools = response.get_json()["tools"]
        tool_names = [t["name"] for t in tools]
        assert expected_tool_name in tool_names

        goto_service_tool = next(t for t in tools if t["name"] == expected_tool_name)
        # command_path ends with "goto" then "service":
        assert goto_service_tool["command_path"][-2] == "goto"
        assert goto_service_tool["command_path"][-1] == "service"
        # arg names from service search control:
        tool_properties = goto_service_tool["inputSchema"]["properties"]
        assert "code" in tool_properties
        assert "region" in tool_properties
        assert "service" in tool_properties

    def test_mcp_tools_arg_property_description_is_prop_name(self):
        """
        Verifies inputSchema.properties[arg_name].description carries the prop_name
        for remaining remapping in proxy.
        """
        # given:
        expected_tool_name = func_id_goto_service_[len(_func_id_prefix) :]

        # when:
        response = self.test_client.get(MCP_TOOLS_PATH)

        # then:
        tools = response.get_json()["tools"]
        goto_service_tool = next(t for t in tools if t["name"] == expected_tool_name)
        tool_properties = goto_service_tool["inputSchema"]["properties"]
        assert tool_properties["code"]["description"] == "code_maturity"
        assert tool_properties["region"]["description"] == "geo_region"
