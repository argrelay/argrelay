from __future__ import annotations

from argrelay_app_server.composite_forest.CompositeForestExtractor import (
    extract_func_tree,
    extract_interp_tree,
    extract_jump_tree,
    extract_tree_abs_path_to_interp_id,
    extract_zero_arg_interp_tree,
)
from argrelay_app_server.composite_forest.DictTreeWalker import normalize_tree
from argrelay_lib_root.enum_desc.SpecialFunc import SpecialFunc
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    FuncTreeInterpFactory,
)
from argrelay_lib_server_plugin_core.plugin_interp.InterpTreeInterpFactory import (
    InterpTreeInterpFactory,
)
from argrelay_schema_config_server.runtime_data_server_app.CompositeForest import (
    CompositeForest,
)
from argrelay_schema_config_server.schema_config_server_app.CompositeForestSchema import (
    composite_forest_desc,
)
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import (
    server_config_desc,
    server_plugin_control_,
)
from argrelay_schema_config_server.schema_config_server_app.ServerPluginControlSchema import (
    composite_forest_,
)
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_33_76_82_84 composite forest (classes derived from `CompositeForestExtractorAbstract`).
    """

    def test_extract_tree_abs_path_to_interp_id(self):
        """
        Test that extracted `CompositeInfoType.tree_abs_path_to_interp_id` is expected.
        """

        test_cases = [
            (
                line_no(),
                {
                    "lay": {
                        "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "intercept": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
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
                    "lay": {
                        "help": f"{InterpTreeInterpFactory.__name__}.default",
                        "duplicates": {
                            "help": f"{InterpTreeInterpFactory.__name__}.default",
                        },
                    },
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
                    "lay": {
                        "enum": f"{InterpTreeInterpFactory.__name__}.default",
                    },
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
                    self.load_composite_forest(),
                    func_id,
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_zero_arg_interp_tree(self):
        """
        Test that extracted `CompositeInfoType.zero_arg_interp_tree` is expected.
        """

        test_cases = [
            (
                line_no(),
                {
                    "lay": "InterpTreeInterpFactory.default",
                    "ar_ssh": "InterpTreeInterpFactory.default",
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
                    self.load_composite_forest(),
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_jump_tree(self):
        """
        Test that extracted `CompositeInfoType.jump_tree` is the same
        as specified per plugin manually (not via `composite_forest`).
        """

        test_cases = [
            # NOTE: FS_91_88_07_23 jump_tree is the same regardless of the plugin.
            (
                line_no(),
                {
                    "lay": {
                        "intercept": [
                            "lay",
                        ],
                        "help": [
                            "lay",
                        ],
                        "enum": [
                            "lay",
                        ],
                        "duplicates": {
                            "intercept": [
                                "lay",
                                "duplicates",
                            ],
                            "help": [
                                "lay",
                                "duplicates",
                            ],
                            "": [
                                "lay",
                                "duplicates",
                            ],
                        },
                        "": [
                            "lay",
                        ],
                    },
                    "ar_ssh": {
                        "": [
                            "ar_ssh",
                        ],
                    },
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
                    self.load_composite_forest(),
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_interp_tree(self):
        """
        Test that extracted `CompositeInfoType.interp_tree` is the same
        as specified per plugin manually (not via `composite_forest`).
        """

        test_cases = [
            (
                line_no(),
                {
                    "lay": {
                        "intercept": "FuncTreeInterpFactory.default",
                        "help": "FuncTreeInterpFactory.default",
                        "enum": "FuncTreeInterpFactory.default",
                        "": "FuncTreeInterpFactory.default",
                        "duplicates": {
                            "intercept": "FuncTreeInterpFactory.default",
                            "help": "FuncTreeInterpFactory.default",
                            "": "FuncTreeInterpFactory.default",
                        },
                    },
                    "ar_ssh": {
                        "": "FuncTreeInterpFactory.default",
                    },
                    "relay_demo": {
                        "intercept": "FuncTreeInterpFactory.default",
                        "help": "FuncTreeInterpFactory.default",
                        "enum": "FuncTreeInterpFactory.default",
                        "": "FuncTreeInterpFactory.default",
                        "duplicates": {
                            "intercept": "FuncTreeInterpFactory.default",
                            "help": "FuncTreeInterpFactory.default",
                            "": "FuncTreeInterpFactory.default",
                        },
                    },
                    "some_command": {
                        "intercept": "FuncTreeInterpFactory.default",
                        "help": "FuncTreeInterpFactory.default",
                        "enum": "FuncTreeInterpFactory.default",
                        "": "FuncTreeInterpFactory.default",
                        "duplicates": {
                            "intercept": "FuncTreeInterpFactory.default",
                            "help": "FuncTreeInterpFactory.default",
                            "": "FuncTreeInterpFactory.default",
                        },
                    },
                    "service_relay_demo": {
                        "help": "FuncTreeInterpFactory.default",
                        "": "FuncTreeInterpFactory.default",
                    },
                },
                f"{InterpTreeInterpFactory.__name__}.default",
            ),
            (
                line_no(),
                {
                    "argrelay.check_env": {
                        "": f"{FuncTreeInterpFactory.__name__}.check_env",
                    },
                },
                f"{InterpTreeInterpFactory.__name__}.check_env",
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
                    self.load_composite_forest(),
                    plugin_instance_id,
                )

                self.assertEqual(
                    expected_dict,
                    actual_dict,
                )

    def test_extract_func_tree(self):
        """
        Test that extracted `CompositeInfoType.func_tree` is the same
        as specified per plugin manually (not via `composite_forest`).
        """

        func_tree_main = {
            "echo": "func_id_echo_args",
            "no_data": SpecialFunc.func_id_no_data.name,
            "data": {
                "get": SpecialFunc.func_id_get_data_envelopes.name,
                "set": SpecialFunc.func_id_set_data_envelopes.name,
            },
            "goto": {
                "repo": "func_id_goto_git_repo",
                "host": "func_id_goto_host",
                "service": "func_id_goto_service",
            },
            "list": {
                "host": "func_id_list_host",
                "service": "func_id_list_service",
            },
            "diff": {
                "service": "func_id_diff_service",
            },
            "desc": {
                "tag": "func_id_desc_git_tag",
                "commit": "func_id_desc_git_commit",
                "host": "func_id_desc_host",
                "service": "func_id_desc_service",
            },
            "config": {
                "print_with_level": "func_id_print_with_severity_level",
                "print_with_exit": "func_id_print_with_exit_code",
                "print_with_io_redirect": "func_id_print_with_io_redirect",
                "double_execution": "func_id_double_execution",
            },
            "ssh": "func_id_ssh_dst",
        }

        test_cases = [
            (
                line_no(),
                {
                    "lay": {
                        "help": "func_id_help_hint",
                        "intercept": "func_id_intercept_invocation",
                        "enum": "func_id_query_enum_items",
                        "duplicates": {
                            "help": "func_id_help_hint",
                            "intercept": "func_id_intercept_invocation",
                            "": func_tree_main,
                        },
                        "": func_tree_main,
                    },
                    "ar_ssh": {
                        "": "func_id_ssh_dst",
                    },
                    "relay_demo": {
                        "help": "func_id_help_hint",
                        "intercept": "func_id_intercept_invocation",
                        "enum": "func_id_query_enum_items",
                        "duplicates": {
                            "help": "func_id_help_hint",
                            "intercept": "func_id_intercept_invocation",
                            "": func_tree_main,
                        },
                        "": func_tree_main,
                    },
                    "some_command": {
                        "help": "func_id_help_hint",
                        "intercept": "func_id_intercept_invocation",
                        "enum": "func_id_query_enum_items",
                        "duplicates": {
                            "help": "func_id_help_hint",
                            "intercept": "func_id_intercept_invocation",
                            "": func_tree_main,
                        },
                        "": func_tree_main,
                    },
                    "service_relay_demo": {
                        "help": "func_id_help_hint",
                        "": {
                            "goto": "func_id_goto_service",
                            "list": "func_id_list_service",
                            "diff": "func_id_diff_service",
                            "desc": "func_id_desc_service",
                        },
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.default",
            ),
            (
                line_no(),
                {
                    "argrelay.check_env": {
                        "server_version": "func_id_get_server_argrelay_version",
                        "server_commit": "func_id_get_server_project_git_commit_id",
                        "server_start_time": "func_id_get_server_start_time",
                    },
                },
                f"{FuncTreeInterpFactory.__name__}.check_env",
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

                normalized_actual_dict = normalize_tree(
                    extract_func_tree(
                        self.load_composite_forest(),
                        plugin_instance_id,
                    )
                )

                self.assertEqual(
                    normalized_expected_dict,
                    normalized_actual_dict,
                )

    @staticmethod
    def load_composite_forest() -> CompositeForest:
        return composite_forest_desc.obj_from_input_dict(
            server_config_desc.dict_from_default_file()[server_plugin_control_][
                composite_forest_
            ]
        )
