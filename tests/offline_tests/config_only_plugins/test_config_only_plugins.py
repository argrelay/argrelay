from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
    mock_subprocess_popen,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Test FS_49_96_50_77 config_only_plugins
    """

    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_config_only_suggestions(self):

        test_cases = [
            (
                line_no(), "some_command config |", CompType.PrefixHidden,
                [
                    "double_execution",
                    "print_with_exit",
                    "print_with_io_redirect",
                    "print_with_level",
                ],
                "Suggest next step in path to select existing config-only function",
            ),
            (
                line_no(), "some_command config print_with_level |", CompType.PrefixHidden,
                [
                    "ERROR",
                    "INFO",
                    "WARN",
                ],
                "Suggest next step in path to select existing config-only function",
            ),
            (
                line_no(), "some_command config ERROR print_with_exit |", CompType.PrefixHidden,
                [
                    "1",
                    "2",
                ],
                "Suggest next step in path to select existing config-only function",
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

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_FS_49_96_50_77_config_only_with_FS_72_53_55_13_default_overrides(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command config double_execution ERROR 1 |", CompType.DescribeArgs,
                {
                    1: {
                        "severity_level": AssignedValue("ERROR", ArgSource.ExplicitPosArg),
                        "exit_code": AssignedValue("1", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        "severity_level": AssignedValue("ERROR", ArgSource.DefaultValue),
                        "exit_code": AssignedValue("1", ArgSource.DefaultValue),
                    },
                    3: None,
                },
                {
                    2: {
                        "severity_level": [
                            "ERROR",
                            "INFO",
                            "WARN",
                        ],
                        "exit_code": [
                            "0",
                            "1",
                            "2",
                        ],
                    },
                    3: None,
                },
                None,
                "FS_72_53_55_13: Provide options hidden by defaults.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )


    def test_config_only_invocation(self):
        """
        NOTE: These tests only assert command line to be executed externally: exit_code, stderr, stdout are mocked.
        """

        test_cases = [
            (
                line_no(), "some_command config ERROR print_with_level 1 |", CompType.InvokeAction,
                {
                    """
echo \"ERROR: text message C\"
""": (
                        0,
                        "text message C",
                        "",
                    ),
                },
                "Assert (mocked) command execution with exit code == 0",
            ),
            (
                line_no(), "some_command config ERROR print_with_exit 2 |", CompType.InvokeAction,
                {
                    """
echo \"text message D\"
exit 2

""": (
                        2,
                        "ERROR: text message D",
                        "",
                    ),
                },
                "Assert (mocked) command execution with exit code != 0",
            ),
            (
                line_no(), "some_command config print_with_io_redirect ERROR 1 |", CompType.InvokeAction,
                {
                    """
if [[ 1 -eq 0 ]]
then
    echo \"text message C\" 1>&1
else
    echo \"text message C\" 1>&2
fi
exit 1

""": (
                        1,
                        "text message C",
                        "",
                    ),
                },
                "Assert (mocked) command with IO redirection (but it is not executed)",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    popen_mock_config,
                    case_comment,
                ) = test_case

                with mock_subprocess_popen(popen_mock_config) as popen_mock:
                    with self.assertRaises(SystemExit) as cm:
                        self.verify_output_with_via_local_client(
                            self.__class__.same_test_data_per_class,
                            test_line,
                            comp_type,
                            None,
                            None,
                            None,
                            None,
                            None,
                            LocalClientEnvMockBuilder().set_reset_local_server(False),
                        )
                    expected_exit_code = next(iter(popen_mock_config.values()))[0]
                    self.assertEqual(cm.exception.code, expected_exit_code)
