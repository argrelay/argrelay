from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceDelegator import ServiceDelegator
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import (
    LiveServerEnvMockBuilder,
)
from argrelay.test_helper.RemoteTestCase import RemoteTestCase


class ThisTestCase(RemoteTestCase):

    def test_RemoteTestCase_with_LiveServerEnvMockBuilder(self):
        """
        This test ensures `RemoteTestCase` with `LiveServerEnvMockBuilder` are usable.
        """

        test_cases = [
            (
                line_no(),
                "some_command list host dev |",
                {
                    0: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("list", ArgSource.ExplicitPosArg),
                        GlobalArgType.ObjectSelector.name: AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassHost.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.CodeMaturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
                    },
                    2: None,
                },
                ServiceDelegator,
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "zxcv-du",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "zxcv-dd",
                    },
                    3: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "poiu-dd",
                    },
                    4: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "asdf-du",
                    },
                    5: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "xcvb-dd",
                    },
                    6: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.HostName.name: "qwer-du",
                    },
                    7: None,
                },
                "Basic test 1 that list multiple objects using remote connection "
                "with `InvocationInput` are intercepted via `EnvMockBuilder`."
            ),
            (
                line_no(),
                "some_command goto service s_b prod |",
                {
                    0: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                        GlobalArgType.ObjectSelector.name: AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassService.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.ServiceName.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.GeoRegion.name: AssignedValue("apac", ArgSource.ImplicitValue),
                    },
                    2: {
                        # Nothing is assigned for `ServiceArgType.AccessType`, but it exists.
                    },
                    3: None,
                },
                ErrorDelegator,
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.ServiceName.name: "s_b",
                        ServiceArgType.HostName.name: "qwer-pd-1",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.ServiceName.name: "s_b",
                        ServiceArgType.HostName.name: "qwer-pd-2",
                    },
                    3: None,
                },
                "Basic test 2 that list multiple objects using remote connection "
                "with `InvocationInput` intercept via `EnvMockBuilder`."
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    case_comment,
                ) = test_case

                self.verify_output_with_via_remote_client(
                    test_line,
                    CompType.InvokeAction,
                    None,
                    None,
                    delegator_class,
                    None,
                    LiveServerEnvMockBuilder(),
                )
