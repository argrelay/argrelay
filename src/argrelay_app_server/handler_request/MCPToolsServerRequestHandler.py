from __future__ import annotations

from argrelay_api_server_cli.server_spec.const_int import MCP_TOOLS_PATH
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    tree_step_prop_name_prefix_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    func_id_,
    search_control_list_,
)


_func_id_prefix = "func_id_"
_no_prop_value = SpecialChar.NoPropValue.value


class MCPToolsServerRequestHandler:

    def __init__(
        self,
        local_server: LocalServer,
    ):
        self.local_server = local_server

    def handle_request(self) -> dict:
        mongo_db = self.local_server.get_mongo_database()
        collection = mongo_db[ReservedEnvelopeClass.class_function.name]

        tools = []
        for envelope in collection.find(
            {
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name
            }
        ):
            tool = _build_tool_descriptor(envelope)
            if tool is not None:
                tools.append(tool)

        return {"tools": tools}


def _build_tool_descriptor(envelope: dict) -> dict | None:
    instance_data = envelope.get("instance_data", {})

    raw_func_id = instance_data.get(func_id_, "")
    if not raw_func_id:
        return None
    tool_name = (
        raw_func_id[len(_func_id_prefix) :]
        if raw_func_id.startswith(_func_id_prefix)
        else raw_func_id
    )

    description = envelope.get("help_hint", raw_func_id)

    step_keys = sorted(k for k in envelope if k.startswith(tree_step_prop_name_prefix_))
    command_path = [envelope[k] for k in step_keys if envelope[k] != _no_prop_value]

    properties = {}
    for sc in instance_data.get(search_control_list_, []):
        for mapping in sc.get("arg_name_to_prop_name_map", []):
            for arg_name, prop_name in mapping.items():
                if arg_name == "class":
                    continue
                properties[arg_name] = {"type": "string", "description": prop_name}

    return {
        "name": tool_name,
        "description": description,
        "command_path": command_path,
        "inputSchema": {
            "type": "object",
            "properties": properties,
        },
    }
