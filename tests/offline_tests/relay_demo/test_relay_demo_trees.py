from __future__ import annotations

from argrelay_api_server_cli.schema_response.InterpResult import InterpResult
from argrelay_app_client.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay_app_client.handler_response.ClientResponseHandlerDescribeLineArgs import (
    ClientResponseHandlerDescribeLineArgs,
)
from argrelay_app_client.relay_client import __main__
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_test_infra.test_infra import (
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EmptyEnvMockBuilder,
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
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

        # TODO: Test why `lay` on query shows `some_command`?
        """
lay 
class_function: 20
tree_step_0: some_command [init_value]
*tree_step_1: ? intercept help subtree goto desc list 
tree_step_2: ? intercept help goto desc list host service repo commit 
        """

        # TODO: Add test to run both `lay` and `some_command` and compare output is identical for identical requests.

        test_cases = [
            (
                line_no(), "some_command |", CompType.PrefixHidden,
                [
                    "config",
                    "data",
                    "desc",
                    "diff",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "no_data",
                    "ssh",
                ],
                "Basic test.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_describe_args(self):
        test_cases = [
            (
                line_no(), "some_command |", CompType.DescribeArgs,
                "Ensure it provides `some_command` as first `init_value` prop.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command |", CompType.DescribeArgs,
                "Ensure it provides `some_command` as first `init_value` prop.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command intercept |", CompType.DescribeArgs,
                "Ensure `intercept` works for `CompType.DescribeArgs`.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command intercept help |", CompType.DescribeArgs,
                "Ensure `intercept` of `help` works for `CompType.DescribeArgs`.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command intercept help |", CompType.DescribeArgs,
                "Ensure `help` of `intercept` works for `CompType.DescribeArgs`.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "# some_command intercept help |", CompType.DescribeArgs,
                "Commented line: selecting `NoopInterpFactory` by default should not fail.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command intercept intercept help |", CompType.DescribeArgs,
                "Doubling of `intercept` should work.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
            (
                line_no(), "some_command subtree help |", CompType.DescribeArgs,
                "Help for `subtree` should work.",
                # TODO: TODO_42_81_01_90: implement asserting data for `CompType.DescribeArgs` to make it easier to assert:
                None,
            ),
        ]

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
                    assert isinstance(command_obj, ClientCommandLocal)
                    interp_ctx = command_obj.interp_ctx

                    if not stdout_str:
                        # Output is not specified - not to be asserted:
                        continue

                    # TODO: TODO_43_41_95_86: use server logger to disable stdout:
                    #       Running print again with capturing `stdout`.
                    #       Executing end-to-end above may generate
                    #       noise output on `stdout`/`stderr` by local server logic.
                    #       A proper implementation would probably be intercepting `DescribeArgs`'s response_dict
                    #       and printing it separately (when no other logic with extra output can intervene)
                    #       to assert the output.
                    #       Alternatively, run this test via `ClientRemote` (see `RemoteTestClass`) where output
                    #       of the server is not captured (as it is a separate process).
                    inner_env_mock_builder = (
                        EmptyEnvMockBuilder()
                        .set_capture_stdout(True)
                        .set_capture_stderr(True)
                    )
                    with inner_env_mock_builder.build():
                        interp_result: InterpResult = InterpResult.from_interp_context(interp_ctx)
                        ClientResponseHandlerDescribeLineArgs.render_result(interp_result)

                        self.assertEqual(
                            stdout_str,
                            inner_env_mock_builder.actual_stdout.getvalue()
                        )

                        self.assertEqual(
                            "",
                            inner_env_mock_builder.actual_stderr.getvalue()
                        )
