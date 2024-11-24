from __future__ import annotations

import json
from typing import Union

from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.relay_client import __main__
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.test_infra import line_no_from_ctor, parse_line_and_cpos
from argrelay.test_infra.CustomTestCase import ShellInputTestCase
from argrelay.test_infra.CustomVerifier import ServerActionVerifier, ProposeArgValuesVerifier
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_74_69_61_79_func_id_get_data_envelopes(self):
        """
        Test FS_74_69_61_79 get set data envelope.
        """

        test_cases = [
            ThisTestCase(
                "Test that suggestion works for `index_prop`-s to select `data_envelope`-s.",
                "some_command data get ClassAccessType |",
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

    def test_FS_74_69_61_79_func_id_set_data_envelopes(self):

        is_cache_enabled = True

        test_cases = [
            ThisTestCase(
                f"Replace _entire data_ for `{ServiceEnvelopeClass.ClassAccessType.name}` via `set` "
                f"to _more items_ and check if it can be seen via `get`.",
                "some_command data get ClassAccessType |",
                CompType.InvokeAction,
                {},
                ProposeArgValuesVerifier(self),
            )
            .set_extra_data_envelopes(
                "some_command data set ClassAccessType |",
                [
                    {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassAccessType.name,
                        ServicePropName.access_type.name: "ro",
                        envelope_payload_: {},
                    },
                    {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassAccessType.name,
                        ServicePropName.access_type.name: "rw",
                        envelope_payload_: {},
                    },
                    {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassAccessType.name,
                        ServicePropName.access_type.name: "xx",
                        envelope_payload_: {},
                    },
                ],
            )
            .set_expected_suggestions(
                [
                    "ro",
                    "rw",
                    "xx",
                ]
            ),
            ThisTestCase(
                f"Replace _entire data_ for `{ServiceEnvelopeClass.ClassAccessType.name}` via `set` "
                f"to _fewer items_ and check if it can be seen via `get`.",
                "some_command data get ClassAccessType |",
                CompType.InvokeAction,
                {},
                ProposeArgValuesVerifier(self),
            )
            .set_extra_data_envelopes(
                "some_command data set ClassAccessType |",
                [
                    {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassAccessType.name,
                        ServicePropName.access_type.name: "xx",
                        envelope_payload_: {},
                    },
                ],
            )
            .set_expected_suggestions(
                [
                    "xx",
                ]
            ),
            ThisTestCase(
                f"Replace _single item_ for `{ServiceEnvelopeClass.ClassAccessType.name}` via `set` "
                f"to _another item_ and check if it can be seen via `get`.",
                "some_command data get ClassAccessType |",
                CompType.InvokeAction,
                {},
                ProposeArgValuesVerifier(self),
            )
            .set_extra_data_envelopes(
                "some_command data set ClassAccessType ro |",
                [
                    {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassAccessType.name,
                        ServicePropName.access_type.name: "xx",
                        envelope_payload_: {},
                    },
                ],
            )
            .set_expected_suggestions(
                [
                    "rw",
                    "xx",
                ]
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):

                ########################################################################################################
                # Load extra `data_envelope`-s via `set`:

                serialized_jsons = []
                for data_envelope in test_case.extra_data_envelopes:
                    serialized_jsons.append(json.dumps(data_envelope))
                provided_input = "\n".join(serialized_jsons)

                (
                    set_command_line,
                    set_cursor_cpos,
                ) = parse_line_and_cpos(test_case.extra_data_set_line)

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_enable_query_cache(is_cache_enabled)
                    .set_mock_stdin(provided_input)
                    .set_command_line(set_command_line)
                    .set_cursor_cpos(set_cursor_cpos)
                    # For `set` it is hard-coded to execute command:
                    .set_comp_type(CompType.InvokeAction)
                    .set_test_data_ids_to_load([
                        self.__class__.same_test_data_per_class,
                    ])
                )
                with env_mock_builder.build():
                    command_obj = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)

                ########################################################################################################
                # Check data via `get`:

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_enable_query_cache(is_cache_enabled)
                    .set_mock_stdin(provided_input)
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

        # FS_74_69_61_79: get set data envelope:
        # The `extra_data_envelopes` below are `set` (via `stdin`) using `extra_data_set_line` command.
        self.extra_data_set_line: str = None
        self.extra_data_envelopes: Union[list[dict], None] = None

    def set_expected_suggestions(
        self,
        given_expected_suggestions: list[str],
    ):
        assert self.expected_suggestions is None
        self.expected_suggestions = given_expected_suggestions
        return self

    def set_extra_data_envelopes(
        self,
        given_data_set_line: str,
        given_extra_data_envelopes: list[dict],
    ):
        assert self.extra_data_set_line is None
        assert self.extra_data_envelopes is None
        self.extra_data_set_line = given_data_set_line
        self.extra_data_envelopes = given_extra_data_envelopes
        return self

