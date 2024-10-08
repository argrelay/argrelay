from __future__ import annotations

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_76_09_29_31"  # overlapped

    def test_propose_auto_comp_TD_76_09_29_31_overlapped(self):
        """
        Test arg values suggestion with TD_76_09_29_31 # overlapped

        Tests:
        *   FS_76_29_13_28 arg consumption priorities
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
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.ClassHost.name,
                            ArgSource.InitValue,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: None,
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServicePropName.cluster_name.name: None,
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_76_09_29_31: Step 1: geo_region is suggested "
                "(host_name is not yet based on FS_76_29_13_28 arg consumption priorities)",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer |",
                CompType.PrefixShown,
                ["amer", "emea", "host-3-amer"],
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.ClassHost.name,
                            ArgSource.InitValue,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ArgSource.ImplicitValue,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_76_09_29_31: Step 2: host_name is suggested "
                "(while geo_region is already assigned based on FS_76_29_13_28 arg consumption priorities)",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer am|",
                CompType.PrefixShown,
                ["amer"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ArgSource.ImplicitValue,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_76_09_29_31 overlapped: Step 1: one of the explicit value matches more than one type, "
                "but it is not assigned to all arg types => suggest only for incomplete missing arg types",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer host|",
                CompType.PrefixShown,
                ["host-3-amer"],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ArgSource.ImplicitValue,
                        ),
                        ServicePropName.host_name.name: None,
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_76_09_29_31 overlapped: Step 1: one of the explicit value matches more than one type, "
                "but it is not assigned to all arg types => suggest only for incomplete missing arg types",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer amer |",
                CompType.DescribeArgs,
                [],
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-amer-downstream",
                            ArgSource.ImplicitValue,
                        ),
                        ServicePropName.host_name.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
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
