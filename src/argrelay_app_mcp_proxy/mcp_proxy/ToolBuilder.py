from __future__ import annotations

import json
from dataclasses import dataclass, field

import mcp.types as types


@dataclass
class ToolDesc:
    name: str
    description: str
    command_path: list[str]
    arg_names: list[str]
    prop_name_for_arg: dict[str, str] = field(default_factory=dict)


def parse_mcp_tools_response(response_dict: dict) -> list[ToolDesc]:
    tool_list = []
    for tool_data in response_dict.get("tools", []):
        arg_properties = tool_data.get("inputSchema", {}).get("properties", {})
        arg_names = list(arg_properties.keys())
        prop_name_for_arg = {
            arg_name: arg_prop.get("description", arg_name)
            for arg_name, arg_prop in arg_properties.items()
        }
        tool_list.append(
            ToolDesc(
                name=tool_data["name"],
                description=tool_data.get("description", tool_data["name"]),
                command_path=tool_data.get("command_path", []),
                arg_names=arg_names,
                prop_name_for_arg=prop_name_for_arg,
            )
        )
    return tool_list


def build_command_line(
    tool_desc: ToolDesc,
    call_args: dict,
) -> str:
    token_list = list(tool_desc.command_path)
    for arg_value in call_args.values():
        if arg_value:
            token_list.append(str(arg_value))
    return " ".join(token_list)


def extract_remaining(
    invocation_input: dict,
    tool_desc: ToolDesc,
) -> dict:
    arg_for_prop = {
        prop_name: arg_name
        for arg_name, prop_name in tool_desc.prop_name_for_arg.items()
    }
    remaining_args = {}
    envelope_containers = invocation_input.get("envelope_containers", [])
    for envelope_container in envelope_containers[1:]:
        for prop_name, prop_values in envelope_container.get(
            "remaining_prop_name_to_prop_value", {}
        ).items():
            arg_name = arg_for_prop.get(prop_name, prop_name)
            remaining_args[arg_name] = prop_values
    return remaining_args


def build_mcp_tool(tool_desc: ToolDesc) -> types.Tool:
    tool_properties = {
        arg_name: {
            "type": "string",
            "description": tool_desc.prop_name_for_arg[arg_name],
        }
        for arg_name in tool_desc.arg_names
    }
    return types.Tool(
        name=tool_desc.name,
        description=tool_desc.description,
        input_schema={
            "type": "object",
            "properties": tool_properties,
        },
    )


def format_tool_result(
    custom_plugin_data: dict,
    remaining_args: dict,
) -> str:
    return json.dumps(
        {
            "custom_plugin_data": custom_plugin_data,
            "remaining": remaining_args,
        },
        indent=2,
    )
