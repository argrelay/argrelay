from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_helper.LocalTestCase import LocalTestCase


class ThisTestCase(LocalTestCase):
    same_test_data_per_class = "TD_38_03_48_51"  # large generated

    def test_propose_auto_comp_TD_38_03_48_51_large_generated(self):
        """
        Test that TD_38_03_48_51 large generated data set is functional.
        """

        test_cases = [
            (
                line_no(), "relay_demo goto host cm1 fs2 gr3 hs|", CompType.PrefixShown,
                [f"hs{host_number}" for host_number in range(0, 10)],
                {
                    1: {
                        ServiceArgType.CodeMaturity.name: AssignedValue("cm1", ArgSource.ExplicitPosArg),
                        ServiceArgType.FlowStage.name: AssignedValue("fs2", ArgSource.ExplicitPosArg),
                        ServiceArgType.GeoRegion.name: AssignedValue("gr3", ArgSource.ExplicitPosArg),
                    },
                },
                "Ensure it suggests relevant hosts.",
            ),
            (
                line_no(), "relay_demo goto host cm1 fs2 gr3|", CompType.PrefixShown,
                [
                    "gr3",
                ],
                {
                    1: {
                        ServiceArgType.CodeMaturity.name: AssignedValue("cm1", ArgSource.ExplicitPosArg),
                        ServiceArgType.FlowStage.name: AssignedValue("fs2", ArgSource.ExplicitPosArg),
                        ServiceArgType.GeoRegion.name: None,
                    },
                },
                "Ensure it suggests the only `GeoRegion` matching the current prefix.",
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

                self.verify_output_with_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )