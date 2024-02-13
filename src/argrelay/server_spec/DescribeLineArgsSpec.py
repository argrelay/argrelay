from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.AssignedValueSchema import assigned_value_desc
from argrelay.schema_response.EnvelopeContainerSchema import envelope_container_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.server_spec.server_data_schema import get_schema_definitions

spec_data = {
    "summary": "Describe search results from arg values of the given command line and cursor position",
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
            "description": "Described search results",
            "schema": {
                "$ref": "#/definitions/" + interp_result_desc.ref_name,
            },
            "examples": {
                "application/json": interp_result_desc.dict_example,
            },
        },
    },
    "definitions": get_schema_definitions([
        # TODO: provide `call_context_desc` with example of expected `comp_type` for `describe_line_args`:
        call_context_desc.ref_name,
        interp_result_desc.ref_name,
        envelope_container_desc.ref_name,
        data_envelope_desc.ref_name,
        assigned_value_desc.ref_name,
        search_control_desc.ref_name,
    ]),
}
