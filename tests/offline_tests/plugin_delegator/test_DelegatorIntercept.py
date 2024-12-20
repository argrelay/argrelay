from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.plugin_delegator.DelegatorIntercept import (
    output_format_class_name,
    OutputFormat,
    output_format_prop_name,
    DelegatorIntercept,
)
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no, assert_test_module_name_embeds_prod_class_name
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_prod_class_name(DelegatorIntercept)

    def test_FS_88_66_66_73_intercept(self):
        """
        Test FS_88_66_66_73 `intercept` command/func
        """

        test_cases = [
            (
                line_no(),
                "some_command intercept |",
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
                "If `intercept` is already selected, it can be recursively suggested during selection of the function "
                "it tries to intercept, if jump tree is configured accordingly.",
            ),
            (
                line_no(),
                "some_command intercept goto |",
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
                "some_command intercept goto service s_b |",
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
            # TODO: TODO_10_06_46_37: list `arg_value` consumption stop options
            # (
            #     line_no(),
            #     "some_command intercept goto service s_b prod dc.77 |",
            #     CompType.PrefixShown,
            #     [
            #         "bbb",
            #         "xxx",
            #     ],
            #     None,
            #     None,
            #     "FS_13_51_07_97 list `arg_value`: singled out `data_envelope` with list `arg_value` "
            #     "will still show all options of the list "
            #     "because explicit selection of one of these values from singled out `data_envelop` "
            #     "may be used to affect behavior of the function.",
            # ),
            (
                line_no(),
                "some_command intercept goto service s_b prod |",
                CompType.PrefixShown,
                [
                    "bbb",
                    "sss",
                    "xxx",
                ],
                None,
                None,
                "FS_13_51_07_97 list `arg_value` from different `data_envelope`-s combine."
            ),
            (
                line_no(),
                "some_command intercept hel|",
                CompType.PrefixShown,
                [
                    "help",
                ],
                {},
                None,
                "For `intercept` any function is allowed - "
                "`help` is also suggested.",
            ),
            (
                line_no(),
                "some_command intercept got|",
                CompType.PrefixShown,
                [
                    "goto",
                ],
                {},
                None,
                "For `intercept` any function is allowed - "
                "`goto` is suggested.",
            ),
            (
                line_no(),
                "some_command intercept goto service s_b prod qwer-pd-2 |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
                    },
                    2: {
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
                    3: {
                        ServicePropName.service_name.name: AssignedValue("s_b", ValueSource.explicit_offered_arg),
                        ServicePropName.code_maturity.name: AssignedValue("prod", ValueSource.explicit_offered_arg),
                        ServicePropName.host_name.name: AssignedValue("qwer-pd-2", ValueSource.explicit_offered_arg),
                    },
                    4: {
                        ServicePropName.access_type.name: AssignedValue("ro", ValueSource.default_value),
                    },
                    5: None,
                },
                None,
                "Invocation payload is provided by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command intercept goto service s_b prod repr_format qwer-pd-2 |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.repr_format.name,
                            ValueSource.explicit_offered_arg,
                        ),
                    },
                    2: {
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
                    3: {
                        ServicePropName.service_name.name: AssignedValue("s_b", ValueSource.explicit_offered_arg),
                        ServicePropName.code_maturity.name: AssignedValue("prod", ValueSource.explicit_offered_arg),
                        ServicePropName.host_name.name: AssignedValue("qwer-pd-2", ValueSource.explicit_offered_arg),
                    },
                    4: {
                        ServicePropName.access_type.name: AssignedValue("ro", ValueSource.default_value),
                    },
                    5: None,
                },
                None,
                "Default `json_format` for `intercept` is overridden by `repr_format`.",
            ),
            (
                line_no(),
                "some_command intercept intercept intercept intercept |",
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
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
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
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    3: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
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
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    5: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
                    },
                    6: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.init_value,
                        ),
                    },
                    7: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
                    },
                    8: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            ReservedEnvelopeClass.class_function.name,
                            ValueSource.init_value,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue(
                            "some_command",
                            ValueSource.init_value,
                        ),
                    },
                    9: None,
                },
                None,
                "Prepend `intercept` by another `intercept` multiple times.",
            ),
            (
                line_no(),
                "some_command func_id_intercept_invocation intercept |",
                CompType.PrefixShown,
                [
                    # TODO: TODO_80_99_84_41 `intercept` has no suggestions if selected via `func_id`
                ],
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
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue(
                            "intercept",
                            ValueSource.explicit_offered_arg,
                        ),
                        ReservedPropName.func_id.name: AssignedValue(
                            SpecialFunc.func_id_intercept_invocation.name,
                            ValueSource.explicit_offered_arg,
                        )
                    },
                    1: {
                        ReservedPropName.envelope_class.name: AssignedValue(
                            output_format_class_name,
                            ValueSource.init_value,
                        ),
                        output_format_prop_name: AssignedValue(
                            OutputFormat.json_format.name,
                            ValueSource.default_value,
                        ),
                    },
                    2: None,
                },
                None,
                "TODO: TODO_80_99_84_41 `intercept` has no suggestions if selected via `func_id`",
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
