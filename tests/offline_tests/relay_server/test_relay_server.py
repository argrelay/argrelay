import dataclasses
import json
from types import SimpleNamespace
from unittest import TestCase

from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_delegator_stub_custom_data_example
from argrelay.relay_server.__main__ import create_app
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_, arg_values_desc
from argrelay.schema_response.InterpResultSchema import all_tokens_, interp_result_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc, custom_plugin_data_
from argrelay.server_spec.const_int import API_SPEC_PATH, API_DOCS_PATH
from argrelay.server_spec.server_data_schema import server_op_data_schemas
from argrelay.test_helper.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestCase(TestCase):
    """
    Server-only test via Flask test client (via API without spanning `argrelay` client).
    """

    def setUp(self):

        env_mock_builder = (
            ServerOnlyEnvMockBuilder()
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
        )
        with env_mock_builder.build():
            self.assertTrue(
                open(server_config_desc.default_file_path).read() == env_mock_builder.get_server_config_yaml()
            )

            flask_app = create_app()
            self.ctx = flask_app.app_context()
            self.ctx.push()
            self.test_client = flask_app.test_client()

            env_mock_builder.assert_server_config_read()

    def tearDown(self):
        self.ctx.pop()

    def test_api_spec(self):
        response = self.test_client.get(
            API_SPEC_PATH,
            content_type = "application/json",
        )
        self.assertEqual(200, response.status_code)
        print(response.json)

        # JSON string to Python object:
        # https://stackoverflow.com/a/15882054/441652
        schema_obj = json.loads(response.text, object_hook = lambda d: SimpleNamespace(**d))

        # Ensure auto-magic schema generation provides example for Swagger UI:
        self.assertEqual(
            call_context_desc.dict_example["command_line"],
            schema_obj.definitions.CallContextSchema.properties.command_line.example,
        )
        self.assertEqual(
            call_context_desc.dict_example["comp_scope"],
            schema_obj.definitions.CallContextSchema.properties.comp_scope.example,
        )
        self.assertEqual(
            call_context_desc.dict_example["cursor_cpos"],
            schema_obj.definitions.CallContextSchema.properties.cursor_cpos.example,
        )
        self.assertEqual(
            call_context_desc.dict_example["is_debug_enabled"],
            schema_obj.definitions.CallContextSchema.properties.is_debug_enabled.example,
        )
        self.assertEqual(
            False,
            schema_obj.definitions.CallContextSchema.additionalProperties,
            "Key `additionalProperties` must be `false` and automatically generated.",
        )

        # Ensure whole example dict for all requests:
        schema_dict = json.loads(response.text)
        for request_path in [e.value for e in ServerAction]:
            self.assertTrue(
                "examples" in schema_dict["paths"][request_path]["post"]["responses"]["200"],
            )

    def test_get_api_docs_ui(self):
        response = self.test_client.get(API_DOCS_PATH)
        self.assertEqual(200, response.status_code)

    ####################################################################################################################
    # describe_line_args

    def test_describe_line_args_via_default_mime_type(self):
        server_response = self.make_post_request(
            server_action = ServerAction.DescribeLineArgs,
            api_path = ServerAction.DescribeLineArgs.value,
            api_headers = {
            },
        )
        self.assertEqual(200, server_response.status_code)
        response_data = json.loads(server_response.get_data(as_text = True))
        interp_result_desc.dict_schema.validate(response_data)
        # Check some data:
        self.assertEqual(
            [
                "some_command",
                "goto",
                "service",
            ],
            response_data[all_tokens_],
        )

    def test_describe_line_args_via_json(self):
        server_response = self.make_post_request(
            server_action = ServerAction.DescribeLineArgs,
            api_path = ServerAction.DescribeLineArgs.value,
            api_headers = {
                "Accept": "application/json",
            },
        )
        self.assertEqual(200, server_response.status_code)
        response_data = json.loads(server_response.get_data(as_text = True))
        interp_result_desc.dict_schema.validate(response_data)
        # Check some data:
        self.assertEqual(
            [
                "some_command",
                "goto",
                "service",
            ],
            response_data[all_tokens_],
        )

    def test_describe_line_args_via_text(self):
        server_response = self.make_post_request(
            server_action = ServerAction.DescribeLineArgs,
            api_path = ServerAction.DescribeLineArgs.value,
            api_headers = {
                "Accept": "text/plain",
            },
        )
        self.assertEqual(406, server_response.status_code)

    ####################################################################################################################
    # propose_arg_values

    def test_propose_arg_values_via_default_mime_type(self):
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
            },
        )
        self.assertEqual(200, server_response.status_code)
        # Check some data:
        self.assertEqual(
            "dev\nqa\nprod",
            server_response.get_data(as_text = True),
        )

    def test_propose_arg_values_via_text(self):
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                "Accept": "text/plain",
            },
        )
        self.assertEqual(200, server_response.status_code)
        # Check some data:
        self.assertEqual(
            "dev\nqa\nprod",
            server_response.get_data(as_text = True),
        )

    def test_propose_arg_values_via_json(self):
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                "Accept": "application/json",
            },
        )
        self.assertEqual(200, server_response.status_code)
        response_data = json.loads(server_response.get_data(as_text = True))
        arg_values_desc.dict_schema.validate(response_data)
        # Check some data:
        self.assertEqual(
            [
                "dev",
                "qa",
                "prod",
            ],
            response_data[arg_values_],
        )

    def test_propose_arg_values_via_wrong_mime_type(self):
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                "Accept": "application/xml",
            },
        )
        self.assertEqual(406, server_response.status_code)

    ####################################################################################################################
    # relay_line_args

    def test_relay_line_args_via_default_mime_type(self):
        server_response = self.make_post_request(
            server_action = ServerAction.RelayLineArgs,
            api_path = ServerAction.RelayLineArgs.value,
            api_headers = {
            },
        )
        self.assertEqual(200, server_response.status_code)
        response_data = json.loads(server_response.get_data(as_text = True))
        invocation_input_desc.dict_schema.validate(response_data)
        self.assertEqual(
            error_delegator_stub_custom_data_example,
            response_data[custom_plugin_data_],
        )

    def test_relay_line_args_via_default_via_json(self):
        server_response = self.make_post_request(
            server_action = ServerAction.RelayLineArgs,
            api_path = ServerAction.RelayLineArgs.value,
            api_headers = {
                "Accept": "application/json",
            },
        )
        self.assertEqual(200, server_response.status_code)
        response_data = json.loads(server_response.get_data(as_text = True))
        invocation_input_desc.dict_schema.validate(response_data)
        self.assertEqual(
            error_delegator_stub_custom_data_example,
            response_data[custom_plugin_data_],
        )

    def test_relay_line_args_via_default_via_text(self):
        server_response = self.make_post_request(
            server_action = ServerAction.RelayLineArgs,
            api_path = ServerAction.RelayLineArgs.value,
            api_headers = {
                "Accept": "text/plain",
            },
        )
        self.assertEqual(406, server_response.status_code)

    ####################################################################################################################

    # noinspection PyMethodMayBeStatic
    def test_auto_schema_is_in_response(self):
        """
        Verifies equivalent of two spec contents:
        *   generated by `apispec` (given to `flasgger` on server start)
        *   generated by `flasgger` (returned in server response)
        """
        response = self.test_client.get(
            API_SPEC_PATH,
            content_type = "application/json",
        )
        self.assertEqual(200, response.status_code)
        response_dict = json.loads(response.text)["definitions"]
        schema_dict = server_op_data_schemas.components.to_dict()["definitions"]
        print_jsons = False
        if print_jsons:
            print(f"response_dict: {json.dumps(response_dict, indent = 4)}")
            print(f"schema_dict: {json.dumps(schema_dict, indent = 4)}")
        self.maxDiff = None
        self.assertEqual(schema_dict, response_dict)

    ####################################################################################################################

    def make_post_request(
        self,
        server_action,
        api_path,
        api_headers,
    ):
        """
        Utility method to make similar requests
        """
        data_obj = dataclasses.replace(
            call_context_desc.dict_schema.load(call_context_desc.dict_example),
            server_action = server_action,
        )
        server_response = self.test_client.post(
            api_path,
            json = call_context_desc.dict_schema.dumps(data_obj),
            headers = api_headers,
        )
        return server_response
