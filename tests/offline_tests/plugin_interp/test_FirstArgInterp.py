from __future__ import annotations

from copy import deepcopy

from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.composite_forest.CompositeForestSchema import tree_roots_
from argrelay.composite_forest.CompositeNodeSchema import sub_tree_
from argrelay.composite_forest.DictTreeWalker import surrogate_node_id_
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_interp.FirstArgInterpFactory import (
    FirstArgInterpFactory,
)
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import (
    first_arg_vals_to_next_interp_factory_ids_,
    ignored_func_ids_list_,
)
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import jump_tree_, func_selector_tree_
from argrelay.plugin_interp.InterpTreeInterp import InterpTreeInterp
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import interp_selector_tree_
from argrelay.relay_client import __main__
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
    server_plugin_control_,
)
from argrelay.schema_config_core_server.ServerPluginControlSchema import composite_forest_
from argrelay.schema_config_plugin.PluginConfigSchema import (
    plugin_instance_entries_,
    plugin_config_desc,
    reusable_config_data_,
)
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_config_,
)
from argrelay.test_infra import parse_line_and_cpos, line_no
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def run_consume_test(self, test_line, expected_consumed_first_token):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        first_command_names = [
            "known_command1",
            "known_command2",
        ]

        server_config_dict = server_config_desc.dict_from_default_file()
        plugin_config_dict = plugin_config_desc.dict_from_default_file()

        # Patch server config for `FirstArgInterpFactory`:
        # bind all `first_command_name`-s to `InterpTreeInterpFactory.default`:
        dependent_plugin_id = f"{FirstArgInterpFactory.__name__}.default"
        plugin_entry = plugin_config_dict[plugin_instance_entries_][dependent_plugin_id]
        for first_command_name in first_command_names:
            # Compose same plugin id (as below):
            plugin_instance_id = f"{InterpTreeInterpFactory.__name__}.default"
            plugin_entry[plugin_config_][first_arg_vals_to_next_interp_factory_ids_][
                first_command_name
            ] = plugin_instance_id

        first_arg_vals_to_next_interp_factory_ids = plugin_entry[plugin_config_][
            first_arg_vals_to_next_interp_factory_ids_
        ]

        # List all known `func_id`-s (without using them by this plugin) to keep validation happy:
        plugin_entry[plugin_config_][ignored_func_ids_list_] = [
            SpecialFunc.func_id_unplugged.name,
        ]

        # Patch server config to plug given command with the same config as `some_command`:
        for first_command_name in first_command_names:

            ############################################################################################################

            composite_tree_root = deepcopy(
                server_config_dict[
                    server_plugin_control_
                ][
                    composite_forest_
                ][
                    tree_roots_
                ][
                    "some_command"
                ]
            )
            # Remove unnecessary:
            del composite_tree_root[sub_tree_]["intercept"]
            del composite_tree_root[sub_tree_]["help"]
            del composite_tree_root[sub_tree_]["enum"]
            del composite_tree_root[sub_tree_]["duplicates"]

            server_config_dict[
                server_plugin_control_
            ][
                composite_forest_
            ][
                tree_roots_
            ][
                first_command_name
            ] = composite_tree_root

            ############################################################################################################

            jump_sub_tree = {
                surrogate_node_id_: [
                    first_command_name,
                ]
            }
            plugin_config_dict[
                reusable_config_data_
            ][
                jump_tree_
            ][
                first_command_name
            ] = jump_sub_tree
            # Replace in all plugin instances using `jump_tree`:
            for plugin_instance_id in [
                f"{FuncTreeInterpFactory.__name__}.func_id_intercept_invocation",
                f"{FuncTreeInterpFactory.__name__}.func_id_help_hint",
                f"{FuncTreeInterpFactory.__name__}.func_id_query_enum_items",
                f"{FuncTreeInterpFactory.__name__}.default",
                f"{FuncTreeInterpFactory.__name__}.check_env",
                f"{FuncTreeInterpFactory.__name__}.service",
            ]:
                plugin_config_dict[
                    plugin_instance_entries_
                ][
                    plugin_instance_id
                ][
                    plugin_config_
                ][
                    jump_tree_
                ][
                    first_command_name
                ] = jump_sub_tree

            ############################################################################################################

            interp_selector_tree = deepcopy(
                plugin_config_dict[
                    plugin_instance_entries_
                ][
                    f"{InterpTreeInterpFactory.__name__}.default"
                ][
                    plugin_config_
                ][
                    interp_selector_tree_
                ][
                    "some_command"
                ]
            )
            # Remove unnecessary:
            del interp_selector_tree["intercept"]
            del interp_selector_tree["help"]
            del interp_selector_tree["enum"]
            del interp_selector_tree["duplicates"]

            plugin_config_dict[
                plugin_instance_entries_
            ][
                f"{InterpTreeInterpFactory.__name__}.default"
            ][
                plugin_config_
            ][
                interp_selector_tree_
            ][
                first_command_name
            ] = interp_selector_tree

            ############################################################################################################

            func_selector_tree = deepcopy(
                plugin_config_dict[
                    plugin_instance_entries_
                ][
                    f"{FuncTreeInterpFactory.__name__}.default"
                ][
                    plugin_config_
                ][
                    func_selector_tree_
                ][
                    "some_command"
                ]
            )
            # Remove unnecessary:
            del func_selector_tree["duplicates"]

            plugin_config_dict[
                plugin_instance_entries_
            ][
                f"{FuncTreeInterpFactory.__name__}.default"
            ][
                plugin_config_
            ][
                func_selector_tree_
            ][
                first_command_name
            ] = func_selector_tree

            ############################################################################################################

        env_mock_builder = (
            LocalClientEnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_server_config_dict(server_config_dict)
            .set_plugin_config_dict(plugin_config_dict)
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, ClientCommandLocal)
            interp_ctx = command_obj.interp_ctx

            if not expected_consumed_first_token:
                self.assertEqual([], interp_ctx.consumed_token_ipos_list())
                return

            # FirstArgInterp is supposed to consume first pos arg only (first token):
            self.assertEqual([0], interp_ctx.consumed_token_ipos_list())
            first_token_value = interp_ctx.parsed_ctx.all_tokens[0]

            interp_factory_id = first_arg_vals_to_next_interp_factory_ids[first_token_value]
            interp_factory_instance: InterpTreeInterpFactory = interp_ctx.interp_factories[interp_factory_id]
            prev_interp: InterpTreeInterp = interp_ctx.prev_interp

            self.assertTrue(
                (
                    prev_interp.interp_factory_id
                    ==
                    interp_factory_instance.plugin_instance_id
                    ==
                    f"{InterpTreeInterpFactory.__name__}.default"
                ),
                "config instructs to name interp instance as the first token it binds to",
            )

    def test_consume_pos_args_unknown(self):
        test_line = "unknown_command prod|"
        self.run_consume_test(test_line, None)

    def test_consume_pos_args_known(self):
        test_line = "known_command1 prod|"
        self.run_consume_test(test_line, "known_command1")
        test_line = "known_command2 prod|"
        self.run_consume_test(test_line, "known_command2")

    def test_consume_pos_args_with_no_args(self):
        test_line = "  | "
        self.run_consume_test(test_line, None)

    def test_propose_command_id(self):
        test_cases = [
            (
                line_no(), "|", CompType.PrefixHidden,
                [
                    "argrelay.check_env",
                    "relay_demo",
                    "service_relay_demo",
                    "some_command",
                ],
                "This will not be called from shell - shell will suggest when command_id is already selected. "
                "Suggest registered command_id-s.",
            ),
            (
                line_no(), "r|", CompType.PrefixHidden,
                [
                    "relay_demo",
                ],
                "This will not be called from shell - shell will suggest when command_id is already selected. "
                "Suggest registered command_id-s.",
            ),
            (
                line_no(), " qwer|", CompType.PrefixHidden,
                [],
                "This will not be called from shell - shell will suggest when command_id is already selected. "
                "Suggest registered command_id-s.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    case_comment,
                ) = test_case

                self.verify_output_with_new_server_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                )
