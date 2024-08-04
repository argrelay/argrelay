from __future__ import annotations

from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker, surrogate_tree_leaf_, normalize_tree
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import surrogate_node_id_
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    # NOTE: It is irrelevant (and does not necessarily match the purpose of the test tree):
    composite_info_type: CompositeInfoType = CompositeInfoType.func_tree

    def test_normalize_tree(self):
        """
        See `normalize_tree`.
        """

        test_cases = [
            (
                line_no(),
                "leaf_1",
                {
                    surrogate_node_id_: "leaf_1",
                },
                f"Transform to add `{surrogate_node_id_}` for non-`dict`.",
            ),
            (
                line_no(),
                {
                    "l1_k1": {
                    },
                },
                {
                    "l1_k1": {
                    },
                },
                f"Ensure empty `dict` remain unchanged.",
            ),
            (
                line_no(),
                {
                    "leaf_1": surrogate_tree_leaf_,
                },
                {
                    "leaf_1": surrogate_tree_leaf_,
                },
                f"Ensure `{surrogate_tree_leaf_}` is NOT transformed into `dict`.",
            ),
            (
                line_no(),
                {
                    "l1_k1": {
                        surrogate_node_id_: {
                            "l3_k1": "some_value",
                        },
                    },
                },
                {
                    "l1_k1": {
                        "l3_k1": "some_value",
                    },
                },
                f"Transform to collapse `{surrogate_node_id_}`.",
            ),
            (
                line_no(),
                {
                    surrogate_node_id_: {
                        "l2_k1": "some_value",
                    },
                    "l1_k1": {
                    },
                },
                {
                    surrogate_node_id_: {
                        "l2_k1": "some_value",
                    },
                    "l1_k1": {
                    },
                },
                f"Ensure no collapse of `{surrogate_node_id_}` if there are other nodes.",
            ),
            (
                line_no(),
                {
                    "l1_k1": "some_value",
                    "l1_k2": "some_value",
                },
                {
                    "l1_k1": "some_value",
                    "l1_k2": "some_value",
                },
                f"Ensure keep normal `dict` unchanged.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    input_tree,
                    expected_output_tree,
                    case_comment,
                ) = test_case

                actual_output_tree = normalize_tree(input_tree)

                self.assertEqual(
                    expected_output_tree,
                    actual_output_tree,
                )

    def test_build_str_leaves_paths(self):
        """
        Test to build map (`dict`) of `str` leaf key to its tree paths.
        """

        test_cases = [
            (
                line_no(),
                {},
                None,
                {},
                "All empty.",
            ),
            (
                line_no(),
                surrogate_tree_leaf_,
                f"{self.composite_info_type}: tree path `[]` must contain at least one step to use leaf `{surrogate_tree_leaf_}`",
                None,
                f"Single leaf named as `{surrogate_tree_leaf_}`",
            ),
            (
                line_no(),
                "leaf_1",
                None,
                {
                    "leaf_1": [
                        [
                        ],
                    ],
                },
                "Single leaf.",
            ),
            (
                line_no(),
                {
                    "leaf_1": surrogate_tree_leaf_,
                },
                None,
                {
                    "leaf_1": [
                        [
                        ],
                    ],
                },
                f"Dict with `{surrogate_tree_leaf_}` leaf.",
            ),
            (
                line_no(),
                {
                    "l1_1": "leaf_1",
                },
                None,
                {
                    "leaf_1": [
                        [
                            "l1_1",
                        ],
                    ],
                },
                "Primitive tree.",
            ),
            (
                line_no(),
                {
                    "l1_1": None,
                },
                f"{self.composite_info_type}: tree path `['l1_1']` leaf type `NoneType` is neither `str` nor `dict`",
                None,
                "Wrong tree node type",
            ),
            (
                line_no(),
                {
                    "l1_1": "leaf_1",
                    "l1_2": {
                        "l2_1": {
                            "l3_1": "leaf_2",
                        },
                        "l2_2": "leaf_1",
                    },
                },
                None,
                {
                    "leaf_1": [
                        [
                            "l1_1",
                        ],
                        [
                            "l1_2",
                            "l2_2",
                        ],
                    ],
                    "leaf_2": [
                        [
                            "l1_2",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                },
                "Duplicate leaf id.",
            ),
            (
                line_no(),
                {
                    "l1_1": "leaf_1",
                    surrogate_node_id_: {
                        "l2_1": {
                            "l3_1": "leaf_2",
                        },
                        surrogate_node_id_: "leaf_1",
                    },
                },
                None,
                {
                    "leaf_1": [
                        [
                            "l1_1",
                        ],
                        [
                        ],
                    ],
                    "leaf_2": [
                        [
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                },
                f"Using `{surrogate_node_id_}` as node id.",
            ),
            (
                line_no(),
                {
                    "l1_1": "leaf_1",
                    "l1_2": {
                        "l2_1": {
                            "l3_1": "leaf_2",
                        },
                        "l2_2": "leaf_3",
                    },
                    "l1_3": {
                        "l2_1": {
                            "l3_1": "leaf_4",
                        },
                        "l2_2": "leaf_5",
                    },
                },
                None,
                {
                    "leaf_1": [
                        [
                            "l1_1",
                        ],
                    ],
                    "leaf_2": [
                        [
                            "l1_2",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    "leaf_3": [
                        [
                            "l1_2",
                            "l2_2",
                        ],
                    ],
                    "leaf_4": [
                        [
                            "l1_3",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    "leaf_5": [
                        [
                            "l1_3",
                            "l2_2",
                        ],
                    ],
                },
                "Bigger tree.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    input_tree,
                    expected_exception,
                    expected_leaf_paths,
                    case_comment,
                ) = test_case

                tree_walker: DictTreeWalker = DictTreeWalker(
                    self.composite_info_type,
                    input_tree,
                )

                if expected_exception is None:
                    actual_leaf_paths: dict[str, list[list[str]]] = tree_walker.build_str_leaves_paths()
                    self.assertEqual(
                        expected_leaf_paths,
                        actual_leaf_paths,
                    )
                else:
                    self.assertIsNone(
                        expected_leaf_paths,
                        self.confusing_result_presence_msg,
                    )
                    with self.assertRaises(Exception) as exc_context:
                        tree_walker.build_str_leaves_paths()
                    self.assertEqual(
                        expected_exception,
                        exc_context.exception.args[0],
                    )

    def test_build_tuple_leaves_paths(self):
        """
        Test to build map (`dict`) of `tuple`/`list` leaf key to its tree paths.
        """

        test_cases = [
            (
                line_no(),
                {},
                None,
                {},
                "All empty.",
            ),
            (
                line_no(),
                "unexpected_str",
                f"{self.composite_info_type}: tree path `[]` leaf type `str` is neither `list` nor `dict`",
                None,
                f"Single leaf of unexpected `str` type.",
            ),
            (
                line_no(),
                [
                    "path_step_1",
                    "path_step_2",
                ],
                None,
                {
                    (
                        "path_step_1",
                        "path_step_2",
                    ): [
                        [
                        ],
                    ],
                },
                "Single leaf.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                    ],
                },
                None,
                {
                    (
                    ): [
                        [
                            "l1_1",
                        ],
                    ],
                },
                "Empty list leaf",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                },
                None,
                {
                    (
                        "path_step_1",
                        "path_step_2",
                    ): [
                        [
                            "l1_1",
                        ],
                    ],
                },
                "Primitive tree.",
            ),
            (
                line_no(),
                {
                    "l1_1": None,
                },
                f"{self.composite_info_type}: tree path `['l1_1']` leaf type `NoneType` is neither `list` nor `dict`",
                None,
                "Wrong tree node type",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    "l1_2": {
                        "l2_1": {
                            "l3_1": [
                                "path_step_1",
                                "path_step_2",
                            ],
                        },
                        surrogate_node_id_: [
                            "path_step_1",
                            "path_step_2",
                            "path_step_3",
                        ],
                    },
                },
                None,
                {
                    (
                        "path_step_1",
                        "path_step_2",
                    ): [
                        [
                            "l1_1",
                        ],
                        [
                            "l1_2",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    (
                        "path_step_1",
                        "path_step_2",
                        "path_step_3",
                    ): [
                        [
                            "l1_2",
                        ],
                    ],
                },
                f"Using `{surrogate_node_id_}` as node id.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    "l1_2": {
                        "l2_1": {
                            "l3_1": [
                                "path_step_1",
                                "path_step_2",
                            ],
                        },
                        "l2_2": [
                            "path_step_1",
                            "path_step_2",
                            "path_step_3",
                        ],
                    },
                },
                None,
                {
                    (
                        "path_step_1",
                        "path_step_2",
                    ): [
                        [
                            "l1_1",
                        ],
                        [
                            "l1_2",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    (
                        "path_step_1",
                        "path_step_2",
                        "path_step_3",
                    ): [
                        [
                            "l1_2",
                            "l2_2",
                        ],
                    ],
                },
                "Duplicate leaf id.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    "l1_2": {
                        "l2_1": {
                            "l3_1": [
                                "path_step_3",
                                "path_step_4",
                            ],
                        },
                        "l2_2": [
                            "path_step_5",
                        ],
                    },
                    "l1_3": {
                        "l2_1": {
                            "l3_1": [
                            ],
                        },
                        "l2_2": [
                            "path_step_6",
                            "path_step_7",
                            "path_step_8",
                            "path_step_9",
                        ],
                    },
                },
                None,
                {
                    (
                        "path_step_1",
                        "path_step_2",
                    ): [
                        [
                            "l1_1",
                        ],
                    ],
                    (
                        "path_step_3",
                        "path_step_4",
                    ): [
                        [
                            "l1_2",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    (
                        "path_step_5",
                    ): [
                        [
                            "l1_2",
                            "l2_2",
                        ],
                    ],
                    (
                    ): [
                        [
                            "l1_3",
                            "l2_1",
                            "l3_1",
                        ],
                    ],
                    (
                        "path_step_6",
                        "path_step_7",
                        "path_step_8",
                        "path_step_9",
                    ): [
                        [
                            "l1_3",
                            "l2_2",
                        ],
                    ],
                },
                "Bigger tree.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    input_tree,
                    expected_exception,
                    expected_leaf_paths,
                    case_comment,
                ) = test_case

                tree_walker: DictTreeWalker = DictTreeWalker(
                    self.composite_info_type,
                    input_tree,
                )

                if expected_exception is None:
                    actual_leaf_paths: dict[tuple[str, ...], list[list[str]]] = tree_walker.build_tuple_leaves_paths()
                    self.assertEqual(
                        expected_leaf_paths,
                        actual_leaf_paths,
                    )
                else:
                    self.assertIsNone(
                        expected_leaf_paths,
                        self.confusing_result_presence_msg,
                    )
                    with self.assertRaises(Exception) as exc_context:
                        tree_walker.build_tuple_leaves_paths()
                    self.assertEqual(
                        expected_exception,
                        exc_context.exception.args[0],
                    )

    def test_build_paths_to_paths(self):
        """
        Test mapping each path in the tree into path from the leaf (`list` in tree becomes `tuple` in map).
        """

        test_cases = [
            (
                line_no(),
                {},
                None,
                {},
                "All empty.",
            ),
            (
                line_no(),
                "unexpected_str",
                f"{self.composite_info_type}: tree path `[]` leaf type `str` is neither `list` nor `dict`",
                None,
                f"Single leaf of unexpected `str` type.",
            ),
            (
                line_no(),
                [
                    "path_step_1",
                    "path_step_2",
                ],
                None,
                {
                    (
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                },
                "Single leaf.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                    ],
                },
                None,
                {
                    (
                        "l1_1",
                    ): (
                    ),
                },
                "Empty list leaf",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                },
                None,
                {
                    (
                        "l1_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                },
                "Primitive tree.",
            ),
            (
                line_no(),
                {
                    "l1_1": None,
                },
                f"{self.composite_info_type}: tree path `['l1_1']` leaf type `NoneType` is neither `list` nor `dict`",
                None,
                "Wrong tree node type",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    surrogate_node_id_: {
                        "l2_1": {
                            "l3_1": [
                                "path_step_1",
                                "path_step_2",
                            ],
                        },
                        surrogate_node_id_: [
                            "path_step_1",
                            "path_step_2",
                            "path_step_3",
                        ],
                    },
                },
                None,
                {
                    (
                        "l1_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                    (
                        "l2_1",
                        "l3_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                    (
                    ): (
                        "path_step_1",
                        "path_step_2",
                        "path_step_3",
                    ),
                },
                f"Using `{surrogate_node_id_}` as node id.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    "l1_2": {
                        "l2_1": {
                            "l3_1": [
                                "path_step_1",
                                "path_step_2",
                            ],
                        },
                        "l2_2": [
                            "path_step_1",
                            "path_step_2",
                            "path_step_3",
                        ],
                    },
                },
                None,
                {
                    (
                        "l1_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                    (
                        "l1_2",
                        "l2_1",
                        "l3_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                    (
                        "l1_2",
                        "l2_2",
                    ): (
                        "path_step_1",
                        "path_step_2",
                        "path_step_3",
                    ),
                },
                "Duplicate leaf id.",
            ),
            (
                line_no(),
                {
                    "l1_1": [
                        "path_step_1",
                        "path_step_2",
                    ],
                    "l1_2": {
                        "l2_1": {
                            "l3_1": [
                                "path_step_3",
                                "path_step_4",
                            ],
                        },
                        "l2_2": [
                            "path_step_5",
                        ],
                    },
                    "l1_3": {
                        "l2_1": {
                            "l3_1": [
                            ],
                        },
                        "l2_2": [
                            "path_step_6",
                            "path_step_7",
                            "path_step_8",
                            "path_step_9",
                        ],
                    },
                },
                None,
                {
                    (
                        "l1_1",
                    ): (
                        "path_step_1",
                        "path_step_2",
                    ),
                    (
                        "l1_2",
                        "l2_1",
                        "l3_1",
                    ): (
                        "path_step_3",
                        "path_step_4",
                    ),
                    (
                        "l1_2",
                        "l2_2",
                    ): (
                        "path_step_5",
                    ),
                    (
                        "l1_3",
                        "l2_1",
                        "l3_1",
                    ): (
                    ),
                    (
                        "l1_3",
                        "l2_2",
                    ): (
                        "path_step_6",
                        "path_step_7",
                        "path_step_8",
                        "path_step_9",
                    ),
                },
                "Bigger tree.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    input_tree,
                    expected_exception,
                    expected_leaf_paths,
                    case_comment,
                ) = test_case

                tree_walker: DictTreeWalker = DictTreeWalker(
                    self.composite_info_type,
                    input_tree,
                )

                if expected_exception is None:
                    actual_leaf_paths: dict[tuple[str, ...], tuple[str, ...]] = tree_walker.build_paths_to_paths()
                    self.assertEqual(
                        expected_leaf_paths,
                        actual_leaf_paths,
                    )
                else:
                    self.assertIsNone(
                        expected_leaf_paths,
                        self.confusing_result_presence_msg,
                    )
                    with self.assertRaises(Exception) as exc_context:
                        tree_walker.build_paths_to_paths()
                    self.assertEqual(
                        expected_exception,
                        exc_context.exception.args[0],
                    )
