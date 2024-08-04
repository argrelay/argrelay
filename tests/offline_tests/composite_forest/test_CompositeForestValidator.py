from __future__ import annotations

from copy import deepcopy
from typing import Callable

from argrelay.composite_forest.CompositeForest import CompositeForest
from argrelay.composite_forest.CompositeForestSchema import composite_forest_desc, tree_roots_
# noinspection PyProtectedMember
from argrelay.composite_forest.CompositeForestValidator import (
    CompositeForestValidatorAbstract,
    _CompositeForestValidator_zero_arg_node_is_root,
    _CompositeForestValidator_func_tree_node_is_leaf,
    _CompositeForestValidator_zero_arg_node_with_interp_tree_node,
    _CompositeForestValidator_interp_tree_node_with_func_tree_node,
    _CompositeForestValidator_plugin_instance_id,
    validate_composite_forest,
)
from argrelay.composite_forest.CompositeForestWalker import CompositeForestWalkerPrinter
from argrelay.composite_forest.CompositeNodeSchema import (
    node_type_,
    sub_tree_,
    plugin_instance_id_,
    func_id_,
)
from argrelay.composite_forest.CompositeNodeType import CompositeNodeType
from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
from argrelay.plugin_loader.NoopLoader import NoopLoader
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_interp.FuncEnvelopeSchema import func_id_some_func_
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, plugin_instance_entries_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests for FS_33_76_82_84 composite forest validator.
    """

    server_config = None

    interp_tree_plugin_id = None
    func_tree_plugin_id = None
    loader_plugin_id = None

    @classmethod
    def setUpClass(cls):
        LocalTestClass.setUpClass()

        # Use server config but it should not matter:
        cls.server_config = server_config_desc.obj_from_default_file()

        cls.interp_tree_plugin_id = f"{InterpTreeInterpFactory.__name__}.default"
        cls.func_tree_plugin_id = f"{FuncTreeInterpFactory.__name__}.default"
        cls.loader_plugin_id = f"{NoopLoader.__name__}.default"

        cls.plugin_instances = {
            cls.interp_tree_plugin_id: InterpTreeInterpFactory(
                server_config = cls.server_config,
                plugin_instance_id = cls.interp_tree_plugin_id,
                plugin_config_dict = plugin_config_desc.dict_from_default_file()[
                    plugin_instance_entries_
                ][
                    cls.interp_tree_plugin_id
                ][
                    plugin_config_
                ]
            ),
            cls.func_tree_plugin_id: FuncTreeInterpFactory(
                server_config = cls.server_config,
                plugin_instance_id = cls.func_tree_plugin_id,
                plugin_config_dict = plugin_config_desc.dict_from_default_file()[
                    plugin_instance_entries_
                ][
                    cls.func_tree_plugin_id
                ][
                    plugin_config_
                ]
            ),
            cls.loader_plugin_id: NoopLoader(
                server_config = cls.server_config,
                plugin_instance_id = cls.func_tree_plugin_id,
                plugin_config_dict = {},
            ),
        }

        cls.valid_composite_forest = {
            tree_roots_: {
                "level_1_key_1": {
                    node_type_: CompositeNodeType.zero_arg_node.name,
                    plugin_instance_id_: cls.interp_tree_plugin_id,
                    sub_tree_: {
                        "level_2_key_1": {
                            node_type_: CompositeNodeType.interp_tree_node.name,
                            plugin_instance_id_: cls.func_tree_plugin_id,
                            sub_tree_: {
                                "level_3_key_1": {
                                    node_type_: CompositeNodeType.tree_path_node.name,
                                    sub_tree_: {
                                        "level_4_key_1": {
                                            node_type_: CompositeNodeType.func_tree_node.name,
                                            func_id_: func_id_some_func_,
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
                    plugin_instance_id_: cls.interp_tree_plugin_id,
                    sub_tree_: {
                        "level_2_key_2": {
                            node_type_: CompositeNodeType.interp_tree_node.name,
                            plugin_instance_id_: cls.func_tree_plugin_id,
                            sub_tree_: {
                                "level_3_key_2": {
                                    node_type_: CompositeNodeType.tree_path_node.name,
                                    sub_tree_: {
                                        "level_4_key_2": {
                                            node_type_: CompositeNodeType.func_tree_node.name,
                                            func_id_: func_id_some_func_,
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

    # noinspection PyMethodMayBeStatic
    def test_composite_forest_schema_load_and_full_validation(self):
        """
        Load simplified FS_33_76_82_84 composite forest to test its schema load and full validation.
        """

        composite_forest: CompositeForest = composite_forest_desc.obj_from_input_dict(self.valid_composite_forest)
        assert composite_forest is not None

        composite_forest_printer = CompositeForestWalkerPrinter(
            composite_forest,
        )
        composite_forest_printer.walk_tree_roots()

        # Ensure that the tree is realistic:
        validate_composite_forest(
            composite_forest,
            self.plugin_instances,
        )

    def test_CompositeForestValidator_zero_arg_node_is_root(self):

        def modify_to_have_zero_arg_node_at_tree_depth():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_]["level_1_key_1"][sub_tree_]["level_2_key_1"]
            local_composite_node[node_type_] = CompositeNodeType.zero_arg_node.name

            return local_composite_forest

        def modify_to_have_non_zero_arg_node_at_tree_root():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_]["level_1_key_1"]
            local_composite_node[node_type_] = CompositeNodeType.tree_path_node.name

            # Adjust data to avoid schema validation error:
            del local_composite_node[plugin_instance_id_]

            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(self.valid_composite_forest),
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
                    composite_forest_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                self._assert_test_case(
                    composite_forest_supplier,
                    _CompositeForestValidator_zero_arg_node_is_root,
                    self.plugin_instances,
                    expected_exception,
                )

    def test_CompositeForestValidator_func_tree_node_is_leaf(self):

        def modify_to_have_non_leaf_func_tree_node():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ][sub_tree_][
                "level_3_key_2"
            ][sub_tree_][
                "level_4_key_2"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.func_tree_node.name

            # Adjust data to avoid schema validation error:
            local_composite_node[sub_tree_] = {
                "level_5_key_2": {
                    node_type_: CompositeNodeType.tree_path_node.name,
                    sub_tree_: None,
                }
            }

            return local_composite_forest

        def modify_to_have_non_func_tree_node_at_tree_leaf():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ][sub_tree_][
                "level_3_key_2"
            ][sub_tree_][
                "level_4_key_2"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.func_tree_node.name
            local_composite_node[node_type_] = CompositeNodeType.tree_path_node.name

            # Adjust data to avoid schema validation error:
            del local_composite_node[func_id_]

            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(self.valid_composite_forest),
                None,
                f"valid tree",
            ),
            (
                line_no(),
                lambda: modify_to_have_non_leaf_func_tree_node(),
                AssertionError,
                f"`{CompositeNodeType.func_tree_node.name}` is not leaf",
            ),
            (
                line_no(),
                lambda: modify_to_have_non_func_tree_node_at_tree_leaf(),
                AssertionError,
                f"not a `{CompositeNodeType.func_tree_node.name}` at tree leaf",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    composite_forest_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                self._assert_test_case(
                    composite_forest_supplier,
                    _CompositeForestValidator_func_tree_node_is_leaf,
                    self.plugin_instances,
                    expected_exception,
                )

    def test_CompositeForestValidator_zero_arg_node_with_interp_tree_node(self):

        def modify_parent_to_non_zero_arg_node():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_1"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.zero_arg_node.name
            local_composite_node[node_type_] = CompositeNodeType.func_tree_node.name

            # Adjust data to avoid schema validation error:
            local_composite_node[func_id_] = "some_func_id"
            del local_composite_node[plugin_instance_id_]

            return local_composite_forest

        def modify_child_to_non_interp_tree_node():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.interp_tree_node.name
            local_composite_node[node_type_] = CompositeNodeType.tree_path_node.name

            # Adjust data to avoid schema validation error:
            del local_composite_node[plugin_instance_id_]

            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(self.valid_composite_forest),
                None,
                f"valid tree",
            ),
            (
                line_no(),
                lambda: modify_parent_to_non_zero_arg_node(),
                AssertionError,
                f"parent is not `{CompositeNodeType.zero_arg_node.name}`",
            ),
            (
                line_no(),
                lambda: modify_child_to_non_interp_tree_node(),
                AssertionError,
                f"child is not `{CompositeNodeType.interp_tree_node.name}`",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    composite_forest_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                self._assert_test_case(
                    composite_forest_supplier,
                    _CompositeForestValidator_zero_arg_node_with_interp_tree_node,
                    self.plugin_instances,
                    expected_exception,
                )

    def test_CompositeForestValidator_interp_tree_node_with_func_tree_node(self):

        def modify_parent_to_non_interp_tree_node():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_1"
            ][sub_tree_][
                "level_2_key_1"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.interp_tree_node.name
            local_composite_node[node_type_] = CompositeNodeType.zero_arg_node.name

            return local_composite_forest

        def modify_child_to_non_func_tree_node():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ][sub_tree_][
                "level_3_key_2"
            ][sub_tree_][
                "level_4_key_2"
            ]
            assert local_composite_node[node_type_] == CompositeNodeType.func_tree_node.name
            local_composite_node[node_type_] = CompositeNodeType.interp_tree_node.name

            # Adjust data to avoid schema validation error:
            del local_composite_node[func_id_]
            local_composite_node[plugin_instance_id_] = self.func_tree_plugin_id

            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(self.valid_composite_forest),
                None,
                f"valid tree",
            ),
            (
                line_no(),
                lambda: modify_parent_to_non_interp_tree_node(),
                AssertionError,
                f"parent is not `{CompositeNodeType.interp_tree_node.name}`",
            ),
            (
                line_no(),
                lambda: modify_child_to_non_func_tree_node(),
                AssertionError,
                f"child is not `{CompositeNodeType.interp_tree_node.name}`",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    composite_forest_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                self._assert_test_case(
                    composite_forest_supplier,
                    _CompositeForestValidator_interp_tree_node_with_func_tree_node,
                    self.plugin_instances,
                    expected_exception,
                )

    def test_CompositeForestValidator_plugin_instance_id(self):

        def modify_zero_arg_node_tree_node_to_use_non_interp_factory_plugin():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_1"
            ]
            assert local_composite_node[plugin_instance_id_] == self.interp_tree_plugin_id

            local_composite_node[plugin_instance_id_] = self.loader_plugin_id

            return local_composite_forest

        def modify_zero_arg_node_tree_node_to_use_non_InterpTreeInterpFactory():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_1"
            ]
            assert local_composite_node[plugin_instance_id_] == self.interp_tree_plugin_id

            local_composite_node[plugin_instance_id_] = self.func_tree_plugin_id

            return local_composite_forest

        def modify_interp_tree_node_to_use_non_interp_factory_plugin():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ]
            assert local_composite_node[plugin_instance_id_] == self.func_tree_plugin_id

            local_composite_node[plugin_instance_id_] = self.loader_plugin_id

            return local_composite_forest

        def modify_interp_tree_node_to_use_non_FuncTreeInterpFactory():
            local_composite_forest = deepcopy(self.valid_composite_forest)
            local_composite_node = local_composite_forest[tree_roots_][
                "level_1_key_2"
            ][sub_tree_][
                "level_2_key_2"
            ]
            assert local_composite_node[plugin_instance_id_] == self.func_tree_plugin_id

            local_composite_node[plugin_instance_id_] = self.interp_tree_plugin_id

            return local_composite_forest

        test_cases = [
            (
                line_no(),
                lambda: deepcopy(self.valid_composite_forest),
                None,
                f"valid tree",
            ),
            (
                line_no(),
                lambda: modify_zero_arg_node_tree_node_to_use_non_interp_factory_plugin(),
                AssertionError,
                f"not a `{PluginType.InterpFactoryPlugin.name}` for {CompositeNodeType.zero_arg_node.name}",
            ),
            (
                line_no(),
                lambda: modify_zero_arg_node_tree_node_to_use_non_InterpTreeInterpFactory(),
                AssertionError,
                f"not a `{InterpTreeInterpFactory.__name__}` for {CompositeNodeType.zero_arg_node.name}",
            ),
            (
                line_no(),
                lambda: modify_interp_tree_node_to_use_non_interp_factory_plugin(),
                AssertionError,
                f"not a `{PluginType.InterpFactoryPlugin.name}` for {CompositeNodeType.interp_tree_node.name}",
            ),
            (
                line_no(),
                lambda: modify_interp_tree_node_to_use_non_FuncTreeInterpFactory(),
                AssertionError,
                f"not a `{FuncTreeInterpFactory.__name__}` for {CompositeNodeType.interp_tree_node.name}",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    composite_forest_supplier,
                    expected_exception,
                    case_comment,
                ) = test_case

                self._assert_test_case(
                    composite_forest_supplier,
                    _CompositeForestValidator_plugin_instance_id,
                    self.plugin_instances,
                    expected_exception,
                )

    def _assert_test_case(
        self,
        composite_forest_supplier: Callable[[], dict],
        validator_ctor: Callable[
            [
                CompositeForest,
                dict[str, "AbstractPluginServer"],
            ],
            CompositeForestValidatorAbstract,
        ],
        plugin_instances: dict[str, "AbstractPluginServer"],
        expected_exception,
    ):

        composite_forest: CompositeForest = composite_forest_desc.obj_from_input_dict(composite_forest_supplier())

        composite_forest_validator = validator_ctor(
            composite_forest,
            plugin_instances,
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
