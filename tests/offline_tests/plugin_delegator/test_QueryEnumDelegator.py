from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_02_25_41_81_enum(self):
        """
        Test FS_02_25_41_81 `func_id_query_enum_items`.
        """

        test_cases = [
            (
                line_no(),
                "some_command enum |",
                CompType.PrefixShown,
                [
                    "config",
                    "desc",
                    "diff",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "meta",
                    "no_data",
                ],
                None,
                None,
                "If `enum` is already selected, it can be recursively suggested during selection of the function",
            ),
            (
                line_no(),
                "some_command enum goto |",
                CompType.PrefixShown,
                [
                    "host",
                    "repo",
                    "service",
                ],
                None,
                None,
                "Completion continues to select functions with `goto` path node in it.",
            ),
            (
                line_no(),
                "some_command enum goto service s_b |",
                CompType.PrefixShown,
                [
                    "dev",
                    "prod",
                    "qa",
                ],
                None,
                None,
                "Completion continues to be driven by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command enum goto service s_b prod qwer-pd-2 |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ArgSource.InitValue),
                    },
                    1: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServicePropName.service_name.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServicePropName.code_maturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServicePropName.host_name.name: AssignedValue("qwer-pd-2", ArgSource.ExplicitPosArg),
                    },
                    3: {
                        ServicePropName.access_type.name: AssignedValue("ro", ArgSource.DefaultValue),
                    },
                    4: None,
                },
                None,
                "Invocation payload is provided by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command enum enum enum enum |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ArgSource.InitValue),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ArgSource.InitValue),
                    },
                    2: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ArgSource.InitValue),
                    },
                    3: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ArgSource.InitValue),
                    },
                    4: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    },
                    5: None,
                },
                None,
                "Prepend `enum` by another `enum` multiple times.",
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

                self.verify_output_with_new_server_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    None,
                )
