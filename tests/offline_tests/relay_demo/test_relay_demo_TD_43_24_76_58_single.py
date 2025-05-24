from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_43_24_76_58"  # single

    def test_propose_auto_comp_TD_43_24_76_58_single(self):
        """
        Test `arg_value`-s suggestion with TD_43_24_76_58 # single
        """

        test_cases = [
            (
                line_no(),
                "some_command host goto |",
                CompType.PrefixShown,
                [
                    "apac",
                    "emea",
                ],
                1,
                {
                    ServicePropName.code_maturity.name: AssignedValue(
                        "dev", ValueSource.implicit_value
                    ),
                },
                "No suggestion of `dev` as all `data_envelope`-s has the same `dev` `ServicePropName.code_maturity`",
            ),
            (
                line_no(),
                "some_command host goto dev |",
                CompType.PrefixShown,
                [
                    "apac",
                    "emea",
                ],
                1,
                {
                    ServicePropName.code_maturity.name: AssignedValue(
                        "dev", ValueSource.explicit_offered_arg
                    ),
                },
                "Even if all `data_envelope`-s has the same `dev` `ServicePropName.code_maturity`, "
                "if it is provided, the value `dev` is still consumed.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    found_container_ipos,
                    expected_assignments,
                    case_comment,
                ) = test_case

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    {
                        found_container_ipos: expected_assignments,
                    },
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
