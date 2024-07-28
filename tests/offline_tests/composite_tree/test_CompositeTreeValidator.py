from __future__ import annotations

from copy import deepcopy

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
# noinspection PyProtectedMember
from argrelay.composite_tree.CompositeTreeValidator import (
    _CompositeTreeValidator_zero_arg_node,
)
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_33_76_82_84 composite tree validator.
    """

    def test_CompositeTreeValidator_zero_arg_node(self):

        valid_composite_forest = {
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
        }

        def modify_to_have_zero_arg_node_at_tree_depth():
            local_composite_forest = deepcopy(valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_]["level_1_key_1"][sub_tree_]["level_2_key_1"]
            local_composite_node[node_type_] = CompositeNodeType.zero_arg_node.name
            # Remove unnecessary data for that type of node to avoid schema validation error:
            del local_composite_node[next_interp_]
            return local_composite_forest

        def modify_to_have_non_zero_arg_node_at_tree_root():
            local_composite_forest = deepcopy(valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_]["level_1_key_1"]
            local_composite_node[node_type_] = CompositeNodeType.tree_path_node.name
            # Remove unnecessary data for that type of node to avoid schema validation error:
            del local_composite_node[plugin_instance_id_]
            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(valid_composite_forest),
                None,
                f"valid tree",
            ),
            (
                line_no(),
                lambda: modify_to_have_zero_arg_node_at_tree_depth(),
                AssertionError,
                f"`{CompositeNodeType.zero_arg_node.name}` is not at tree root",
            ),
            (
                line_no(),
                lambda: modify_to_have_non_zero_arg_node_at_tree_root(),
                AssertionError,
                f"not a `{CompositeNodeType.zero_arg_node.name}` at tree root",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    dict_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                composite_forest: CompositeForest = composite_forest_desc.obj_from_input_dict(dict_supplier())

                composite_forest_validator = _CompositeTreeValidator_zero_arg_node(
                    composite_forest,
                )

                if expected_exception is None:
                    composite_forest_validator.walk_tree_roots()
                else:
                    with self.assertRaises(expected_exception) as exc_context:
                        composite_forest_validator.walk_tree_roots()
                    self.assertEqual(
                        expected_exception,
                        type(exc_context.exception),
                    )
