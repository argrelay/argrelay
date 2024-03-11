from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
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
        """

        test_cases = [
            (
                line_no(),
                "some_command host dev goto downstream |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "TD_76_09_29_31: geo_region set is suggested (while host_name set is the same)",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "TD_76_09_29_31: host_name set is suggested (while geo_region set is the same)",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer am|",
                CompType.PrefixShown,
                ["amer"],
                {},
                None,
                "TD_76_09_29_31 # overlapped: one of the explicit value matches more than one type, "
                "but it is not assigned to all arg types => some suggestion for incomplete missing arg types",
            ),
            (
                line_no(),
                "some_command goto host dev downstream amer amer |",
                CompType.PrefixShown,
                [],
                {},
                None,
                "TD_76_09_29_31 # overlapped: all values assigned - no more suggestions",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer amer |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServiceArgType.geo_region.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServiceArgType.flow_stage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServiceArgType.cluster_name.name: AssignedValue("dev-amer-downstream", ArgSource.ImplicitValue),
                        ServiceArgType.host_name.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                    },
                },
                # TODO: add verification of consumed and unconsumed tokens
                ErrorDelegator,
                "TD_76_09_29_31: Both geo_region and host_name are correctly assigned",
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
                    delegator_class,
                    case_comment,
                ) = test_case

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    delegator_class,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
