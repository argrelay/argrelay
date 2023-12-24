from __future__ import annotations

import dataclasses

from argrelay.enum_desc.CompType import CompType
from argrelay.relay_client import __main__
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.test_infra import line_no, parse_line_and_cpos, change_to_known_repo_path
from argrelay.test_infra.EnvMockBuilder import (
    LiveServerEnvMockBuilder,
)
from argrelay.test_infra.RemoteTestClass import RemoteTestClass


class ThisTestClass(RemoteTestClass):

    def test_ProposeArgValuesRemoteOptimizedClientCommand_is_functionally_equivalent_to_non_optimized(self):
        """
        Makes sure these two classes work the same way:
        *   ProposeArgValuesRemoteOptimizedClientCommand
        *   ProposeArgValuesRemoteClientCommand
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

                    with change_to_known_repo_path("."):
                        client_config_obj: ClientConfig = dataclasses.replace(
                            # Use real config from client with connection details for live server:
                            client_config_desc.from_default_file(),
                            # Adjust client config to test optimized and non-optimized implementation:
                            optimize_completion_request = optimize_completion_request,
                        )
                    client_config_dict = client_config_desc.dict_schema.dump(client_config_obj)

                    env_mock_builder = (
                        LiveServerEnvMockBuilder()
                        .set_command_line(command_line)
                        .set_cursor_cpos(cursor_cpos)
                        .set_comp_type(comp_type)
                        .set_mock_client_config_file_read(True)
                        .set_client_config_dict(client_config_dict)
                        .set_capture_stdout(True)
                        .set_capture_stderr(True)
                    )
                    with env_mock_builder.build():
                        # when:

                        __main__.main()

                        # then:

                        self.assertEqual(
                            expected_stdout_str,
                            env_mock_builder.actual_stdout.getvalue(),
                        )
                        self.assertEqual(
                            "",
                            env_mock_builder.actual_stderr.getvalue(),
                        )
