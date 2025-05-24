from argrelay_app_client.handler_response.ClientResponseHandlerDescribeLineArgs import (
    indent_size,
)
from argrelay_lib_root.enum_desc.ClientExitCode import ClientExitCode
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_root.enum_desc.TermColor import TermColor
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    func_envelope_path_step_prop_name,
)
from argrelay_lib_server_plugin_demo.demo_git.DelegatorGitRepoGotoRepo import (
    func_id_goto_git_repo_,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceHostDesc import (
    func_id_desc_host_,
)
from argrelay_test_infra.test_infra import (
    change_to_known_repo_path,
    line_no,
)
from argrelay_test_infra.test_infra.End2EndTestClass import (
    End2EndTestClass,
)


# noinspection PyMethodMayBeStatic
class ThisTestClass(End2EndTestClass):

    def test_DescribeLineArgs(self):
        """
        Invokes client via generated `@/exe/run_argrelay_client` sending `ServerAction.DescribeArgs`.
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                f"{self.default_bound_command} goto h|",
                f"""
{TermColor.consumed_token.value}{self.default_bound_command}{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value}
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_n.value}3{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: {self.default_bound_command} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*{func_envelope_path_step_prop_name(2)}: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}ost{TermColor.reset_style.value} repo service
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_state.name}: ?{TermColor.reset_style.value} {FuncState.fs_beta} {FuncState.fs_demo}
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_id.name}: ?{TermColor.reset_style.value} func_id_goto_git_repo func_id_goto_host func_id_goto_service
""",
                "Test sample 1",
            ),
            (
                line_no(),
                f"{self.default_bound_command} goto s|",
                f"""
{TermColor.consumed_token.value}{self.default_bound_command}{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value}
{ReservedEnvelopeClass.class_function.name}: {TermColor.found_count_n.value}3{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{ReservedPropName.envelope_class.name}: {ReservedEnvelopeClass.class_function.name} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(0)}: {self.default_bound_command} {TermColor.other_assigned_arg_value.value}[{ValueSource.init_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_offered_arg_value.value}{func_envelope_path_step_prop_name(1)}: goto {TermColor.explicit_offered_arg_value.value}[{ValueSource.explicit_offered_arg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*{func_envelope_path_step_prop_name(2)}: ?{TermColor.reset_style.value} host repo {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}s{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}ervice{TermColor.reset_style.value}
{" " * indent_size}{TermColor.other_assigned_arg_value.value}{func_envelope_path_step_prop_name(3)}: {SpecialChar.NoPropValue.value} {TermColor.other_assigned_arg_value.value}[{ValueSource.implicit_value.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_state.name}: ?{TermColor.reset_style.value} {FuncState.fs_beta} {FuncState.fs_demo}
{" " * indent_size}{TermColor.remaining_value.value}{ReservedPropName.func_id.name}: ?{TermColor.reset_style.value} func_id_goto_git_repo func_id_goto_host func_id_goto_service
""",
                "Test sample 2",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    expected_stdout_str,
                    case_comment,
                ) = test_case
                with change_to_known_repo_path("."):
                    self.assert_DescribeLineArgs(
                        self.default_bound_command,
                        test_line,
                        expected_stdout_str,
                    )

    def test_ProposeArgValues(self):
        """
        Invokes client via generated `@/exe/run_argrelay_client` sending `ServerAction.ProposeArgValues`.
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                f"{self.default_bound_command} desc host dev upstream |",
                CompType.PrefixShown,
                f"""amer
apac
emea
""",
                "Test sample 1",
            ),
            (
                line_no(),
                f"{self.default_bound_command} desc host dev upstream a|",
                CompType.SubsequentHelp,
                f"""amer
apac
""",
                "Test sample 2",
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
                    case_comment,
                ) = test_case
                with change_to_known_repo_path("."):
                    self.assert_ProposeArgValues(
                        self.default_bound_command,
                        test_line,
                        comp_type,
                        expected_stdout_str,
                    )

    def test_RelayLineArgs(self):
        """
        Invokes client via generated `@/exe/run_argrelay_client` sending `ServerAction.RelayLineArgs`.
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                f"{self.default_bound_command} desc host dev upstream amer".split(" "),
                0,
                "",
                "INFO: command executed successfully: demo implementation is a stub"
                + "\n",
                f"{func_id_desc_host_} is a stub",
            ),
            (
                line_no(),
                f"{self.default_bound_command} echo one two three four five".split(" "),
                0,
                f"{self.default_bound_command} echo one two three four five\n",
                "",
                "FS_43_50_57_71: `echo_args` func executes successfully printing its args.",
            ),
            (
                line_no(),
                f"{self.default_bound_command} goto host dev upstream amer".split(" "),
                0,
                "",
                "INFO: command executed successfully: demo implementation is a stub"
                + "\n",
                "`DelegatorError` executes successfully with output on STDERR.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    command_line_args,
                    expected_exit_code,
                    expected_stdout_str,
                    expected_stderr_str,
                    case_comment,
                ) = test_case
                with change_to_known_repo_path("."):
                    self.assert_RelayLineArgs(
                        command_line_args,
                        expected_stdout_str,
                        expected_stderr_str,
                        expected_exit_code,
                    )

    def test_prohibit_unconsumed_args(self):
        """
        These cases test that `prohibit_unconsumed_args` works for selected funcs.
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                f"{self.default_bound_command} help this_arg_is_unknown_and_unconsumed".split(
                    " "
                ),
                ClientExitCode.GeneralError.value,
                "",
                f"ERROR: this function prohibits unrecognized args (see {TermColor.remaining_token.value}highlighted{TermColor.reset_style.value} on Alt+Shift+Q results): {TermColor.remaining_token.value}this_arg_is_unknown_and_unconsumed{TermColor.reset_style.value}"
                + "\n",
                "FS_71_87_33_52 help prohibits unconsumed args",
            ),
            (
                line_no(),
                f"{self.default_bound_command} intercept this_arg_is_unknown_and_unconsumed".split(
                    " "
                ),
                ClientExitCode.ClientSuccess.value,
                # There is output - ignore:
                None,
                "",
                "FS_88_66_66_73 intercept does NOT prohibit unconsumed args",
            ),
            (
                line_no(),
                f"{self.default_bound_command} goto repo this_arg_is_unknown_and_unconsumed".split(
                    " "
                ),
                ClientExitCode.GeneralError.value,
                "",
                f"ERROR: this function prohibits unrecognized args (see {TermColor.remaining_token.value}highlighted{TermColor.reset_style.value} on Alt+Shift+Q results): {TermColor.remaining_token.value}this_arg_is_unknown_and_unconsumed{TermColor.reset_style.value}"
                + "\n",
                f"FS_67_16_61_97 git_plugin: {func_id_goto_git_repo_} prohibits unconsumed args",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    command_line_args,
                    expected_exit_code,
                    expected_stdout_str,
                    expected_stderr_str,
                    case_comment,
                ) = test_case
                with change_to_known_repo_path("."):
                    self.assert_RelayLineArgs(
                        command_line_args,
                        expected_stdout_str,
                        expected_stderr_str,
                        expected_exit_code,
                    )

    def test_ProposeArgValues_fails(self):
        wrong_expected_stdout = "whatever"
        with self.assertRaises(AssertionError):
            with change_to_known_repo_path("."):
                self.assert_ProposeArgValues(
                    self.default_bound_command,
                    f"{self.default_bound_command} desc host dev upstream |",
                    CompType.PrefixShown,
                    wrong_expected_stdout,
                    0,
                )

    def test_DescribeLineArgs_fails(self):
        wrong_expected_stdout = "whatever"
        with self.assertRaises(AssertionError):
            with change_to_known_repo_path("."):
                self.assert_DescribeLineArgs(
                    self.default_bound_command,
                    f"{self.default_bound_command} goto h|",
                    wrong_expected_stdout,
                    0,
                )

    def test_RelayLineArgs_fails(self):
        wrong_expected_exit_code = 1
        with self.assertRaises(AssertionError):
            with change_to_known_repo_path("."):
                self.assert_RelayLineArgs(
                    f"{self.default_bound_command} desc host dev upstream am".split(
                        " "
                    ),
                    None,
                    None,
                    wrong_expected_exit_code,
                )
