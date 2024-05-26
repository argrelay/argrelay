from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_39_25_11_76"  # missing props

    def test_arg_assignments_and_suggestions_for_TD_39_25_11_76_missing_props(self):
        test_cases = [
            (
                line_no(), "relay_demo goto host zxcv |", CompType.PrefixShown,
                [],
                None,
                "See Step 1 in the next test case."
            ),
            (
                line_no(), "relay_demo goto host zxcv |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    1: {
                        ServiceArgType.geo_region.name: [
                            "emea"
                        ],
                        ServiceArgType.cluster_name.name: [
                            "dev-emea-downstream",
                        ],
                        ServiceArgType.host_name.name: AssignedValue("zxcv", ArgSource.ExplicitPosArg),
                        ServiceArgType.live_status.name: AssignedValue("red", ArgSource.ImplicitValue),
                    },
                    2: {
                        ServiceArgType.access_type.name: AssignedValue("rw", ArgSource.DefaultValue),
                    },
                    3: None,
                },
                "Step 1: "
                "TD_39_25_11_76: `data_envelope`-s with missing props: "
                "there are two `zxcv` hosts: one in `apac` and another in `emea`, "
                "but there is no suggestions because `apac` host does not have `ServiceArgType.live_status` property "
                "which is assigned as `ArgSource.ImplicitValue` now from the single value available in `emea` - "
                "this hides existence of the host in `apac`. "

                "Also, `ServiceArgType.geo_region` and `ServiceArgType.cluster_name` are not singled out "
                "even though there is only single value - this happens because "
                "`EnvelopeContainer.populate_implicit_arg_values` is sets `ServiceArgType.live_status` to "
                "`ArgSource.ImplicitValue` but still sees multiple `data_envelope`-s with different values"
                "for `ServiceArgType.geo_region` and `ServiceArgType.cluster_name`.",
            ),
            (
                line_no(), "relay_demo goto host asdf |", CompType.PrefixShown,
                [
                    "apac",
                    "emea",
                ],
                None,
                "See Step 2 in the next test case."
            ),
            (
                line_no(), "relay_demo goto host asdf |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    1: {
                        ServiceArgType.geo_region.name: [
                            "apac",
                            "emea",
                        ],
                        ServiceArgType.cluster_name.name: [
                            "dev-apac-downstream",
                            "dev-emea-downstream",
                        ],
                        ServiceArgType.host_name.name: AssignedValue("asdf", ArgSource.ExplicitPosArg),
                        ServiceArgType.live_status.name: AssignedValue("yellow", ArgSource.ImplicitValue),
                    },
                    2: {
                        ServiceArgType.access_type.name: None,
                    },
                    3: None,
                },
                "Step 2: "
                "TD_39_25_11_76: `data_envelope`-s with missing props: "
                "unlike Step 1, here hosts are suggested from both `emea` and `apac` because "
                "host `asdf` has `ServiceArgType.live_status` property everywhere.",
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
