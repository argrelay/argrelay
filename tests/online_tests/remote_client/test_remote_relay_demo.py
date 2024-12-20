from __future__ import annotations

from argrelay.custom_integ.DelegatorServiceHostList import DelegatorServiceHostList
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_delegator.DelegatorError import DelegatorError
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "list",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "host",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_host.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.code_maturity.name: AssignedValue("dev", ValueSource.explicit_offered_arg),
                    },
                    2: None,
                },
                DelegatorServiceHostList,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "zxcv-du",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "zxcv-dd",
                    },
                    3: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "poiu-dd",
                    },
                    4: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "asdf-du",
                    },
                    5: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "xcvb-dd",
                    },
                    6: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                        ServicePropName.host_name.name: "qwer-du",
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "goto",
                            ValueSource.explicit_offered_arg,
                        ),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue(
                            "service",
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ServiceEnvelopeClass.class_service.name,
                            ValueSource.init_value,
                        ),
                        ServicePropName.service_name.name: AssignedValue("s_b", ValueSource.explicit_offered_arg),
                        ServicePropName.code_maturity.name: AssignedValue("prod", ValueSource.explicit_offered_arg),
                        ServicePropName.geo_region.name: AssignedValue("apac", ValueSource.implicit_value),
                    },
                    2: {
                        # Nothing is assigned for `ServicePropName.access_type`, but it exists.
                    },
                    3: None,
                },
                DelegatorError,
                {
                    0: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                    },
                    1: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "s_b",
                        ServicePropName.host_name.name: "qwer-pd-1",
                    },
                    2: {
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                        ServicePropName.service_name.name: "s_b",
                        ServicePropName.host_name.name: "qwer-pd-2",
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
                    envelope_ipos_to_prop_values,
                    case_comment,
                ) = test_case

                self.verify_output_via_remote_client(
                    test_line,
                    CompType.InvokeAction,
                    None,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    envelope_ipos_to_prop_values,
                    None,
                    LiveServerEnvMockBuilder(),
                )
