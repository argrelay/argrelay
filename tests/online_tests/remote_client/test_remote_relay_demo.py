from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceDelegator import ServiceDelegator
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import (
    LiveServerEnvMockBuilder,
)
from argrelay.test_infra.RemoteTestClass import RemoteTestClass


class ThisTestClass(RemoteTestClass):

    def test_RemoteTestClass_with_LiveServerEnvMockBuilder(self):
        """
        This test ensures `RemoteTestClass` with `LiveServerEnvMockBuilder` are usable.
        """

        test_cases = [
            (
                line_no(),
                "some_command list host dev |",
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("list", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("host", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassHost.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.code_maturity.name: AssignedValue("dev", ArgSource.ExplicitPosArg),
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
                        ServiceArgType.host_name.name: "zxcv-du",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "zxcv-dd",
                    },
                    3: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "poiu-dd",
                    },
                    4: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "asdf-du",
                    },
                    5: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "xcvb-dd",
                    },
                    6: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                        ServiceArgType.host_name.name: "qwer-du",
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ServiceEnvelopeClass.ClassService.name,
                            ArgSource.InitValue,
                        ),
                        ServiceArgType.service_name.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServiceArgType.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.geo_region.name: AssignedValue("apac", ArgSource.ImplicitValue),
                    },
                    2: {
                        # Nothing is assigned for `ServiceArgType.access_type`, but it exists.
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
                        ServiceArgType.service_name.name: "s_b",
                        ServiceArgType.host_name.name: "qwer-pd-1",
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                        ServiceArgType.service_name.name: "s_b",
                        ServiceArgType.host_name.name: "qwer-pd-2",
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

                self.verify_output_via_remote_client(
                    test_line,
                    CompType.InvokeAction,
                    None,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_field_values,
                    None,
                    LiveServerEnvMockBuilder(),
                )
