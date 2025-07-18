from argrelay_api_server_cli.schema_request.CallContextSchema import call_context_desc
from argrelay_api_server_cli.schema_response.ArgValuesSchema import (
    arg_values_,
    arg_values_desc,
)
from argrelay_api_server_cli.server_spec.server_data_schema import (
    get_schema_definitions,
)

spec_data = {
    "summary": "Propose `arg_value`-s for the given command line and cursor position",
    "consumes": [
        "application/json",
    ],
    "produces": [
        "application/json",
        "text/plain",
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
            "description": "List of proposed `arg_value`-s",
            "schema": {
                "$ref": "#/definitions/" + arg_values_desc.ref_name,
            },
            "examples": {
                "application/json": arg_values_desc.dict_example,
                "text/plain": "\n".join(arg_values_desc.dict_example[arg_values_]),
            },
        },
    },
    "definitions": get_schema_definitions(
        [
            # TODO: provide `call_context_desc` with example of expected comp_type for propose_arg_values:
            call_context_desc.ref_name,
            arg_values_desc.ref_name,
        ]
    ),
}
