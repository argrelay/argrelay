from __future__ import annotations

from argrelay.composite_tree.CompositeForest import CompositeForest
from argrelay.composite_tree.CompositeForestSchema import composite_forest_desc, tree_roots_
from argrelay.composite_tree.CompositeNodeSchema import (
    node_type_,
    sub_tree_,
    plugin_instance_id_,
    func_id_,
    next_interp_,
    jump_path_,
)
from argrelay.composite_tree.CompositeNodeType import CompositeNodeType
from argrelay.composite_tree.CompositeTreeValidator import validate_composite_tree
from argrelay.composite_tree.CompositeTreeWalker import CompositeTreeWalkerPrinter
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_33_76_82_84 composite tree walker.
    """

    def test_composite_tree_schema_load(self):
        """
        Load simplified FS_33_76_82_84 composite trees to test its schema.
        """
        test_cases = [
            (
                line_no(),
                {
                    tree_roots_: {
                        "level_1_key_1": {
                            node_type_: CompositeNodeType.zero_arg_node.name,
                            plugin_instance_id_: "some_plugin_instance_id",
                            sub_tree_: {
                                "level_2_key_1": {
                                    node_type_: CompositeNodeType.interp_tree_node.name,
                                    plugin_instance_id_: "some_plugin_instance_id",
                                    next_interp_: {
                                        jump_path_: [],
                                        plugin_instance_id_: "some_plugin_instance_id",
                                    },
                                    sub_tree_: {
                                        "level_3_key_1": {
                                            node_type_: CompositeNodeType.tree_path_node.name,
                                            sub_tree_: {
                                                "level_4_key_1": {
                                                    node_type_: CompositeNodeType.func_tree_node.name,
                                                    func_id_: "some_func_id",
                                                    sub_tree_: None,
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "level_1_key_2": {
                            node_type_: CompositeNodeType.zero_arg_node.name,
                            plugin_instance_id_: "some_plugin_instance_id",
                            sub_tree_: {
                                "level_2_key_2": {
                                    node_type_: CompositeNodeType.interp_tree_node.name,
                                    plugin_instance_id_: "some_plugin_instance_id",
                                    next_interp_: {
                                        jump_path_: [],
                                        plugin_instance_id_: "some_plugin_instance_id",
                                    },
                                    sub_tree_: {
                                        "level_3_key_2": {
                                            node_type_: CompositeNodeType.tree_path_node.name,
                                            sub_tree_: {
                                                "level_4_key_2": {
                                                    node_type_: CompositeNodeType.func_tree_node.name,
                                                    func_id_: "some_func_id",
                                                    sub_tree_: None,
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                f"Complete tree with all `{CompositeNodeType.__name__}`-s",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    given_dict,
                    case_comment,
                ) = test_case

                composite_forest: CompositeForest = composite_forest_desc.obj_from_input_dict(given_dict)
                assert composite_forest is not None

                composite_forest_printer = CompositeTreeWalkerPrinter(
                    composite_forest,
                )
                composite_forest_printer.walk_tree_roots()

                # Ensure that the tree is realistic:
                validate_composite_tree(
                    composite_forest,
                )
