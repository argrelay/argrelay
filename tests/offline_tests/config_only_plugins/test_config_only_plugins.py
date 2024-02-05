from __future__ import annotations

from argrelay.enum_desc.CompType import CompType
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Test FS_49_96_50_77 config_only_plugins
    """

    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_config_only_suggestions(self):
        """
        Test arg values suggestion with TD_63_37_05_36 # demo
        """

        # @formatter:off
        test_cases = [
            (
                line_no(), "some_command config |", CompType.PrefixHidden,
                [
                    "print_with_exit",
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
