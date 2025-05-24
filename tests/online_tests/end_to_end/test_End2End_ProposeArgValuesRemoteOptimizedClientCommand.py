from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_test_infra.test_infra import (
    change_to_known_repo_path,
    line_no,
)
from argrelay_test_infra.test_infra.End2EndTestClass import (
    End2EndTestClass,
)


class ThisTestClass(End2EndTestClass):

    def test_ClientCommandRemoteWorkerTextProposeArgValuesOptimized_sends_valid_JSON_for_commands_with_quotes(
        self,
    ):
        """
        Invokes client via generated `@/exe/run_argrelay_client` sending `ServerAction.ProposeArgValues`.
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                f'{self.default_bound_command} desc host dev "some_unrecognized_token upstream |',
                CompType.PrefixShown,
                f"""amer
apac
emea
""",
            ),
            (
                line_no(),
                f'{self.default_bound_command} desc host dev "some_unrecognized_token" upstream a|',
                CompType.SubsequentHelp,
                f"""amer
apac
""",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_stdout_str,
                ) = test_case
                with change_to_known_repo_path("."):
                    self.assert_ProposeArgValues(
                        self.default_bound_command,
                        test_line,
                        comp_type,
                        expected_stdout_str,
                    )
