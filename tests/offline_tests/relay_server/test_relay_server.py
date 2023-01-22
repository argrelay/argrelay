import dataclasses
import json
from types import SimpleNamespace
from unittest import TestCase

from argrelay.enum_desc.CompType import CompType
from argrelay.relay_server.__main__ import create_app
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.server_spec.const_int import API_SPEC
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
    RELAY_LINE_ARGS_PATH,
)
from argrelay.server_spec.server_data_schema import API_DOCS_UI_PATH, server_op_data_schemas
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):
    """
    Server-only test via Flask test client (via API without spanning `argrelay` client).
    """

    def setUp(self):

        env_mock_builder = (
            EnvMockBuilder()
            .set_mock_client_config_file_read(False)
            .set_mock_client_input(False)
            .set_client_config_with_local_server(False)
        )
        with env_mock_builder.build():
            self.assertTrue(
                open(server_config_desc.default_file_path).read() == env_mock_builder.get_server_config_yaml()
            )

            flask_app = create_app()
            self.ctx = flask_app.app_context()
            self.ctx.push()
            self.client = flask_app.test_client()

            env_mock_builder.assert_server_config_read()

    def tearDown(self):
        self.ctx.pop()

    def test_api_spec(self):
        response = self.client.get(
            API_SPEC,
            content_type = "application/json",
        )
        self.assertEqual(200, response.status_code)
        print(response.json)

        # JSON string to Python object:
        # https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object/15882054#15882054
        schema_obj = json.loads(response.text, object_hook = lambda d: SimpleNamespace(**d))

        # Ensure auto-magic schema generation provides example for Swagger UI:
        self.assertEqual(
            request_context_desc.dict_example["command_line"],
            schema_obj.definitions.RequestContextSchema.properties.command_line.example,
        )
        self.assertEqual(
            request_context_desc.dict_example["comp_type"],
            schema_obj.definitions.RequestContextSchema.properties.comp_type.example,
        )
        self.assertEqual(
            request_context_desc.dict_example["cursor_cpos"],
            schema_obj.definitions.RequestContextSchema.properties.cursor_cpos.example,
        )
        self.assertEqual(
            request_context_desc.dict_example["is_debug_enabled"],
            schema_obj.definitions.RequestContextSchema.properties.is_debug_enabled.example,
        )
        self.assertEqual(
            False,
            schema_obj.definitions.RequestContextSchema.additionalProperties,
            "Key `additionalProperties` must be `false` and automatically generated."
        )

        # Ensure whole example dict for all requests:
        schema_dict = json.loads(response.text)
        for request_path in [
            DESCRIBE_LINE_ARGS_PATH,
            PROPOSE_ARG_VALUES_PATH,
            RELAY_LINE_ARGS_PATH,
        ]:
            self.assertEqual(
                request_context_desc.dict_example,
                schema_dict["paths"][request_path]["post"]["parameters"][0]["example"],
            )

    def test_get_api_docs_ui(self):
        response = self.client.get(API_DOCS_UI_PATH)
        self.assertEqual(200, response.status_code)

    def test_describe_line_args(self):
        data_obj = dataclasses.replace(
            request_context_desc.dict_schema.load(request_context_desc.dict_example),
            comp_type = CompType.DescribeArgs,
        )
        response = self.client.post(
            DESCRIBE_LINE_ARGS_PATH,
            json = request_context_desc.dict_schema.dumps(data_obj),
        )
        self.assertEqual(200, response.status_code)

    def test_propose_arg_values(self):
        data_obj = dataclasses.replace(
            request_context_desc.dict_schema.load(request_context_desc.dict_example),
            comp_type = CompType.PrefixShown,
        )
        response = self.client.post(
            PROPOSE_ARG_VALUES_PATH,
            json = request_context_desc.dict_schema.dumps(data_obj),
        )
        self.assertEqual(200, response.status_code)

    def test_relay_line_args(self):
        data_obj = dataclasses.replace(
            request_context_desc.dict_schema.load(request_context_desc.dict_example),
            comp_type = CompType.InvokeAction,
        )
        response = self.client.post(
            RELAY_LINE_ARGS_PATH,
            json = request_context_desc.dict_schema.dumps(data_obj),
        )
        self.assertEqual(200, response.status_code)

    # noinspection PyMethodMayBeStatic
    def test_auto_schema_is_in_response(self):
        response = self.client.get(
            API_SPEC,
            content_type = "application/json",
        )
        self.assertEqual(200, response.status_code)
        definitions_dict = json.loads(response.text)["definitions"]
        schemas_dict = server_op_data_schemas.components.to_dict()["schemas"]
        print_jsons = False
        if print_jsons:
            print(f"definitions_dict: {json.dumps(definitions_dict, indent = 4)}")
            print(f"components_json: {json.dumps(schemas_dict, indent = 4)}")
        self.assertEqual(schemas_dict, definitions_dict)
