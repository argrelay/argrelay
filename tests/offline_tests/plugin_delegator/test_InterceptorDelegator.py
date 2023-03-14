from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.RunMode import RunMode
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.test_helper import line_no
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    def test_FS_88_66_66_73_intercept(self):
        """
        Test FS_88_66_66_73 `intercept` command/func
        """

        test_cases = [
            (
                line_no(),
                "some_command intercept |",
                RunMode.CompletionMode,
                CompType.PrefixShown,
                ["goto", "desc", "list"],
                None,
                None,
                "If `intercept` is already selected (which has `FunctionCategory` = `internal`), "
                "it should not be suggested during selection of `external` function.",
            ),
            (
                line_no(),
                "some_command intercept goto service s_b prod |",
                RunMode.CompletionMode,
                CompType.PrefixShown,
                ["qwer-pd-1", "qwer-pd-2"],
                None,
                None,
                "Completion continues to be driven by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command intercept hel|",
                RunMode.CompletionMode,
                CompType.PrefixShown,
                [],
                {},
                None,
                "For `intercept` only `external` functions are allowed - "
                "`help` is not suggested.",
            ),
            (
                line_no(),
                "some_command intercept got|",
                RunMode.CompletionMode,
                CompType.PrefixShown,
                ["goto"],
                {},
                None,
                "For `intercept` only `external` functions are allowed - "
                "`goto` is suggested.",
            ),
            (
                line_no(),
                "some_command intercept goto service s_b prod qwer-pd-2 |",
                RunMode.InvocationMode,
                CompType.InvokeAction,
                [],
                {
                    0: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("internal", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("intercept", ArgSource.InitValue),
                        GlobalArgType.ObjectSelector.name: AssignedValue("func", ArgSource.InitValue),
                    },
                    1: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("goto", ArgSource.ExplicitPosArg),
                        GlobalArgType.ObjectSelector.name: AssignedValue("service", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        ServiceArgType.ServiceName.name: AssignedValue("s_b", ArgSource.ExplicitPosArg),
                        ServiceArgType.CodeMaturity.name: AssignedValue("prod", ArgSource.ExplicitPosArg),
                        ServiceArgType.HostName.name: AssignedValue("qwer-pd-2", ArgSource.ExplicitPosArg),
                    },
                },
                None,
                "Invocation payload is provided by function selected via `goto` and `service`.",
            ),
            (
                line_no(),
                "some_command intercept intercept intercept intercept |",
                RunMode.InvocationMode,
                CompType.InvokeAction,
                [],
                {
                    0: {
                        GlobalArgType.FunctionCategory.name: AssignedValue("internal", ArgSource.InitValue),
                        GlobalArgType.ActionType.name: AssignedValue("intercept", ArgSource.InitValue),
                        GlobalArgType.ObjectSelector.name: AssignedValue("func", ArgSource.InitValue),
                    },
                    1: {
                        # Only `ArgSource.InitValue` as nothing else could be determined:
                        ReservedArgType.EnvelopeClass.name: AssignedValue(
                            ReservedEnvelopeClass.ClassFunction.name,
                            ArgSource.InitValue,
                        ),
                        GlobalArgType.FunctionCategory.name: AssignedValue("external", ArgSource.InitValue),
                    },
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
                    run_mode,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                    case_comment,
                ) = test_case

                self.verify_output(
                    "TD_63_37_05_36",  # demo
                    test_line,
                    run_mode,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    delegator_class,
                )
