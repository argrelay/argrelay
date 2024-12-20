from __future__ import annotations

from argrelay.custom_integ.DelegatorSshDst import DelegatorSshDst, func_id_ssh_dst_, class_ssh_dst_
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no, assert_test_module_name_embeds_prod_class_name
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorSshDst)

    def test_DelegatorSshDst(self):

        test_cases = [
            (
                line_no(),
                "ar_ssh dev |",
                [],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "ar_ssh",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{func_envelope_path_step_prop_name(3)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_ssh_dst_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_ssh_dst_,
                            ValueSource.init_value,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                        ServicePropName.run_mode.name: AssignedValue("active", ValueSource.implicit_value),
                    },
                    2: None,
                },
                DelegatorSshDst,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_ssh_dst_,
                        ServicePropName.run_mode.name: "active",
                        ServicePropName.code_maturity.name: "dev",
                        ServicePropName.service_name.name: "tmp",
                    },
                    2: None,
                },
                {
                    # TODO: TODO_75_52_01_67: also fix this (related to `token_bucket`-s)
                    #       When func is selected by the first arg only, apparently,
                    #       `token_bucket` logic is not invoked and `None` value is left:
                    0: None,
                    1: 0,
                },
                f"Access `{func_id_ssh_dst_}` via `ar_ssh` command and "
                f"ensure `{DelegatorSshDst.__name__}` works."
            ),
            (
                line_no(),
                "some_command ssh passive |",
                [],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "ssh",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{func_envelope_path_step_prop_name(3)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_ssh_dst_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_ssh_dst_,
                            ValueSource.init_value,
                        ),
                        ServicePropName.run_mode.name: AssignedValue("passive", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.implicit_value),
                        ServicePropName.service_name.name: AssignedValue("home", ValueSource.implicit_value),
                        ServicePropName.dir_path.name: AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                    },
                    2: None,
                },
                DelegatorSshDst,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_ssh_dst_,
                        ServicePropName.run_mode.name: "passive",
                        ServicePropName.service_name.name: "home",
                    },
                    2: None,
                },
                {
                    0: 0,
                    1: 0,
                },
                f"Access `{func_id_ssh_dst_}` via `some_command ssh` command and "
                f"ensure `{DelegatorSshDst.__name__}` works."
            ),
            (
                line_no(),
                "ar_ssh |",
                [
                    "dev",
                    "test",
                ],
                {
                    0: {
                        # TODO: Use `explicit_offered_arg` for the first arg instead of `init_value`:
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "ar_ssh",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{func_envelope_path_step_prop_name(3)}": AssignedValue(
                            SpecialChar.NoPropValue.value,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_state.name}": AssignedValue(
                            FuncState.fs_demo.name,
                            ValueSource.implicit_value,
                        ),
                        f"{ReservedPropName.func_id.name}": AssignedValue(
                            func_id_ssh_dst_,
                            ValueSource.implicit_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            class_ssh_dst_,
                            ValueSource.init_value,
                        ),
                        ServicePropName.flow_stage.name: AssignedValue("backend", ValueSource.implicit_value),
                    },
                    2: None,
                },
                DelegatorSshDst,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: class_ssh_dst_,
                        ServicePropName.flow_stage.name: "backend",
                        ServicePropName.service_name.name: "tmp",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: class_ssh_dst_,
                        ServicePropName.flow_stage.name: "backend",
                        ServicePropName.service_name.name: "root",
                    },
                    3: {
                        ReservedPropName.envelope_class.name: class_ssh_dst_,
                        ServicePropName.flow_stage.name: "backend",
                        ServicePropName.service_name.name: "home",
                    },
                    4: None,
                },
                {
                    # TODO: TODO_75_52_01_67: also fix this (related to `token_bucket`-s)
                    #       When func is selected by the first arg only, apparently,
                    #       `token_bucket` logic is not invoked and `None` value is left:
                    0: None,
                    1: None,
                },
                f"Run `{func_id_ssh_dst_}` without any args to ensure `{DelegatorSshDst.__name__}` works."
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
