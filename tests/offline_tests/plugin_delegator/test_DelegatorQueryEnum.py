from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_delegator.DelegatorQueryEnum import DelegatorQueryEnum
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no, assert_test_module_name_embeds_prod_class_name
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorQueryEnum)

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
                    "data",
                    "desc",
                    "diff",
                    "duplicates",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "no_data",
                    "ssh",
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "enum",
                            ValueSource.init_value,
                        ),
                    },
                    1: {
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
                    2: {
                        ServicePropName.service_name.name: AssignedValue("s_b", ValueSource.explicit_offered_arg),
                        ServicePropName.code_maturity.name: AssignedValue("prod", ValueSource.explicit_offered_arg),
                        ServicePropName.host_name.name: AssignedValue("qwer-pd-2", ValueSource.explicit_offered_arg),
                    },
                    3: {
                        ServicePropName.access_type.name: AssignedValue("ro", ValueSource.default_value),
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
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ValueSource.init_value),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ValueSource.init_value),
                    },
                    2: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ValueSource.init_value),
                    },
                    3: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("enum", ValueSource.init_value),
                    },
                    4: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
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
