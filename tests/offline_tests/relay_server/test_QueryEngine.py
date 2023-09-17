from unittest import TestCase, mock

from argrelay.client_spec.ShellContext import ShellContext, UNKNOWN_COMP_KEY
from argrelay.enum_desc.CompType import CompType
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.server_spec.CallContext import CallContext
from argrelay.test_helper import parse_line_and_cpos, line_no
from argrelay.test_helper.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestCase(TestCase):

    def test_enable_query_cache(self):
        """
        Test enabled and disabled cache has no diff and that cache actually works
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                True,
                "some_command host goto e| dev", CompType.PrefixHidden,
                "emea",
                "cache is enabled",
            ),
            (
                line_no(),
                False,
                "some_command host goto e| dev", CompType.PrefixHidden,
                "emea",
                "cache is disabled",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    enable_query_cache,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                env_mock_builder = (
                    ServerOnlyEnvMockBuilder()
                    .set_enable_query_cache(enable_query_cache)
                    .set_test_data_ids_to_load(["TD_63_37_05_36"])  # demo
                )
                with env_mock_builder.build():
                    # Start `LocalServer` with data:
                    server_config = server_config_desc.from_default_file()
                    local_server = LocalServer(server_config)
                    local_server.start_local_server()
                    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)

                    fq_method_name = f"{QueryEngine.__module__}.{QueryEngine._process_prop_values.__qualname__}"

                    # 1st run:
                    actual_suggestions_1st_run = "1st"
                    with mock.patch(fq_method_name, wraps = QueryEngine._process_prop_values) as method_mock:
                        actual_suggestions_1st_run = self.run_completion(
                            ShellContext(
                                command_line = command_line,
                                cursor_cpos = cursor_cpos,
                                comp_type = comp_type,
                                is_debug_enabled = False,
                                comp_key = UNKNOWN_COMP_KEY,
                            ).create_call_context(),
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_mock,
                            # 1st time: processing is always called:
                            True,
                        )
                    # 2nd run:
                    actual_suggestions_2nd_run = "2nd"
                    with mock.patch(fq_method_name, wraps = QueryEngine._process_prop_values) as method_mock:
                        actual_suggestions_2nd_run = self.run_completion(
                            ShellContext(
                                command_line = command_line,
                                cursor_cpos = cursor_cpos,
                                comp_type = comp_type,
                                is_debug_enabled = False,
                                comp_key = UNKNOWN_COMP_KEY,
                            ).create_call_context(),
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_mock,
                            # 2nd time: not called when cache is enabled, called when cache is disabled:
                            not enable_query_cache,
                        )
                    self.assertEqual(actual_suggestions_1st_run, actual_suggestions_2nd_run)

    def run_completion(
        self,
        call_ctx: CallContext,
        propose_arg_values_handler,
        expected_suggestions,
        method_mock,
        is_called,
    ):
        response_dict = propose_arg_values_handler.handle_request(call_ctx)
        actual_suggestions = "\n".join(response_dict[arg_values_])
        self.assertEqual(expected_suggestions, actual_suggestions)
        self.assertEqual(method_mock.called, is_called)
        return actual_suggestions
