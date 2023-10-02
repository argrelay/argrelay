from __future__ import annotations

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.FirstArgInterpFactory import (
    FirstArgInterpFactory,
)
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_vals_to_next_interp_factory_ids_
from argrelay.plugin_interp.NoopInterp import NoopInterp
from argrelay.plugin_interp.NoopInterpFactory import NoopInterpFactory
from argrelay.relay_client import __main__
from argrelay.schema_config_core_server.ServerConfigSchema import plugin_instance_id_load_list_, plugin_dict_
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_config_,
    plugin_module_name_,
    plugin_class_name_,
    plugin_type_,
)
from argrelay.test_helper import parse_line_and_cpos, line_no
from argrelay.test_helper.EnvMockBuilder import (
    load_custom_integ_server_config_dict,
    LocalClientEnvMockBuilder,
)
from argrelay.test_helper.InOutTestCase import InOutTestCase


class ThisTestCase(InOutTestCase):

    def run_consume_test(self, test_line, expected_consumed_first_token):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        first_command_names = [
            "known_command1",
            "known_command2",
        ]

        # Patch server config for FirstArgInterpFactory - bind all `first_command_names` to NoopInterpFactory:
        first_arg_vals_to_next_interp_factory_ids = {}
        for first_command_name in first_command_names:
            # Compose same plugin id (as below):
            plugin_instance_id = NoopInterpFactory.__name__ + "." + first_command_name
            first_arg_vals_to_next_interp_factory_ids[first_command_name] = plugin_instance_id
        server_config_dict = load_custom_integ_server_config_dict()
        plugin_entry = server_config_dict[plugin_dict_][FirstArgInterpFactory.__name__]
        plugin_entry[plugin_config_] = {
            first_arg_vals_to_next_interp_factory_ids_: first_arg_vals_to_next_interp_factory_ids,
        }

        # Patch server config to add NoopInterpFactory (2 plugin instances):
        for first_command_name in first_command_names:
            # Compose same plugin id (as above):
            plugin_instance_id = NoopInterpFactory.__name__ + "." + first_command_name
            plugin_entry = {
                plugin_module_name_: NoopInterpFactory.__module__,
                plugin_class_name_: NoopInterpFactory.__name__,
                plugin_type_: PluginType.InterpFactoryPlugin.name,
                plugin_config_: {
                    "arbitrary_comment": first_command_name,
                },
            }
            assert plugin_instance_id not in server_config_dict[plugin_dict_]
            assert plugin_instance_id not in server_config_dict[plugin_instance_id_load_list_]
            server_config_dict[plugin_dict_][plugin_instance_id] = plugin_entry
            server_config_dict[plugin_instance_id_load_list_].append(plugin_instance_id)

        env_mock_builder = (
            LocalClientEnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_server_config_dict(server_config_dict)
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)
            interp_ctx = command_obj.interp_ctx

            if not expected_consumed_first_token:
                self.assertEqual([], interp_ctx.consumed_tokens)
                return

            # FirstArgInterp is supposed to consume first pos arg only (first token):
            self.assertEqual([0], interp_ctx.consumed_tokens)
            first_token_value = interp_ctx.parsed_ctx.all_tokens[0]

            interp_factory_id = first_arg_vals_to_next_interp_factory_ids[first_token_value]
            interp_factory_instance: NoopInterpFactory = interp_ctx.interp_factories[interp_factory_id]
            prev_interp: NoopInterp = interp_ctx.prev_interp

            self.assertTrue(
                prev_interp.arbitrary_comment
                ==
                interp_factory_instance.config_dict["arbitrary_comment"]
                ==
                first_token_value,
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
                    "relay_demo",
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
                    "TD_63_37_05_36",  # demo
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                )
