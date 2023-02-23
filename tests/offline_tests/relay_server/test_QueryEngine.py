from unittest import TestCase, mock
from unittest.mock import patch, MagicMock

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.relay_server.QueryEngine import QueryEngine
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
                    .set_test_data_ids_to_load(["TD_63_37_05_36"])  # demo
                )
                with env_mock_builder.build():

                    fq_method_name = f"{QueryEngine.__module__}.{QueryEngine.process_results.__qualname__}"

                    # 1st run:
                    with mock.patch(fq_method_name, wraps = QueryEngine.process_results) as method_mock:

                        command_obj = __main__.main()
                        assert isinstance(command_obj, AbstractLocalClientCommand)

                        actual_suggestions_first_run = "\n".join(command_obj.response_dict[arg_values_])
                        self.assertEqual(expected_suggestions, actual_suggestions_first_run)

                        self.assertTrue(method_mock.called)

