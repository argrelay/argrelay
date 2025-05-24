from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_demo.demo_service.ServiceLoader import ServiceLoader
from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_38_03_48_51"  # large generated

    def test_propose_auto_comp_TD_38_03_48_51_large_generated(self):
        """
        Test that TD_38_03_48_51 large generated data set is functional.
        """

        ServiceLoader.object_multiplier = 10

        test_cases = [
            (
                line_no(),
                "lay goto host cm1 fs2 gr3 hs|",
                CompType.PrefixShown,
                [
                    f"hs{host_number}"
                    for host_number in range(0, ServiceLoader.object_multiplier)
                ],
                {
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue(
                            "cm1", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.flow_stage.name: AssignedValue(
                            "fs2", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.geo_region.name: AssignedValue(
                            "gr3", ValueSource.explicit_offered_arg
                        ),
                    },
                },
                "Ensure it suggests relevant hosts.",
            ),
            (
                line_no(),
                "lay goto host cm1 fs2 gr3|",
                CompType.PrefixShown,
                [
                    "gr3",
                ],
                {
                    1: {
                        ServicePropName.code_maturity.name: AssignedValue(
                            "cm1", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.flow_stage.name: AssignedValue(
                            "fs2", ValueSource.explicit_offered_arg
                        ),
                        ServicePropName.geo_region.name: None,
                    },
                },
                "Ensure it suggests the only `geo_region` matching the current prefix.",
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
