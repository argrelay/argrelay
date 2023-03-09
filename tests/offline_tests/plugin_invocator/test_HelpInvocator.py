from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.test_helper import line_no
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    def test_FS_71_87_33_52_intercept(self):
        """
        Test FS_71_87_33_52 `help` command/func
        """

        test_cases = [
            (
                line_no(),
                "some_command help |",
                RunMode.InvocationMode,
                CompType.InvokeAction,
                [],
                {
                    0: {},  # help itself
                    1: {
                        # (goto, desc, list) x (host, service) external functions:
                        # TODO: Universal verifier: be able to verify arbitrary data on `EnvelopeContainer`, not only assigned types to values.
                        # "found_count": 6
                    }
                },
                None,
                "Execute help with no args.",
            ),
            (
                line_no(),
                "some_command help interc|",
                RunMode.CompletionMode,
                CompType.PrefixShown,
                ["intercept"],
                {},
                None,
                "For `help` even `internal` functions are allowed.",
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
                    invocator_class,
                    case_comment,
                ) = test_case

                self.verify_output(
                    "TD_63_37_05_36",  # demo
                    test_line,
                    run_mode,
                    comp_type,
                    expected_suggestions,
                    envelope_ipos_to_expected_assignments,
                    invocator_class,
                )
