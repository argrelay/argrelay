from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay_lib_server_plugin_demo.demo_service.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_76_09_29_31"  # overlapped

    def test_propose_auto_comp_TD_76_09_29_31_overlapped(self):
        """
        Test `arg_value`-s suggestion with TD_76_09_29_31 # overlapped

        Tests:
        *   FS_76_29_13_28 `command_arg` consumption priority
        """

        test_cases = [
            (
                line_no(),
                "some_command host dev goto downstream |",
                CompType.PrefixShown,
                ["amer", "emea"],
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
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: None,
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.explicit_offered_arg),
                        ServicePropName.cluster_name.name: None,
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_76_09_29_31: Step 1: geo_region is suggested "
                "(host_name is not yet based on FS_76_29_13_28 `command_arg` consumption priority)",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer |",
                CompType.PrefixShown,
                ["amer", "emea", "host-3-amer"],
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
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("amer", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.explicit_offered_arg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ValueSource.implicit_value,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_76_09_29_31: Step 2: host_name is suggested "
                "(while geo_region is already assigned based on FS_76_29_13_28 `command_arg` consumption priority)",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer am|",
                CompType.PrefixShown,
                ["amer"],
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
                        ServicePropName.geo_region.name: AssignedValue("amer", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.explicit_offered_arg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ValueSource.implicit_value,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_76_09_29_31 overlapped: Step 1: one of the explicit `arg_value` matches more than one `prop_name`-s, "
                "but it is not assigned to all `prop_name`-s => suggest only for incomplete missing `prop_name`-s",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer host|",
                CompType.PrefixShown,
                ["host-3-amer"],
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
                        ServicePropName.geo_region.name: AssignedValue("amer", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.explicit_offered_arg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ValueSource.implicit_value,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                "TD_76_09_29_31 overlapped: Step 1: one of the explicit `arg_value` matches more than one `prop_name`-s, "
                "but it is not assigned to all `prop_name`-s => suggest only for incomplete missing `prop_name`",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer amer |",
                CompType.DescribeArgs,
                [],
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
                        ServicePropName.geo_region.name: AssignedValue("amer", ValueSource.explicit_offered_arg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ValueSource.explicit_offered_arg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ValueSource.implicit_value,
                        ),
                        ServicePropName.host_name.name: AssignedValue("amer", ValueSource.explicit_offered_arg),
                    },
                    2: {
                        # ServiceEnvelopeClass.class_access_type.name
                    },
                    3: None,
                },
                # TODO: TODO_70_48_96_29: add verification of consumed and remaining tokens
                "TD_76_09_29_31 overlapped: "
                "Both geo_region and host_name are correctly assigned. "
                "All values assigned - no more suggestions. ",
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
