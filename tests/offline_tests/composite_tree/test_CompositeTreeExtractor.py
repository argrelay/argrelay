from __future__ import annotations

from argrelay.composite_tree.CompositeForest import CompositeForest
from argrelay.composite_tree.CompositeForestSchema import composite_forest_desc
from argrelay.composite_tree.CompositeTreeExtractor import (
    extract_tree_abs_path_to_interp_id,
    extract_zero_arg_interp_tree,
    extract_jump_tree,
    extract_interp_tree,
    extract_func_tree,
)
from argrelay.composite_tree.DictTreeWalker import normalize_tree
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
    server_plugin_control_,
)
from argrelay.schema_config_core_server.ServerPluginControlSchema import composite_forest_
from argrelay.test_infra import line_no
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_33_76_82_84 composite tree (classes derived from `CompositeTreeExtractorAbstract`).
    """

    def test_extract_tree_abs_path_to_interp_id(self):
        """
        Test that extracted `CompositeInfoType.tree_abs_path_to_interp_id` is the same
        as specified per plugin manually (not via `composite_tree`).
        """

        test_cases = [
            (
                line_no(),
                {
                    "relay_demo": {
                        "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
                    "some_command": {
                        "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
                },
                SpecialFunc.func_id_intercept_invocation.name,
            ),
            (
                line_no(),
                {
                    "relay_demo": {
                        "help": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "help": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
                    "some_command": {
                        "help": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "help": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
                    "service_relay_demo": {
                        "help": f"{InterpTreeInterpFactory.__name__}.default",
                    },
                },
                SpecialFunc.func_id_help_hint.name,
            ),
            (
                line_no(),
                {
                    "relay_demo": {
                        "enum": f"{InterpTreeInterpFactory.__name__}.default",
                    },
                    "some_command": {
                        "enum": f"{InterpTreeInterpFactory.__name__}.default",
                    },
                },
                SpecialFunc.func_id_query_enum_items.name,
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_dict,
                    func_id,
                ) = test_case

                actual_dict = extract_tree_abs_path_to_interp_id(
                    self.load_composite_tree(),
                    func_id,
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_zero_arg_interp_tree(self):
        """
        Test that extracted `CompositeInfoType.zero_arg_interp_tree` is the same
        as specified per plugin manually (not via `composite_tree`).
        """

        test_cases = [
            (
                line_no(),
                {
                    "relay_demo": "InterpTreeInterpFactory.default",
                    "some_command": "InterpTreeInterpFactory.default",
                    "service_relay_demo": "InterpTreeInterpFactory.default",
                    "argrelay.check_env": "InterpTreeInterpFactory.check_env",
                },
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_dict,
                ) = test_case

                actual_dict = extract_zero_arg_interp_tree(
                    self.load_composite_tree(),
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_jump_tree(self):
        """
        Test that extracted `CompositeInfoType.jump_tree` is the same
        as specified per plugin manually (not via `composite_tree`).
        """

        test_cases = [
            # NOTE: FS_91_88_07_23 jump_tree is the same regardless of the plugin.
            (
                line_no(),
                {
                    "relay_demo": {
                        "intercept": [
                            "relay_demo",
                        ],
                        "help": [
                            "relay_demo",
                        ],
                        "enum": [
                            "relay_demo",
                        ],
                        "duplicates": {
                            "intercept": [
                                "relay_demo",
                                "duplicates",
                            ],
                            "help": [
                                "relay_demo",
                                "duplicates",
                            ],
                            "": [
                                "relay_demo",
                                "duplicates",
                            ],
                        },
                        "": [
                            "relay_demo",
                        ],
                    },
                    "some_command": {
                        "intercept": [
                            "some_command",
                        ],
                        "help": [
                            "some_command",
                        ],
                        "enum": [
                            "some_command",
                        ],
                        "duplicates": {
                            "intercept": [
                                "some_command",
                                "duplicates",
                            ],
                            "help": [
                                "some_command",
                                "duplicates",
                            ],
                            "": [
                                "some_command",
                                "duplicates",
                            ],
                        },
                        "": [
                            "some_command",
                        ],
                    },
                    "service_relay_demo": {
                        "help": [
                            "service_relay_demo",
                        ],
                        "": [
                            "service_relay_demo",
                        ],
                    },
                    "argrelay.check_env": {
                        "": [
                            "argrelay.check_env",
                        ],
                    },
                },
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_dict,
                ) = test_case

                actual_dict = extract_jump_tree(
                    self.load_composite_tree(),
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_interp_tree(self):
        """
        Test that extracted `CompositeInfoType.interp_tree` is the same
        as specified per plugin manually (not via `composite_tree`).
        """

        test_cases = [
            (
                line_no(),
                {
                    "relay_demo": {
                        "intercept": "FuncTreeInterpFactory.func_id_intercept_invocation",
                        "help": "FuncTreeInterpFactory.func_id_help_hint",
                        "enum": "FuncTreeInterpFactory.func_id_query_enum_items",
                        "": "FuncTreeInterpFactory.default",
                        "duplicates": {
                            "intercept": "FuncTreeInterpFactory.func_id_intercept_invocation",
                            "help": "FuncTreeInterpFactory.func_id_help_hint",
                            "": "FuncTreeInterpFactory.default",
                        },
                    },
                    "some_command": {
                        "intercept": "FuncTreeInterpFactory.func_id_intercept_invocation",
                        "help": "FuncTreeInterpFactory.func_id_help_hint",
                        "enum": "FuncTreeInterpFactory.func_id_query_enum_items",
                        "": "FuncTreeInterpFactory.default",
                        "duplicates": {
                            "intercept": "FuncTreeInterpFactory.func_id_intercept_invocation",
                            "help": "FuncTreeInterpFactory.func_id_help_hint",
                            "": "FuncTreeInterpFactory.default",
                        },
                    },
                    "service_relay_demo": {
                        "help": "FuncTreeInterpFactory.func_id_help_hint",
                        "": "FuncTreeInterpFactory.service",
                    },
                },
                f"{InterpTreeInterpFactory.__name__}.default",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_dict,
                    plugin_instance_id,
                ) = test_case

                actual_dict = extract_interp_tree(
                    self.load_composite_tree(),
                    plugin_instance_id,
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_func_tree(self):
        """
        Test that extracted `CompositeInfoType.func_tree` is the same
        as specified per plugin manually (not via `composite_tree`).
        """

        func_tree_main = {
            "echo": "func_id_echo_args",
            "goto": {
                "repo": "goto_git_repo_func",
                "host": "goto_host_func",
                "service": "goto_service_func",
            },
            "list": {
                "host": "list_host_func",
                "service": "list_service_func",
            },
            "diff": {
                "service": "diff_service_func",
            },
            "desc": {
                "tag": "desc_git_tag_func",
                "commit": "desc_git_commit_func",
                "host": "desc_host_func",
                "service": "desc_service_func",
            },
            "config": {
                "print_with_level": "funct_id_print_with_severity_level",
                "print_with_exit": "funct_id_print_with_exit_code",
                "print_with_io_redirect": "funct_id_print_with_io_redirect",
                "double_execution": "funct_id_double_execution",
            },
        }

        test_cases = [
            (
                line_no(),
                {
                    "relay_demo": {
                        "intercept": SpecialFunc.func_id_intercept_invocation.name,
                        "duplicates": {
                            "intercept": SpecialFunc.func_id_intercept_invocation.name,
                        },
                    },
                    "some_command": {
                        "intercept": SpecialFunc.func_id_intercept_invocation.name,
                        "duplicates": {
                            "intercept": SpecialFunc.func_id_intercept_invocation.name,
                        }
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.func_id_intercept_invocation",
            ),
            (
                line_no(),
                {
                    "relay_demo": {
                        "help": SpecialFunc.func_id_help_hint.name,
                        "duplicates": {
                            "help": SpecialFunc.func_id_help_hint.name,
                        },
                    },
                    "some_command": {
                        "help": SpecialFunc.func_id_help_hint.name,
                        "duplicates": {
                            "help": SpecialFunc.func_id_help_hint.name,
                        }
                    },
                    "service_relay_demo": {
                        "help": SpecialFunc.func_id_help_hint.name,
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.func_id_help_hint",
            ),
            (
                line_no(),
                {
                    "relay_demo": {
                        "enum": SpecialFunc.func_id_query_enum_items.name,
                    },
                    "some_command": {
                        "enum": SpecialFunc.func_id_query_enum_items.name,
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.func_id_query_enum_items",
            ),
            (
                line_no(),
                {
                    "relay_demo": {
                        "duplicates": {
                            "": func_tree_main,
                        },
                        "": func_tree_main,
                    },
                    "some_command": {
                        "duplicates": {
                            "": func_tree_main,
                        },
                        "": func_tree_main,
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.default",
            ),
            (
                line_no(),
                {
                    "service_relay_demo": {
                        "goto": "goto_service_func",
                        "list": "list_service_func",
                        "diff": "diff_service_func",
                        "desc": "desc_service_func",
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.service",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_func_tree,
                    plugin_instance_id,
                ) = test_case

                normalized_expected_dict = normalize_tree(expected_func_tree)

                # No need to normalize extracted `actual_dict`
                # because `composite_tree` is constructed to maintain `dict` structure
                # without `surrogate_node_id_`-s and `surrogate_tree_leaf_`-s.
                actual_dict = normalize_tree(extract_func_tree(
                    self.load_composite_tree(),
                    plugin_instance_id,
                ))

                self.assertEqual(
                    normalized_expected_dict,
                    actual_dict,
                )

    @staticmethod
    def load_composite_tree(
    ) -> CompositeForest:
        return composite_forest_desc.obj_from_input_dict(
            server_config_desc.dict_from_default_file()[server_plugin_control_][composite_forest_]
        )
