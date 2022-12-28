import dataclasses
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch, mock_open

import pkg_resources
import yaml

from argrelay.api_ext.relay_server.ServerConfig import ServerConfig
from argrelay.api_ext.relay_server.ServerConfigSchema import server_config_desc
from argrelay.api_int.const_int import API_SPEC
from argrelay.api_int.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
    RELAY_LINE_ARGS_PATH,
)
from argrelay.api_int.data_schema.RequestContextSchema import request_context_desc
from argrelay.api_int.meta_data import CompType
from argrelay.api_int.server_op import server_op_data_schemas, API_DOCS_UI_PATH
from argrelay.relay_server.__main__ import create_app


def load_relay_demo_server_config_dict() -> dict:
    # Composing path to resource this way keeps its base directory always at this relative path:
    test_server_config_path = pkg_resources.resource_filename(__name__, "../../demo/argrelay.server.yaml")
    server_config = yaml.safe_load(open(test_server_config_path))
    # Override loaded data - do not start mongo server during testing:
    server_config["mongo_config"]["start_server"] = False
    return server_config


def load_relay_demo_server_config_object() -> ServerConfig:
    return server_config_desc.from_input_dict(load_relay_demo_server_config_dict())


class ThisTestCase(TestCase):

    def setUp(self):
        server_config_yaml = yaml.dump(load_relay_demo_server_config_dict())
        with patch("builtins.open", mock_open(read_data = server_config_yaml)) as mock_file:
            self.assertTrue(open(server_config_desc.default_file_path).read() == server_config_yaml)

            flask_app = create_app()
            self.ctx = flask_app.app_context()
            self.ctx.push()
            self.client = flask_app.test_client()

        mock_file.assert_called_with(server_config_desc.default_file_path)

    def tearDown(self):
        self.ctx.pop()

    def test_api_spec(self):
        response = self.client.get(
            API_SPEC,
            content_type = "application/json",
        )
        self.assertEqual(200, response.status_code)
        print(response.json)

        # Ensure auto-magic schema generation provides example for Swagger UI:
        schema_obj = json.loads(response.text, object_hook = lambda d: SimpleNamespace(**d))
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

        # Ensure whole example object for all requests:
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
            request_context_desc.object_schema.load(request_context_desc.dict_example),
            comp_type = CompType.DescribeArgs,
        )
        response = self.client.post(
            DESCRIBE_LINE_ARGS_PATH,
            json = request_context_desc.object_schema.dumps(data_obj),
        )
        self.assertEqual(200, response.status_code)

    def test_propose_arg_values(self):
        data_obj = dataclasses.replace(
            request_context_desc.object_schema.load(request_context_desc.dict_example),
            comp_type = CompType.PrefixShown,
        )
        response = self.client.post(
            PROPOSE_ARG_VALUES_PATH,
            json = request_context_desc.object_schema.dumps(data_obj),
        )
        self.assertEqual(200, response.status_code)

    def test_relay_line_args(self):
        data_obj = dataclasses.replace(
            request_context_desc.object_schema.load(request_context_desc.dict_example),
            comp_type = CompType.InvokeAction,
        )
        response = self.client.post(
            RELAY_LINE_ARGS_PATH,
            json = request_context_desc.object_schema.dumps(data_obj),
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
