from unittest import TestCase, mock
from unittest.mock import patch, MagicMock

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.relay_client import __main__
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_context.RequestContext import RequestContext
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.test_helper import parse_line_and_cpos, line_no
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):

    def test_when_cache_is_enabled(self):
        """
        Test enabled and disabled cache has no diff and that cache actually works
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                "some_command host goto e| dev", CompType.PrefixHidden,
                "emea",
                "just one sample",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                env_mock_builder = (
                    EnvMockBuilder()
                    .set_run_mode(RunMode.CompletionMode)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                    .set_enable_query_cache(True)
                    # Server-only mock:
                    .set_mock_client_config_file_read(False)
                    .set_mock_client_input(False)
                    .set_client_config_with_local_server(False)
                    .set_test_data_ids_to_load(["TD_63_37_05_36"])  # demo
                )
                with env_mock_builder.build():

                    # Start `LocalServer` with data:
                    server_config = server_config_desc.from_default_file()
                    local_server = LocalServer(server_config)
                    local_server.start_local_server()
                    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)

                    request_ctx = RequestContext(
                        command_line = command_line,
                        cursor_cpos = cursor_cpos,
                        comp_type = comp_type,
                        is_debug_enabled = False,
                    )

                    fq_method_name = f"{QueryEngine.__module__}.{QueryEngine.process_results.__qualname__}"

                    # 1st run:
                    actual_suggestions_1st_run = "1st"
                    with mock.patch(fq_method_name, wraps = QueryEngine.process_results) as method_mock:
                        actual_suggestions_1st_run = self.run_completion(
                            request_ctx,
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_mock,
                            True,
                        )
                    # 2nd run:
                    actual_suggestions_2nd_run = "2nd"
                    with mock.patch(fq_method_name, wraps = QueryEngine.process_results) as method_mock:
                        actual_suggestions_2nd_run = self.run_completion(
                            request_ctx,
                            propose_arg_values_handler,
                            expected_suggestions,
                            method_mock,
                            False,
                        )

                    self.assertEqual(actual_suggestions_1st_run, actual_suggestions_2nd_run)

    def run_completion(self, request_ctx, propose_arg_values_handler, expected_suggestions, method_mock, is_called):
        input_ctx = AbstractServerRequestHandler.create_input_ctx(request_ctx, RunMode.CompletionMode)
        response_dict = propose_arg_values_handler.handle_request(input_ctx)
        actual_suggestions = "\n".join(response_dict[arg_values_])
        self.assertEqual(expected_suggestions, actual_suggestions)
        self.assertEqual(method_mock.called, is_called)
        return actual_suggestions
