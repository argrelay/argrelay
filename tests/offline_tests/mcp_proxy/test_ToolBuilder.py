from __future__ import annotations

from argrelay_app_mcp_proxy.mcp_proxy.ToolBuilder import (
    build_command_line,
    build_mcp_tool,
    extract_remaining,
    format_tool_result,
    parse_mcp_tools_response,
    ToolDesc,
)
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass

_sample_response_dict = {
    "tools": [
        {
            "name": "goto_service",
            "description": "Go to service",
            "command_path": ["some_command", "goto", "service"],
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "code_maturity"},
                    "region": {"type": "string", "description": "geo_region"},
                    "service": {"type": "string", "description": "service_name"},
                },
            },
        },
        {
            "name": "list_host",
            "description": "List hosts",
            "command_path": ["some_command", "list", "host"],
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "code_maturity"},
                    "host": {"type": "string", "description": "host_name"},
                },
            },
        },
    ]
}


class ThisTestClass(BaseTestClass):
    """
    Tests for ToolBuilder pure functions (FS_66_17_43_42 test_infra / special test mode #9).

    No server, no client, no network.
    """

    ####################################################################################################################
    # parse_mcp_tools_response

    def test_parse_mcp_tools_response_empty_dict(self):
        result = parse_mcp_tools_response({})

        self.assertEqual([], result)

    def test_parse_mcp_tools_response_empty_tools_list(self):
        result = parse_mcp_tools_response({"tools": []})

        self.assertEqual([], result)

    def test_parse_mcp_tools_response_returns_tool_desc_list(self):
        result = parse_mcp_tools_response(_sample_response_dict)

        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], ToolDesc)
        self.assertIsInstance(result[1], ToolDesc)

    def test_parse_mcp_tools_response_populates_tool_desc_fields(self):
        result = parse_mcp_tools_response(_sample_response_dict)
        goto_service_tool = result[0]

        self.assertEqual("goto_service", goto_service_tool.name)
        self.assertEqual("Go to service", goto_service_tool.description)
        self.assertEqual(
            ["some_command", "goto", "service"], goto_service_tool.command_path
        )
        self.assertEqual(["code", "region", "service"], goto_service_tool.arg_names)

    def test_parse_mcp_tools_response_prop_name_for_arg(self):
        result = parse_mcp_tools_response(_sample_response_dict)
        goto_service_tool = result[0]

        self.assertEqual("code_maturity", goto_service_tool.prop_name_for_arg["code"])
        self.assertEqual("geo_region", goto_service_tool.prop_name_for_arg["region"])
        self.assertEqual("service_name", goto_service_tool.prop_name_for_arg["service"])

    ####################################################################################################################
    # build_command_line

    def test_build_command_line_no_args(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=["some_command", "goto", "service"],
            arg_names=[],
        )

        result = build_command_line(tool_desc, {})

        self.assertEqual("some_command goto service", result)

    def test_build_command_line_with_args(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=["some_command", "goto", "service"],
            arg_names=["code", "region"],
            prop_name_for_arg={"code": "code_maturity", "region": "geo_region"},
        )

        result = build_command_line(
            tool_desc,
            {"code": "prod", "region": "apac"},
        )

        self.assertIn("some_command goto service", result)
        self.assertIn("prod", result)
        self.assertIn("apac", result)

    def test_build_command_line_skips_empty_arg_values(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=["some_command", "goto", "service"],
            arg_names=["code", "region"],
            prop_name_for_arg={"code": "code_maturity", "region": "geo_region"},
        )

        result = build_command_line(
            tool_desc,
            {"code": "prod", "region": ""},
        )

        self.assertIn("prod", result)
        self.assertNotIn("  ", result)

    def test_build_command_line_skips_none_arg_values(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=["some_command", "goto", "service"],
            arg_names=["code", "region"],
            prop_name_for_arg={"code": "code_maturity", "region": "geo_region"},
        )

        result = build_command_line(
            tool_desc,
            {"code": None, "region": "apac"},
        )

        self.assertNotIn("None", result)
        self.assertIn("apac", result)

    ####################################################################################################################
    # extract_remaining

    def test_extract_remaining_empty_envelope_containers(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=[],
            arg_names=["code"],
            prop_name_for_arg={"code": "code_maturity"},
        )

        result = extract_remaining({"envelope_containers": []}, tool_desc)

        self.assertEqual({}, result)

    def test_extract_remaining_skips_container_ipos_0(self):
        """envelope_containers[0] is function container - must not be included in remaining."""
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=[],
            arg_names=["code"],
            prop_name_for_arg={"code": "code_maturity"},
        )
        invocation_input = {
            "envelope_containers": [
                {
                    "remaining_prop_name_to_prop_value": {
                        "func_id": ["func_id_goto_service"],
                    },
                },
            ],
        }

        result = extract_remaining(invocation_input, tool_desc)

        self.assertEqual({}, result)

    def test_extract_remaining_maps_prop_name_to_arg_name(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=[],
            arg_names=["code", "region"],
            prop_name_for_arg={
                "code": "code_maturity",
                "region": "geo_region",
            },
        )
        invocation_input = {
            "envelope_containers": [
                {},
                {
                    "remaining_prop_name_to_prop_value": {
                        "code_maturity": ["dev", "prod", "qa"],
                        "geo_region": ["amer", "apac", "emea"],
                    },
                },
            ],
        }

        result = extract_remaining(invocation_input, tool_desc)

        self.assertEqual(["dev", "prod", "qa"], result["code"])
        self.assertEqual(["amer", "apac", "emea"], result["region"])

    def test_extract_remaining_merges_multiple_containers(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=[],
            arg_names=["code", "host"],
            prop_name_for_arg={
                "code": "code_maturity",
                "host": "host_name",
            },
        )
        invocation_input = {
            "envelope_containers": [
                {},
                {
                    "remaining_prop_name_to_prop_value": {
                        "code_maturity": ["dev", "prod"],
                    },
                },
                {
                    "remaining_prop_name_to_prop_value": {
                        "host_name": ["host_a", "host_b"],
                    },
                },
            ],
        }

        result = extract_remaining(invocation_input, tool_desc)

        self.assertIn("code", result)
        self.assertIn("host", result)

    ####################################################################################################################
    # build_mcp_tool

    def test_build_mcp_tool_name_and_description(self):
        import mcp.types as types

        tool_desc = ToolDesc(
            name="goto_service",
            description="Go to service",
            command_path=["some_command", "goto", "service"],
            arg_names=["code"],
            prop_name_for_arg={"code": "code_maturity"},
        )

        result = build_mcp_tool(tool_desc)

        self.assertIsInstance(result, types.Tool)
        self.assertEqual("goto_service", result.name)
        self.assertEqual("Go to service", result.description)

    def test_build_mcp_tool_input_schema_properties(self):
        tool_desc = ToolDesc(
            name="goto_service",
            description="",
            command_path=[],
            arg_names=["code", "region"],
            prop_name_for_arg={
                "code": "code_maturity",
                "region": "geo_region",
            },
        )

        result = build_mcp_tool(tool_desc)

        self.assertIn("code", result.inputSchema["properties"])
        self.assertIn("region", result.inputSchema["properties"])
        self.assertEqual(
            "code_maturity", result.inputSchema["properties"]["code"]["description"]
        )

    ####################################################################################################################
    # format_tool_result

    def test_format_tool_result_is_valid_json(self):
        import json

        result_str = format_tool_result(
            {"error_code": 0},
            {"code": ["dev", "prod"]},
        )
        parsed = json.loads(result_str)

        self.assertIn("custom_plugin_data", parsed)
        self.assertIn("remaining", parsed)

    def test_format_tool_result_zero_remaining_on_success(self):
        import json

        result_str = format_tool_result(
            {"output": "done"},
            {},
        )
        parsed = json.loads(result_str)

        self.assertEqual({}, parsed["remaining"])
