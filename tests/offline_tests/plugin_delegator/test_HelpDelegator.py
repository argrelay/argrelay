from __future__ import annotations

from typing import Union

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.relay_client import __main__
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.test_infra import line_no_from_ctor
from argrelay.test_infra.CustomTestCase import ShellInputTestCase
from argrelay.test_infra.CustomVerifier import RelayLineArgsVerifier, ProposeArgValuesVerifier, ServerActionVerifier
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
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
                # TODO_32_99_70_35: Instead of keeping JSON sample here, create TestCaseBuilder which integrates JSON verifier and convert the entire test class to use that.

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
                    assert isinstance(command_obj, AbstractLocalClientCommand)

                    test_case.sever_action_verifier.verify_all(call_context_desc.dict_schema.dumps(
                        command_obj.interp_ctx.parsed_ctx,
                    ))


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
