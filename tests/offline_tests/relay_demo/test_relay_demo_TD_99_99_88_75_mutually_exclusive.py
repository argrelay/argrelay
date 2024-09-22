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
    same_test_data_per_class = "TD_99_99_88_75"  # mutually exclusive

    def test_propose_auto_comp_TD_99_99_88_75_mutually_exclusive(self):
        """
        Test arg values suggestion with TD_99_99_88_75 # mutually exclusive

        Tests:
        *   FS_44_36_84_88 consume args one by one
        *   FS_76_29_13_28 arg consumption priorities
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
                        ServicePropName.code_maturity.name: AssignedValue("qa", ArgSource.ImplicitValue),
                        ServicePropName.geo_region.name: AssignedValue("apac", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue("qa-apac-downstream", ArgSource.ImplicitValue),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
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
                        ServicePropName.code_maturity.name: AssignedValue("qa", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ArgSource.ImplicitValue),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue("qa-apac-downstream", ArgSource.ImplicitValue),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                        ServicePropName.geo_region.name: AssignedValue("emea", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ArgSource.ImplicitValue,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("emea", ArgSource.ImplicitValue),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ArgSource.ImplicitValue,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                        ServicePropName.geo_region.name: AssignedValue("emea", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ArgSource.ImplicitValue,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as according to "
                "FS_76_29_13_28: user input priority, `emea` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining arg vals:
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("qa", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ArgSource.ImplicitValue),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue("qa-apac-downstream", ArgSource.ImplicitValue),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as according to "
                "FS_76_29_13_28: user input priority, `qa` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining arg vals:
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("qa", ArgSource.ImplicitValue),
                        ServicePropName.geo_region.name: AssignedValue("apac", ArgSource.ExplicitPosArg),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue("qa-apac-downstream", ArgSource.ImplicitValue),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-a-*` are suggested as according to "
                "FS_76_29_13_28: user input priority, `apac` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining arg vals:
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServicePropName.geo_region.name: AssignedValue("emea", ArgSource.ImplicitValue),
                        ServicePropName.flow_stage.name: AssignedValue("downstream", ArgSource.ImplicitValue),
                        ServicePropName.cluster_name.name: AssignedValue(
                            "dev-emea-downstream",
                            ArgSource.ImplicitValue,
                        ),
                    },
                    2: {
                        # ServiceEnvelopeClass.ClassAccessType.name
                    },
                    3: None,
                },
                "TD_99_99_88_75: `host-b-*` are suggested as according to "
                "FS_76_29_13_28: user input priority, `dev` is eaten first, and "
                # TODO: TODO_70_48_96_29: be able to assert remaining arg vals:
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
