"""
This package generates OpenAPI spec definitions for `relay_server` it publishes over HTTP.
While `relay_client` is supposed to use these definitions, it does not.
Instead, it uses `marshmallow` schemas these OpenAPI spec definitions are generated from.
"""

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc
from argrelay.server_spec.const_int import DEFAULT_OPEN_API_VERSION, UNUSED_TITLE, UNUSED_VERSION

# This spec is only used to generate data schemas: Marshmallow Schemas -> JSON Schemas.
# These data schemas are subsequently used in OAS specs for paths (which are defined manually).
# All serialization/deserialization/validation is done using `marshmallow` schemas (instead of JSON Schemas below).
server_op_data_schemas = APISpec(
    title = UNUSED_TITLE,
    version = UNUSED_VERSION,
    openapi_version = DEFAULT_OPEN_API_VERSION,
    plugins = [MarshmallowPlugin()],
)

# Generate data schemas: Marshmallow Schema -> JSON Schema:
server_op_data_schemas.components.schema(
    request_context_desc.ref_name,
    schema = request_context_desc.dict_schema,
)
server_op_data_schemas.components.schema(
    arg_values_desc.ref_name,
    schema = arg_values_desc.dict_schema,
)

# Run API docs UI at the root:
API_DOCS_UI_PATH = "/"
