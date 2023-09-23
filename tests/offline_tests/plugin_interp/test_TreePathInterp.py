from argrelay.enum_desc.CompType import CompType
from argrelay.plugin_interp.TreePathInterp import fetch_tree_node
from argrelay.test_helper import line_no
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    def test_FS_01_89_09_24_fetch_tree_node(self):
        """
        Tests part of FS_01_89_09_24
        """
        empty_tree = {}
        full_tree = {
            "a": {
                "x": {
                    "1": "bingo",
                },
                "y": {
                },
            },
            "b": {
            },
            "c": None,
        }
        test_cases = [
            (line_no(), empty_tree, [], empty_tree),
            (line_no(), empty_tree, ["whatever"], None),
            (line_no(), full_tree, ["a", "x", "1"], "bingo"),
            (line_no(), full_tree, ["c", "x", "1"], None),
            (line_no(), full_tree, ["c"], None),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    tree_dict,
                    node_coord,
                    expected_result,
                ) = test_case

                self.assertEqual(
                    expected_result,
                    fetch_tree_node(tree_dict, node_coord),
                )

    def test_FS_01_89_09_24_tree(self):
        """
        Test arg values suggestion with FS_01_89_09_24 # tree
        """

        test_cases = [
            (
                line_no(),
                "some_command |",
                CompType.PrefixShown,
                ['help', 'intercept', 'subtree', 'goto', 'desc', 'list'],
                {},
                None,
                "FS_01_89_09_24: `intercept` and `help` are suggested via tree search mechanism "
                "rather than data search.",
            ),
            (
                line_no(),
                "some_command inter|",
                CompType.PrefixShown,
                ["intercept"],
                {},
                None,
                "FS_01_89_09_24: prefix suggestion also works for `intercept` (help is filtered out).",
            ),
            (
                line_no(),
                "some_command host qa upstream amer qw goto ro s_c green rtyu-qu |",
                CompType.PrefixShown,
                ["amer", "emea"],
                {},
                None,
                "FS_01_89_09_24: Even if `intercept` is not specified in the beginning, "
                "`TreePathInterp` does not suggest it",
            ),
            (
                line_no(),
                "some_command | host qa upstream amer qw goto ro s_c green rtyu-qu",
                CompType.PrefixShown,
                # TODO: FS_23_62_89_43: This can be fixed to take into account cursor position
                #                       and suggest not only missing args for already populated command line,
                #                       but also internal functions available for that position (e.g. `intercept`)
                ["amer", "emea"],
                {},
                None,
                "FS_01_89_09_24: Suggest functions available for this position "
                "even if the rest of the command line is populated.",
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
                    "TD_76_09_29_31",  # overlapped
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    delegator_class,
                    None,
                )
