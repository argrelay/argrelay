from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.RunMode import RunMode
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.runtime_data.AssignedValue import AssignedValue
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
                {},
                ErrorInvocator,
                "Execute help with no args.",
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
