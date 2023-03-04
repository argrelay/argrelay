from unittest import TestCase

from argrelay.plugin_interp.TreePathInterp import fetch_tree_node
from argrelay.test_helper import line_no


class ThisTestCase(TestCase):

    # TODO: clean this after replacing with TreePathInterp test instead:
    def test_fetch_tree_node(self):
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

                self.assertEquals(
                    expected_result,
                    fetch_tree_node(tree_dict, node_coord),
                )
