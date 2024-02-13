"""
This package generates OpenAPI spec definitions for `relay_server` which publishes them over HTTP.
While `relay_client` is supposed to use these definitions, it does not.
Instead, it uses `marshmallow` schemas these OpenAPI spec definitions are generated from.
"""

from __future__ import annotations

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec.const_int import (
    DEFAULT_OPEN_API_VERSION,
    UNUSED_TITLE,
    UNUSED_VERSION,
)

# This spec is only used to generate data schemas: Marshmallow Schemas -> JSON Schemas.
# These data schemas are subsequently used in OAS specs for paths (which are defined manually).
# All serialization/deserialization/validation is done using `marshmallow` schemas (instead of JSON Schemas below).
server_op_data_schemas = APISpec(
    title = UNUSED_TITLE,
    version = UNUSED_VERSION,
    openapi_version = DEFAULT_OPEN_API_VERSION,
    plugins = [
        MarshmallowPlugin(
            # Override default resolver to preserve `Schema` postfix (keep full schema class name):
            schema_name_resolver = lambda schema_obj: schema_obj.__class__.__name__
        )
    ],
)


def add_type_desc_to_schema(type_desc: TypeDesc):
    """
    Generate data schemas: Marshmallow Schema (type_desc) -> JSON Schema
    """
    server_op_data_schemas.components.schema(
        type_desc.ref_name,
        schema = type_desc.dict_schema,
    )


def get_schema_definitions(ref_names: list[str]):
    """
    In order for `flasgger` to generate GUI, it needs full list schema definitions
    (including those added recursively for nested schemas) for Open API specs
    referenced via `@swag_from` annotations.
    At the moment, this list of schema names is composed manually
    (by checking errors on GUI or by running `test_auto_schema_is_in_response`).
    Actual schemas are generated via `marshmallow` + `apispec` inside:
    `server_op_data_schemas.components.schemas`
    This function (although providing minimum functionality) is the single point
    where this cumbersome mechanism is documented.
    """

    schema_definitions = {}
    for ref_name in ref_names:
        schema_definitions[ref_name] = server_op_data_schemas.components.schemas[ref_name]
    return schema_definitions


# Request: common for several API paths:
# *   ServerAction.DescribeLineArgs
# *   ServerAction.ProposeArgValues
# *   ServerAction.RelayLineArgs
add_type_desc_to_schema(call_context_desc)

# Response for:
# *   ServerAction.DescribeLineArgs:
add_type_desc_to_schema(interp_result_desc)

# Response for:
# *   ServerAction.ProposeArgValues:
add_type_desc_to_schema(arg_values_desc)

# Response for:
# *   ServerAction.RelayLineArgs:
add_type_desc_to_schema(invocation_input_desc)
