from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_interp.FuncTreeInterpFactory import func_envelope_path_step_prop_name
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

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
                    "desc",
                    "echo",
                    "enum",
                    "goto",
                    "help",
                    "intercept",
                    "list",
                    "subtree",
                ],
                None,
                None,
                "If `intercept` is already selected, it can be recursively suggested during selection of the function "
                "it tries to intercept, if jump tree is configured accordingly.",
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
            #     # TODO: FS_13_51_07_97 list arg value: the `data_envelope` is singled out, but list arg values should still be suggested:
            #     "FS_13_51_07_97 list arg value: singled out `data_envelope` with list arg value "
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
                "FS_13_51_07_97 list arg value from different `data_envelope`-s combine."
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
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("intercept", ArgSource.InitValue),
                    },
                    1: {
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("goto", ArgSource.ExplicitPosArg),
                        f"{func_envelope_path_step_prop_name(2)}": AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServiceArgType.ServiceName.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.HostName.name: AssignedValue("qwer-pd-2", ArgSource.ExplicitPosArg),
                    },
                    3: {
                        ServiceArgType.AccessType.name: AssignedValue("ro", ArgSource.DefaultValue),
                    },
                    4: None,
                },
                None,
                "Invocation payload is provided by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command intercept intercept intercept intercept |",
                CompType.InvokeAction,
                None,
                {
                    0: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("intercept", ArgSource.InitValue),
                    },
                    1: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("intercept", ArgSource.InitValue),
                    },
                    2: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("intercept", ArgSource.InitValue),
                    },
                    3: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                        f"{func_envelope_path_step_prop_name(1)}": AssignedValue("intercept", ArgSource.InitValue),
                    },
                    4: {
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        f"{func_envelope_path_step_prop_name(0)}": AssignedValue("some_command", ArgSource.InitValue),
                    },
                    5: None,
                },
                None,
                # TODO: This only captures the behavior of such command line.
                #       Currently, it cannot select another `intercept` function
                #       because `ArgSource.InitValue` is set to `external` subsequently.
                "Prepend `intercept` by another `intercept` multiple times.",
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
