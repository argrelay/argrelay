from argrelay.enum_desc.CompType import CompType
from argrelay.test_helper import line_no
from argrelay.test_helper.LocalTestCase import LocalTestCase


class ThisTestCase(LocalTestCase):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_FS_71_87_33_52_help_hint(self):
        """
        Test FS_71_87_33_52 `help` command/func
        """

        test_cases = [
            (
                line_no(),
                "some_command help |",
                CompType.InvokeAction,
                None,
                {
                    0: {},  # help itself
                    1: {
                        # (goto, desc, list) x (host, service) external functions:
                        # TODO: (JSONPath?) Universal verifier: be able to verify arbitrary data on `EnvelopeContainer` (JSONPath?), not only assigned types to values.
                        # "found_count": 6
                    }
                },
                None,
                None,
                "Execute help with no args.",
            ),
            (
                line_no(),
                "some_command help interc|",
                CompType.PrefixShown,
                ["intercept"],
                {},
                None,
                None,
                "For `help` even `internal` functions are allowed.",
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
                    json_path_query,
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
