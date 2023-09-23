from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    same_test_data_per_class = "TD_43_24_76_58"  # single

    def test_propose_auto_comp_TD_43_24_76_58_single(self):
        """
        Test arg values suggestion with TD_43_24_76_58 # single
        """

        test_cases = [
            (
                line_no(), "some_command host goto |", CompType.PrefixShown,
                [
                    "apac",
                    "emea",
                ],
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ImplicitValue),
                },
                "No suggestion of `dev` as all `data_envelope`-s has the same `dev` `ServiceArgType.CodeMaturity`",
            ),
            (
                line_no(), "some_command host goto dev |", CompType.PrefixShown,
                [
                    "apac",
                    "emea",
                ],
                1,
                {
                    ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                },
                "Even if all `data_envelope`-s has the same `dev` `ServiceArgType.CodeMaturity`, "
                "if it is provided, the value `dev` is still consumed."
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

                self.verify_output_with_via_local_client(
                    ThisTestCase.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    {
                        found_container_ipos: expected_assignments,
                    },
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )
