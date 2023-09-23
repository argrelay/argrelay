
from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

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
                "TD_76_09_29_31: GeoRegion set is suggested (while HostName set is the same)",
            ),
            (
                line_no(),
                "some_command host dev goto downstream amer |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "TD_76_09_29_31: HostName set is suggested (while GeoRegion set is the same)",
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
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                        GlobalArgType.ObjectSelector.name: AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                        ServiceArgType.GeoRegion.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                        ServiceArgType.FlowStage.name: AssignedValue("downstream", ArgSource.ExplicitPosArg),
                        ServiceArgType.ClusterName.name: AssignedValue("dev-amer-downstream", ArgSource.ImplicitValue),
                        ServiceArgType.HostName.name: AssignedValue("amer", ArgSource.ExplicitPosArg),
                    },
                },
                # TODO: add verification of consumed and unconsumed tokens
                ErrorDelegator,
                "TD_76_09_29_31: Both GeoRegion and HostName are correctly assigned",
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
                    ThisTestCase.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
