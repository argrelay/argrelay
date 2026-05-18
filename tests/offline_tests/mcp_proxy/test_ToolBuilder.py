from __future__ import annotations

import json

from argrelay_app_mcp_proxy.mcp_proxy.ToolBuilder import (
    build_command_line,
    build_mcp_tool,
    extract_remaining,
    format_tool_result,
    parse_mcp_tools_response,
    ToolDesc,
)

_sample_response_dict = {
    "tools": [
        {
            "name": "goto_service",
            "description": "Go to service",
            "command_path": [
                "some_command",
                "goto",
                "service",
            ],
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
            "command_path": [
                "some_command",
                "list",
                "host",
            ],
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

########################################################################################################################
# parse_mcp_tools_response


def test_parse_mcp_tools_response_empty_dict():
    # given:

    # when:
    result = parse_mcp_tools_response({})

    # then:
    assert result == []


def test_parse_mcp_tools_response_empty_tools_list():
    # given:

    # when:
    result = parse_mcp_tools_response({"tools": []})

    # then:
    assert result == []


def test_parse_mcp_tools_response_returns_tool_desc_list():
    # given:

    # when:
    result = parse_mcp_tools_response(_sample_response_dict)

    # then:
    assert len(result) == 2
    assert isinstance(result[0], ToolDesc)
    assert isinstance(result[1], ToolDesc)


def test_parse_mcp_tools_response_populates_tool_desc_fields():
    # given:

    # when:
    result = parse_mcp_tools_response(_sample_response_dict)

    # then:
    goto_service_tool = result[0]
    assert goto_service_tool.name == "goto_service"
    assert goto_service_tool.description == "Go to service"
    assert goto_service_tool.command_path == ["some_command", "goto", "service"]
    assert goto_service_tool.arg_names == ["code", "region", "service"]


def test_parse_mcp_tools_response_prop_name_for_arg():
    # given:

    # when:
    result = parse_mcp_tools_response(_sample_response_dict)

    # then:
    goto_service_tool = result[0]
    assert goto_service_tool.prop_name_for_arg["code"] == "code_maturity"
    assert goto_service_tool.prop_name_for_arg["region"] == "geo_region"
    assert goto_service_tool.prop_name_for_arg["service"] == "service_name"


########################################################################################################################
# build_command_line


def test_build_command_line_no_args():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[
            "some_command",
            "goto",
            "service",
        ],
        arg_names=[],
    )

    # when:
    result = build_command_line(tool_desc, {})

    # then:
    assert result == "some_command goto service"


def test_build_command_line_with_args():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[
            "some_command",
            "goto",
            "service",
        ],
        arg_names=[
            "code",
            "region",
        ],
        prop_name_for_arg={
            "code": "code_maturity",
            "region": "geo_region",
        },
    )

    # when:
    result = build_command_line(
        tool_desc,
        {
            "code": "prod",
            "region": "apac",
        },
    )

    # then:
    assert "some_command goto service" in result
    assert "prod" in result
    assert "apac" in result


def test_build_command_line_skips_empty_arg_values():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[
            "some_command",
            "goto",
            "service",
        ],
        arg_names=[
            "code",
            "region",
        ],
        prop_name_for_arg={
            "code": "code_maturity",
            "region": "geo_region",
        },
    )

    # when:
    result = build_command_line(
        tool_desc,
        {
            "code": "prod",
            "region": "",
        },
    )

    # then:
    assert "prod" in result
    assert "  " not in result


def test_build_command_line_skips_none_arg_values():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[
            "some_command",
            "goto",
            "service",
        ],
        arg_names=[
            "code",
            "region",
        ],
        prop_name_for_arg={
            "code": "code_maturity",
            "region": "geo_region",
        },
    )

    # when:
    result = build_command_line(
        tool_desc,
        {
            "code": None,
            "region": "apac",
        },
    )

    # then:
    assert "None" not in result
    assert "apac" in result


########################################################################################################################
# extract_remaining


def test_extract_remaining_empty_envelope_containers():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[],
        arg_names=["code"],
        prop_name_for_arg={"code": "code_maturity"},
    )

    # when:
    result = extract_remaining(
        {"envelope_containers": []},
        tool_desc,
    )

    # then:
    assert result == {}


def test_extract_remaining_skips_container_ipos_0():
    """
    envelope_containers[0] is function container - must not be included in remaining.
    """
    # given:
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

    # when:
    result = extract_remaining(
        invocation_input,
        tool_desc,
    )

    # then:
    assert result == {}


def test_extract_remaining_maps_prop_name_to_arg_name():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[],
        arg_names=[
            "code",
            "region",
        ],
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

    # when:
    result = extract_remaining(
        invocation_input,
        tool_desc,
    )

    # then:
    assert result["code"] == ["dev", "prod", "qa"]
    assert result["region"] == ["amer", "apac", "emea"]


def test_extract_remaining_merges_multiple_containers():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[],
        arg_names=[
            "code",
            "host",
        ],
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

    # when:
    result = extract_remaining(
        invocation_input,
        tool_desc,
    )

    # then:
    assert "code" in result
    assert "host" in result


########################################################################################################################
# build_mcp_tool


def test_build_mcp_tool_name_and_description():
    import mcp.types as types

    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="Go to service",
        command_path=[
            "some_command",
            "goto",
            "service",
        ],
        arg_names=["code"],
        prop_name_for_arg={"code": "code_maturity"},
    )

    # when:
    result = build_mcp_tool(tool_desc)

    # then:
    assert isinstance(result, types.Tool)
    assert result.name == "goto_service"
    assert result.description == "Go to service"


def test_build_mcp_tool_input_schema_properties():
    # given:
    tool_desc = ToolDesc(
        name="goto_service",
        description="",
        command_path=[],
        arg_names=[
            "code",
            "region",
        ],
        prop_name_for_arg={
            "code": "code_maturity",
            "region": "geo_region",
        },
    )

    # when:
    result = build_mcp_tool(tool_desc)

    # then:
    assert "code" in result.inputSchema["properties"]
    assert "region" in result.inputSchema["properties"]
    assert result.inputSchema["properties"]["code"]["description"] == "code_maturity"


########################################################################################################################
# format_tool_result


def test_format_tool_result_is_valid_json():
    # given:

    # when:
    result_str = format_tool_result(
        {"error_code": 0},
        {"code": ["dev", "prod"]},
    )

    # then:
    parsed = json.loads(result_str)
    assert "custom_plugin_data" in parsed
    assert "remaining" in parsed


def test_format_tool_result_zero_remaining_on_success():
    # given:

    # when:
    result_str = format_tool_result(
        {"output": "done"},
        {},
    )

    # then:
    parsed = json.loads(result_str)
    assert parsed["remaining"] == {}
