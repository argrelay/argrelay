from __future__ import annotations

from typing import Union

from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.plugin_delegator.HelpDelegator import HelpDelegator
from argrelay.relay_client import __main__
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.InvocationInput import InvocationInput
from argrelay.test_infra import line_no_from_ctor, line_no, parse_line_and_cpos
from argrelay.test_infra.CustomTestCase import ShellInputTestCase
from argrelay.test_infra.CustomVerifier import RelayLineArgsVerifier, ServerActionVerifier, ProposeArgValuesVerifier
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder, EmptyEnvMockBuilder, EnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_71_87_33_52_help_hint(self):
        """
        Test FS_71_87_33_52 `help` command/func
        """

        test_cases = [
            ThisTestCase(
                "Execute `help` without args for `some_command` command.",
                "some_command help |",
                CompType.InvokeAction,
                {
                    0: {},  # help func envelope itself
                    1: {
                        # (goto, desc, list) x (host, service) external functions:
                        # TODO_32_99_70_35: (JSONPath?) Universal verifier: be able to verify arbitrary data on `EnvelopeContainer`, not only assigned types to values.
                        # "found_count": 6
                    },
                },
                RelayLineArgsVerifier(self),
            ),
            ThisTestCase(
                "Execute `help` without args for `service_relay_demo` command.",
                "service_relay_demo help |",
                CompType.PrefixShown,
                {},
                ProposeArgValuesVerifier(self),
            ),
            ThisTestCase(
                "For `help` even `internal` functions are allowed.",
                "some_command help interc|",
                CompType.PrefixShown,
                {},
                ProposeArgValuesVerifier(self),
            )
            .set_expected_suggestions(
                [
                    "intercept",
                ]
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                self.verify_output_with_new_server_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_case.test_line,
                    test_case.comp_type,
                    test_case.expected_suggestions,
                    test_case.container_ipos_to_expected_assignments,
                    None,
                    None,
                )

                ########################################################################################################
                # TODO: TODO_32_99_70_35: Instead of keeping JSON sample here, create TestCaseBuilder which integrates JSON verifier and convert the entire test class to use that.

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_command_line(test_case.command_line)
                    .set_cursor_cpos(test_case.cursor_cpos)
                    .set_comp_type(test_case.comp_type)
                    .set_test_data_ids_to_load([
                        self.__class__.same_test_data_per_class,
                    ])
                )
                with env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)

                    test_case.sever_action_verifier.verify_all(call_context_desc.dict_schema.dumps(
                        command_obj.interp_ctx.parsed_ctx,
                    ))

    def test_help_hint(self):
        """
        Expects to have help function (`HelpDelegator` via `CompType.InvokeAction`) to be invoked.
        Verifies its FS_71_87_33_52 help output with expected one.
        """
        test_cases = [
            (
                line_no(), "relay_demo help goto |",
                "FS_71_87_33_52 ensure ordered list of args in help output "
                "(command name first, then function spec args)",
                f"""relay_demo goto host ~ {TermColor.known_envelope_id.value}# {TermColor.reset_style.value}{TermColor.known_envelope_id.value}func_id_goto_host {TermColor.reset_style.value}{TermColor.help_hint.value}# {TermColor.reset_style.value}{TermColor.help_hint.value}Go (log in) to remote host {TermColor.reset_style.value}
relay_demo goto repo {SpecialChar.NoPropValue.value} {TermColor.known_envelope_id.value}# {TermColor.reset_style.value}{TermColor.known_envelope_id.value}func_id_goto_git_repo {TermColor.reset_style.value}{TermColor.help_hint.value}# {TermColor.reset_style.value}{TermColor.help_hint.value}Goto Git repository (`cd` to its path) {TermColor.reset_style.value}
relay_demo goto service {SpecialChar.NoPropValue.value} {TermColor.known_envelope_id.value}# {TermColor.reset_style.value}{TermColor.known_envelope_id.value}func_id_goto_service {TermColor.reset_style.value}{TermColor.help_hint.value}# {TermColor.reset_style.value}{TermColor.help_hint.value}Go (log in) to remote host and dir path with specified service {TermColor.reset_style.value}
""",
            ),
            (
                line_no(), "some_command help list |",
                "FS_71_87_33_52 ensure ordered list of args in help output "
                "(command name first, then function spec args)",
                f"""some_command list host {SpecialChar.NoPropValue.value} {TermColor.known_envelope_id.value}# {TermColor.reset_style.value}{TermColor.known_envelope_id.value}func_id_list_host {TermColor.reset_style.value}{TermColor.help_hint.value}# {TermColor.reset_style.value}{TermColor.help_hint.value}List remote hosts matching search query {TermColor.reset_style.value}
some_command list service {SpecialChar.NoPropValue.value} {TermColor.known_envelope_id.value}# {TermColor.reset_style.value}{TermColor.known_envelope_id.value}func_id_list_service {TermColor.reset_style.value}{TermColor.help_hint.value}# {TermColor.reset_style.value}{TermColor.help_hint.value}List service instances matching search query {TermColor.reset_style.value}
""",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    case_comment,
                    stdout_str,
                ) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                outer_env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_reset_local_server(False)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(CompType.InvokeAction)
                    .set_capture_delegator_invocation_input(HelpDelegator)
                    .set_test_data_ids_to_load([
                        self.__class__.same_test_data_per_class,
                    ])
                )
                with outer_env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)
                    interp_ctx = command_obj.interp_ctx

                    invocation_input: InvocationInput = EnvMockBuilder.invocation_input

                # TODO_43_41_95_86: use server logger to disable stdout:
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
                    HelpDelegator.invoke_action(invocation_input)

                    self.assertEqual(
                        stdout_str,
                        inner_env_mock_builder.actual_stdout.getvalue(),
                    )

                    self.assertEqual(
                        "",
                        inner_env_mock_builder.actual_stderr.getvalue(),
                    )


class ThisTestCase(ShellInputTestCase):

    def __init__(
        self,
        case_comment: str,
        test_line: str,
        comp_type: CompType,
        container_ipos_to_expected_assignments: dict[int, dict[str, AssignedValue]],
        sever_action_verifier: ServerActionVerifier,
    ):
        super().__init__(
            line_no = line_no_from_ctor(),
            case_comment = case_comment,
        )
        self.set_test_line(test_line)
        self.set_comp_type(comp_type)

        self.container_ipos_to_expected_assignments = container_ipos_to_expected_assignments
        self.sever_action_verifier = sever_action_verifier

        self.expected_suggestions: Union[list[str], None] = None

    def set_expected_suggestions(
        self,
        given_expected_suggestions: list[str],
    ):
        assert self.expected_suggestions is None
        self.expected_suggestions = given_expected_suggestions
        return self
