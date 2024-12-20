from __future__ import annotations

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_99_99_88_75"  # mutually exclusive

    def test_propose_auto_comp_TD_99_99_88_75_mutually_exclusive(self):
        """
        Test `arg_value`-s suggestion with TD_99_99_88_75 # mutually exclusive

        Tests:
        *   FS_44_36_84_88 consume args one by one
        *   FS_76_29_13_28 `command_arg` consumption priority
        """

        test_cases = [
            (
                line_no(),
                "some_command host goto apac |",
                CompType.PrefixShown,
                ["host-a-1", "host-a-2"],
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_host.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("qa", ValueSource.implicit_value),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "qa-apac-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as there is only them envelope matching `apac`",
            ),
            (
                line_no(),
                "some_command host goto qa |",
                CompType.PrefixShown,
                ["host-a-1", "host-a-2"],
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_host.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("qa", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.implicit_value),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "qa-apac-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as there is only them envelope matching `qa`",
            ),
            (
                line_no(),
                "some_command host goto emea |",
                CompType.PrefixShown,
                ["host-b-1", "host-b-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.implicit_value),
                        ServicePropName.geo_region.name: AssignedValue("emea", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as there is only them envelope matching `emea`",
            ),
            (
                line_no(),
                "some_command host goto dev |",
                CompType.PrefixShown,
                ["host-b-1", "host-b-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("emea", ValueSource.implicit_value),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as there is only them envelope matching `dev`",
            ),
            (
                line_no(),
                "some_command host goto emea qa |",
                CompType.PrefixShown,
                ["host-b-1", "host-b-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.implicit_value),
                        ServicePropName.geo_region.name: AssignedValue("emea", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as according to "
                "FS_76_29_13_28: `command_arg` consumption priority, `emea` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining `arg_value`-s:
                "FS_44_36_84_88: `qa` become remaining "
                "(rather than becoming FS_51_67_38_37 impossible arg combination)",
            ),
            (
                line_no(),
                "some_command host goto qa emea |",
                CompType.PrefixShown,
                ["host-a-1", "host-a-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("qa", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.implicit_value),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "qa-apac-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as according to "
                "FS_76_29_13_28: `command_arg` consumption priority, `qa` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining `arg_value`-s:
                "FS_44_36_84_88: `emea` become remaining "
                "(rather than becoming FS_51_67_38_37 impossible arg combination)",
            ),
            (
                line_no(),
                "some_command host goto apac dev |",
                CompType.PrefixShown,
                ["host-a-1", "host-a-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("qa", ValueSource.implicit_value),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "qa-apac-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as according to "
                "FS_76_29_13_28: `command_arg` consumption priority, `apac` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining `arg_value`-s:
                "FS_44_36_84_88: `dev` become remaining "
                "(rather than becoming FS_51_67_38_37 impossible arg combination)",
            ),
            (
                line_no(),
                "some_command host goto dev apac |",
                CompType.PrefixShown,
                ["host-b-1", "host-b-2"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("emea", ValueSource.implicit_value),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.implicit_value),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ValueSource.implicit_value,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as according to "
                "FS_76_29_13_28: `command_arg` consumption priority, `dev` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining `arg_value`-s:
                "FS_44_36_84_88: `apac` become remaining "
                "(rather than becoming FS_51_67_38_37 impossible arg combination)",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
