import dataclasses
import json
from types import SimpleNamespace
from typing import Callable, Any

from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_delegator_stub_custom_data_example
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.schema_response.InterpResultSchema import interp_result_desc, all_tokens_
from argrelay.schema_response.InvocationInputSchema import custom_plugin_data_
from argrelay.server_spec.const_int import API_SPEC_PATH, API_DOCS_PATH
from argrelay.server_spec.server_data_schema import server_op_data_schemas
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import ServerOnlyEnvMockBuilder
from argrelay.test_helper.ServerOnlyTestCase import ServerOnlyTestCase


class ThisTestCase(ServerOnlyTestCase):
    """
    Server-only test via Flask test client (via API without using `argrelay` client code).
    """

    def setUp(self):
        super().setUp()

        self.create_server_in_mocked_env(
            ServerOnlyEnvMockBuilder()
            .set_test_data_ids_to_load([
                "TD_63_37_05_36",  # demo
            ])
        )
        self.test_client = self.flask_app.test_client()

    def tearDown(self):
        super().tearDown()

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

        # Ensure auto-magic schema generation provides example for Swagger GUI:
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

    ####################################################################################################################
    # Special cases

    def test_get_api_docs_ui(self):
        response = self.test_client.get(API_DOCS_PATH)
        self.assertEqual(200, response.status_code)

    def test_no_headers_case_for_all(self):
        for server_request in ServerAction:
            server_response = self.make_post_request(
                server_action = server_request,
                api_path = server_request.value,
                api_headers = {
                    # "Content-Type": None,
                    # "Accept": None,
                },
            )
            self.assertEqual(200, server_response.status_code)

    def test_propose_arg_values_via_send_none_recv_none(self):
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                # "Content-Type": None,
                # "Accept": None,
            },
        )
        self.assertEqual(200, server_response.status_code)
        self.assertEqual(
            "dev\nqa\nprod",
            server_response.get_data(as_text = True),
        )

    def test_propose_arg_values_via_send_json_recv_none(self):
        """
        Default response is "text/plain" - required for `ProposeArgValuesRemoteOptimizedClientCommand`.
        """
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                "Content-Type": "application/json",
                # "Accept": None,
            },
        )
        self.assertEqual(200, server_response.status_code)
        self.assertEqual(
            "dev\nqa\nprod",
            server_response.get_data(as_text = True),
        )

    def test_propose_arg_values_via_send_json_recv_text(self):
        """
        Support "text/plain" response - required for `ProposeArgValuesRemoteOptimizedClientCommand`.
        """
        server_response = self.make_post_request(
            server_action = ServerAction.ProposeArgValues,
            api_path = ServerAction.ProposeArgValues.value,
            api_headers = {
                "Content-Type": "application/json",
                "Accept": "text/plain",
            },
        )
        self.assertEqual(200, server_response.status_code)
        self.assertEqual(
            "dev\nqa\nprod",
            server_response.get_data(as_text = True),
        )

    ####################################################################################################################
    # General cases

    def test_server_responses(self):

        http_status_to_headers = {

            # HTTP 415 Unsupported Media Type
            # The server refuses to accept the request because the payload format is in an unsupported format:
            415: [
                {
                    "Content-Type": "application/xml",
                    # "Accept": None,
                },
                {
                    "Content-Type": "application/xml",
                    "Accept": "application/json",
                },
            ],

            # HTTP 406 Not Acceptable
            # The server cannot produce a response matching the list of acceptable types by client:
            406: [
                {
                    "Content-Type": "application/json",
                    "Accept": "text/plain",
                },
                {
                    "Content-Type": "application/json",
                    "Accept": "application/xml",
                },
            ],

            # HTTP 200 OK
            200: [
                {
                    # "Content-Type": None,
                    # "Accept": None,
                },
                {
                    # "Content-Type": None,
                    "Accept": "application/json",
                },
                {
                    "Content-Type": "application/json",
                    # "Accept": None,
                },
                {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            ],
        }

        extra_data_verifiers = {
            200: {
                ServerAction.DescribeLineArgs: [
                    lambda response_data:
                    self.assertEqual(
                        [
                            "some_command",
                            "goto",
                            "service",
                        ],
                        response_data[all_tokens_],
                    ),
                ],
                ServerAction.ProposeArgValues: [
                    lambda response_data:
                    self.assertEqual(
                        [
                            "dev",
                            "qa",
                            "prod",
                        ],
                        response_data[arg_values_],
                    ),
                ],
                ServerAction.RelayLineArgs: [
                    lambda response_data:
                    self.assertEqual(
                        error_delegator_stub_custom_data_example,
                        response_data[custom_plugin_data_],
                    )
                ]
            },
        }

        def get_extra_data_verifiers(
            status_code,
            server_action,
        ):
            if status_code in extra_data_verifiers:
                if server_action in extra_data_verifiers[status_code]:
                    return extra_data_verifiers[status_code][server_action]
            return []

        test_cases = []

        for server_action in ServerAction:
            for status_code, api_headers_list in http_status_to_headers.items():
                for api_headers in api_headers_list:

                    # Special cases:

                    if server_action is ServerAction.ProposeArgValues:
                        func_ref = None
                        if api_headers.get("Accept") is None and api_headers.get("Content-Type") is None:
                            func_ref = self.test_propose_arg_values_via_send_none_recv_none
                        if api_headers.get("Accept") is None and api_headers.get("Content-Type") == "application/json":
                            func_ref = self.test_propose_arg_values_via_send_json_recv_none
                        if api_headers.get("Accept") == "text/plain":
                            func_ref = self.test_propose_arg_values_via_send_json_recv_text
                        if func_ref:
                            test_cases.append((
                                line_no(),
                                f"Special case: {func_ref}",
                                api_headers,
                                server_action,
                                200,
                                # No extra data verifications - it is done in special case functions instead:
                                [],
                            ))
                            continue

                    # General cases:

                    test_cases.append((
                        line_no(),
                        f"General case",
                        api_headers,
                        server_action,
                        status_code,
                        get_extra_data_verifiers(status_code, server_action)
                    ))

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    case_comment,
                    api_headers,
                    server_action,
                    expected_status_code,
                    data_verifiers,
                ) = test_case

                self.make_post_request_and_verify(
                    server_action,
                    api_headers,
                    expected_status_code,
                    *data_verifiers,
                )

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
            data = call_context_desc.dict_schema.dumps(data_obj),
            headers = api_headers,
        )
        return server_response

    def make_post_request_and_verify(
        self,
        server_action,
        api_headers,
        expected_status_code,
        *data_verifiers: Callable[[Any], None],
    ):
        server_response = self.make_post_request(
            server_action,
            server_action.value,
            api_headers,
        )
        self.assertEqual(expected_status_code, server_response.status_code)
        if data_verifiers:
            response_data = json.loads(server_response.get_data(as_text = True))
            interp_result_desc.dict_schema.validate(response_data)
            for data_verifier in data_verifiers:
                data_verifier(response_data)
