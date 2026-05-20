from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    func_envelope_path_step_prop_name,
)
from argrelay_lib_server_plugin_demo.demo_sleep.DelegatorSleep import (
    class_sleep_,
    DelegatorSleep,
    func_id_sleep_,
    time_delay_prop_name_,
)
from argrelay_test_infra.test_infra import (
    assert_test_module_name_embeds_prod_class_name,
    line_no,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorSleep)

    def test_DelegatorSleep(self):

        test_cases = [
            (
                line_no(),
                "lay sleep 4s |",
                [],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "lay",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "sleep",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_sleep_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_sleep_,
                            ValueSource.init_value,
                        ),
                        time_delay_prop_name_: AssignedValue(
                            "4s", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: None,
                },
                DelegatorSleep,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "4s",
                    },
                    2: None,
                },
                {
                    0: 0,
                    1: 0,
                },
                f"Access `{func_id_sleep_}` via `lay sleep` and select 4s duration.",
            ),
            (
                line_no(),
                "lay sleep 16s |",
                [],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "lay",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "sleep",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_sleep_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_sleep_,
                            ValueSource.init_value,
                        ),
                        time_delay_prop_name_: AssignedValue(
                            "16s", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: None,
                },
                DelegatorSleep,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "16s",
                    },
                    2: None,
                },
                {
                    0: 0,
                    1: 0,
                },
                f"Access `{func_id_sleep_}` via `lay sleep` and select 16s duration.",
            ),
            (
                line_no(),
                "some_command sleep 64s |",
                [],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "sleep",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_sleep_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_sleep_,
                            ValueSource.init_value,
                        ),
                        time_delay_prop_name_: AssignedValue(
                            "64s", ValueSource.explicit_offered_arg
                        ),
                    },
                    2: None,
                },
                DelegatorSleep,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "64s",
                    },
                    2: None,
                },
                {
                    0: 0,
                    1: 0,
                },
                f"Access `{func_id_sleep_}` via `some_command sleep` and select 64s duration.",
            ),
            (
                line_no(),
                "lay sleep |",
                [
                    "16s",
                    "4s",
                    "64s",
                ],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "lay",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "sleep",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_sleep_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_sleep_,
                            ValueSource.init_value,
                        ),
                    },
                    2: None,
                },
                DelegatorSleep,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "4s",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "16s",
                    },
                    3: {
                        ReservedPropName.envelope_class.name: class_sleep_,
                        time_delay_prop_name_: "64s",
                    },
                    4: None,
                },
                {
                    0: 0,
                    1: 0,
                },
                f"Tab-complete `lay sleep` with no args shows all available durations.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    CompType.InvokeAction,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    expected_container_ipos_to_used_token_bucket,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
