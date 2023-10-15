from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec.server_data_schema import get_schema_definitions

spec_data = {
    "summary": "Provide input data to delegate execution of command on client side",
    "consumes": [
        "application/json",
    ],
    "produces": [
        "application/json",
    ],
    "parameters": [
        {
            "name": call_context_desc.ref_name,
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/" + call_context_desc.ref_name,
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Input data to delegate execution of command on client side",
            "schema": {
                "$ref": "#/definitions/" + invocation_input_desc.ref_name,
            },
            "examples": {
                "application/json": invocation_input_desc.dict_example,
            },
        },
    },
    "definitions": get_schema_definitions([
        # TODO: provide `call_context_desc` with example of expected comp_type for relay_line_args:
        call_context_desc.ref_name,
        invocation_input_desc.ref_name,
        plugin_entry_desc.ref_name,
    ]),
}
