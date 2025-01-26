from __future__ import annotations

from typing import Union

from argrelay_api_server_cli.schema_request.CallContextSchema import call_context_desc
from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_app_client.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay_app_client.relay_client import __main__
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.SpecialFunc import SpecialFunc
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorDataBackendGet import DelegatorDataBackendGet
from argrelay_test_infra.test_infra import (
    assert_test_module_name_embeds_prod_class_name,
    line_no_from_ctor,
)
from argrelay_test_infra.test_infra.CustomTestCase import ShellInputTestCase
from argrelay_test_infra.test_infra.CustomVerifier import (
    ProposeArgValuesVerifier,
    ServerActionVerifier,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorDataBackendGet)

    def test_FS_74_69_61_79_func_id_get_data_envelopes(self):
        """
        Test FS_74_69_61_79 get set data envelope.
        """

        test_cases = [
            ThisTestCase(
                "Test that suggestion works for `index_prop`-s to select `data_envelope`-s.",
                "some_command data get class_access_type |",
                CompType.PrefixShown,
                {},
                ProposeArgValuesVerifier(self),
            )
            .set_expected_suggestions(
                [
                    "ro",
                    "rw",
                ]
            ),
            ThisTestCase(
                f"Test that suggestion does not make server fail if "
                f"`{SpecialFunc.func_id_get_data_envelopes.name}` is prefixed with "
                f"`{SpecialFunc.func_id_help_hint.name}`.",
                "some_command help data get |",
                CompType.PrefixShown,
                {},
                ProposeArgValuesVerifier(self),
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
