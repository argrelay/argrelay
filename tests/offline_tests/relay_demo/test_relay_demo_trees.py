from __future__ import annotations

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.relay_client import __main__
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.test_helper import line_no, parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
    EmptyEnvMockBuilder,
)
from argrelay.test_helper.LocalTestCase import LocalTestCase


class ThisTestCase(LocalTestCase):
    """
    Test several features working together:
    *   FS_01_89_09_24 interp tree
    *   FS_26_43_73_72 func tree
    *   FS_91_88_07_23 jump tree
    *   FS_42_76_93_51 first interp
    *   FS_41_40_39_44 suggest from interp tree
    """

    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_propose_auto_comp_demo(self):
        """
        TODO
        """

        # TODO: Test why `relay_demo` on query shows `some_command`?
        """
relay_demo 
ClassFunction: 20
tree_path_selector_0: some_command [InitValue]
*tree_path_selector_1: ? intercept help subtree goto desc list 
tree_path_selector_2: ? intercept help goto desc list host service repo commit 
        """

        # TODO: Add test to run both `some_command` and `relay_demo` and compare output is identical for identical requests.

        # @formatter:off
        test_cases = [

            (
                line_no(), "relay_demo |", CompType.PrefixHidden,
                [
                    "help",
                    "intercept",
                    "subtree",
                    "desc",
                    "echo",
                    "goto",
                    "list",
                    # TODO: Why there is extra `help` and `intercept` suggestions?
                    "subtree",
                    "help",
                    "intercept",
                ],
                "Basic test.",
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

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_describe_args(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "relay_demo |", CompType.DescribeArgs,
                "Ensure it provides `relay_demo` as first `InitValue` prop.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command |", CompType.DescribeArgs,
                "Ensure it provides `some_command` as first `InitValue` prop.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "relay_demo intercept |", CompType.DescribeArgs,
                "Ensure `intercept` works for `CompType.DescribeArgs`.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "relay_demo intercept help |", CompType.DescribeArgs,
                "Ensure `intercept` of `help` works for `CompType.DescribeArgs`.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "relay_demo intercept help |", CompType.DescribeArgs,
                "Ensure `help` of `intercept` works for `CompType.DescribeArgs`.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "# relay_demo intercept help |", CompType.DescribeArgs,
                "Commented line: selecting `NoopInterpFactory` by default should not fail.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "relay_demo intercept intercept help |", CompType.DescribeArgs,
                "Doubling of `intercept` should work.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "relay_demo subtree help |", CompType.DescribeArgs,
                "Help for `subtree` should work.",
                # TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    case_comment,
                    stdout_str,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                outer_env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_reset_local_server(False)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                    .set_test_data_ids_to_load([
                        self.__class__.same_test_data_per_class,
                    ])
                )
                with outer_env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    interp_ctx = command_obj.interp_ctx

                    if not stdout_str:
                        # Output is not specified - not to be asserted:
                        continue

                    # TODO: Running print again with capturing `stdout`.
                    #       Executing end-to-end above may generate
                    #       noise output on `stdout`/`stderr` by local server logic.
                    #       A proper implementation would probably be intercepting `DescribeArgs`'s response_dict
                    #       and printing it separately (when no other logic with extra output can intervene)
                    #       to assert the output.
                    #       Alternatively, run this test via `RemoteClient` (see `RemoteTestCase`) where output
                    #       of the server is not captured (as it is a separate process).
                    inner_env_mock_builder = (
                        EmptyEnvMockBuilder()
                        .set_capture_stdout(True)
                        .set_capture_stderr(True)
                    )
                    with inner_env_mock_builder.build():
                        interp_result: InterpResult = InterpResult(
                            arg_values = interp_ctx.comp_suggestions,
                            all_tokens = interp_ctx.parsed_ctx.all_tokens,
                            consumed_tokens = interp_ctx.consumed_tokens,
                            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
                            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
                            envelope_containers = interp_ctx.envelope_containers,
                        )
                        DescribeLineArgsClientResponseHandler.render_result(interp_result)

                        self.assertEqual(
                            stdout_str,
                            inner_env_mock_builder.actual_stdout.getvalue()
                        )

                        self.assertEqual(
                            "",
                            inner_env_mock_builder.actual_stderr.getvalue()
                        )
