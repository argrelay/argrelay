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
    tools = []
    for tool in response_dict.get("tools", []):
        properties = tool.get("inputSchema", {}).get("properties", {})
        arg_names = list(properties.keys())
        prop_name_for_arg = {
            arg: prop.get("description", arg) for arg, prop in properties.items()
        }
        tools.append(
            ToolDesc(
                name=tool["name"],
                description=tool.get("description", tool["name"]),
                command_path=tool.get("command_path", []),
                arg_names=arg_names,
                prop_name_for_arg=prop_name_for_arg,
            )
        )
    return tools


def build_command_line(tool: ToolDesc, args: dict) -> str:
    tokens = list(tool.command_path)
    for v in args.values():
        if v:
            tokens.append(str(v))
    return " ".join(tokens)


def extract_remaining(invocation_input: dict, tool: ToolDesc) -> dict:
    arg_for_prop = {v: k for k, v in tool.prop_name_for_arg.items()}
    result = {}
    envelope_containers = invocation_input.get("envelope_containers", [])
    for container in envelope_containers[1:]:
        for prop_name, values in container.get(
            "remaining_prop_name_to_prop_value", {}
        ).items():
            arg_name = arg_for_prop.get(prop_name, prop_name)
            result[arg_name] = values
    return result


def build_mcp_tool(tool: ToolDesc) -> types.Tool:
    properties = {
        arg_name: {"type": "string", "description": tool.prop_name_for_arg[arg_name]}
        for arg_name in tool.arg_names
    }
    return types.Tool(
        name=tool.name,
        description=tool.description,
        inputSchema={"type": "object", "properties": properties},
    )


def format_tool_result(custom_plugin_data: dict, remaining: dict) -> str:
    return json.dumps(
        {
            "custom_plugin_data": custom_plugin_data,
            "remaining": remaining,
        },
        indent=2,
    )
