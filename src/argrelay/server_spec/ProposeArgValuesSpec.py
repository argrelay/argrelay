from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc, arg_values_
from argrelay.server_spec.server_data_schema import server_op_data_schemas, get_schema_definitions

spec_data = {
    "summary": "Propose arg values for the given command line and cursor position",
    "consumes": [
        "application/json",
    ],
    "produces": [
        "application/json",
        "text/plain",
    ],
    "parameters": [
        {
            "name": request_context_desc.ref_name,
            "in": "body",
            "required": True,
            "schema": {
                "$ref": "#/definitions/" + request_context_desc.ref_name,
            },
        },
    ],
    "responses": {
        "200": {
            "description": "List of proposed arg values",
            "schema": {
                "$ref": "#/definitions/" + arg_values_desc.ref_name,
            },
            "examples": {
                "application/json": arg_values_desc.dict_example,
                "text/plain": "\n".join(arg_values_desc.dict_example[arg_values_]),
            },
        },
    },
    "definitions": get_schema_definitions([
        request_context_desc.ref_name,
        arg_values_desc.ref_name,
    ]),
}
