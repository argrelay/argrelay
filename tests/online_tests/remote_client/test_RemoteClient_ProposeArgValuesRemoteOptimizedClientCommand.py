from __future__ import annotations

from argrelay_app_client.client_command_remote.ClientCommandRemoteWorkerJson import ClientCommandRemoteWorkerJson
from argrelay_app_client.client_command_remote.ClientCommandRemoteWorkerTextProposeArgValuesOptimized import (
    ClientCommandRemoteWorkerTextProposeArgValuesOptimized,
)
from argrelay_app_client.relay_client import __main__
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_test_infra.test_infra import (
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    LiveServerEnvMockBuilder,
    wrap_instance_method_on_class,
)
from argrelay_test_infra.test_infra.RemoteTestClass import RemoteTestClass


class ThisTestClass(RemoteTestClass):

    def test_ClientCommandRemoteWorkerTextProposeArgValuesOptimized_is_functionally_equivalent_to_non_optimized(self):
        """
        Makes sure these two classes work the same way:
        *   ClientCommandRemoteWorkerTextProposeArgValuesOptimized
        *   ClientCommandRemoteWorkerJson
        """

        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command upstream goto host |", CompType.PrefixHidden,
                """dev
prod
qa
""",
                "Sample 1",
            ),
            (
                line_no(), "some_command host goto upstream a|", CompType.SubsequentHelp,
                """amer
apac
""",
                "Sample 2",
            ),
        ]
        # @formatter:on

        for optimize_completion_request in [
            True,
            False,
        ]:
            for test_case in test_cases:
                with self.subTest((test_case, optimize_completion_request)):
                    (
                        line_number,
                        test_line,
                        comp_type,
                        expected_stdout_str,
                        case_comment,
                    ) = test_case

                    (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                    env_mock_builder = (
                        LiveServerEnvMockBuilder()
                        .set_command_line(command_line)
                        .set_cursor_cpos(cursor_cpos)
                        .set_comp_type(comp_type)
                        .set_client_config_dict()
                        .set_show_pending_spinner(False)
                        .set_mock_client_config_file_read(True)
                        .set_client_config_to_optimize_completion_request(optimize_completion_request)
                        .set_capture_stdout(True)
                        .set_capture_stderr(True)
                    )
                    with env_mock_builder.build():
                        with wrap_instance_method_on_class(
                            ClientCommandRemoteWorkerTextProposeArgValuesOptimized,
                            ClientCommandRemoteWorkerTextProposeArgValuesOptimized.execute_command,
                        ) as optimized_method_wrap_mock:
                            with wrap_instance_method_on_class(
                                ClientCommandRemoteWorkerJson,
                                ClientCommandRemoteWorkerJson.execute_command,
                            ) as non_optimized_method_wrap_mock:

                                # when:

                                __main__.main()

                                # then:

                                if optimize_completion_request:
                                    assert optimized_method_wrap_mock.called
                                    assert not non_optimized_method_wrap_mock.called
                                else:
                                    assert not optimized_method_wrap_mock.called
                                    assert non_optimized_method_wrap_mock.called

                                self.assertEqual(
                                    expected_stdout_str,
                                    env_mock_builder.actual_stdout.getvalue(),
                                )
                                self.assertEqual(
                                    "",
                                    env_mock_builder.actual_stderr.getvalue(),
                                )
