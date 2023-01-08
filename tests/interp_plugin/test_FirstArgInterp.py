from __future__ import annotations

from unittest import TestCase

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.interp_plugin.FirstArgInterpFactory import (
    FirstArgInterpFactory,
)
from argrelay.interp_plugin.NamedNoopInterp import NamedNoopInterp
from argrelay.interp_plugin.NamedNoopInterpFactory import NamedNoopInterpFactory
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.PluginType import PluginType
from argrelay.meta_data.RunMode import RunMode
from argrelay.relay_client import __main__
from argrelay.schema_config_core_server.FirstArgInterpFactorySchema import first_arg_vals_to_next_interp_factory_ids_
from argrelay.schema_config_core_server.ServerConfigSchema import plugin_list_
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_id_,
    plugin_config_,
    plugin_module_name_,
    plugin_class_name_,
    plugin_type_,
)
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import (
    EnvMockBuilder,
    load_relay_demo_server_config_dict,
)


class ThisTestCase(TestCase):

    def run_test(self, test_line):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        first_command_names = [
            "known_command1",
            "known_command2",
        ]

        # Patch server config for FirstArgInterpFactory - bind all `first_command_names` to NamedNoopInterpFactory:
        first_arg_vals_to_next_interp_factory_ids = {}
        for first_command_name in first_command_names:
            # Compose same plugin id (as below):
            first_arg_vals_to_next_interp_factory_ids[
                first_command_name
            ] = NamedNoopInterpFactory.__name__ + "." + first_command_name
        server_config_dict = load_relay_demo_server_config_dict()
        for plugin_entry in server_config_dict[plugin_list_]:
            if plugin_entry[plugin_id_] == FirstArgInterpFactory.__name__:
                plugin_entry[plugin_config_] = {
                    first_arg_vals_to_next_interp_factory_ids_: first_arg_vals_to_next_interp_factory_ids,
                }

        # Patch server config to add NamedNoopInterpFactory (2 plugin instances):
        for first_command_name in first_command_names:
            plugin_entry = {
                # Compose same plugin id (as above):
                plugin_id_: NamedNoopInterpFactory.__name__ + "." + first_command_name,
                plugin_module_name_: NamedNoopInterpFactory.__module__,
                plugin_class_name_: NamedNoopInterpFactory.__name__,
                plugin_type_: PluginType.InterpFactoryPlugin.name,
                plugin_config_: {
                    "instance_name": first_command_name,
                },
            }
            server_config_dict[plugin_list_].append(plugin_entry)

        env_mock_builder = (
            EnvMockBuilder()
            .set_run_mode(RunMode.CompletionMode)
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_server_config_dict(server_config_dict)
        )
        with env_mock_builder.build():
            command_obj = __main__.main()
            assert isinstance(command_obj, AbstractLocalClientCommand)
            interp_ctx = command_obj.interp_ctx

            # FirstArgInterp is supposed to consume first pos arg only (first token):
            self.assertEqual([0], interp_ctx.consumed_tokens)
            first_token_value = interp_ctx.parsed_ctx.all_tokens[0]

            interp_factory_id = first_arg_vals_to_next_interp_factory_ids[first_token_value]
            interp_factory_instance: NamedNoopInterpFactory = interp_ctx.interp_factories[interp_factory_id]
            prev_interp: NamedNoopInterp = interp_ctx.prev_interp

            self.assertTrue(
                prev_interp.instance_name
                ==
                interp_factory_instance.config_dict["instance_name"]
                ==
                first_token_value,
                "config instructs to name interp instance as the first token it binds to",
            )

    def test_consume_pos_args_unknown(self):
        test_line = "unknown_command prod|"
        with self.assertRaises(KeyError):
            self.run_test(test_line)

    def test_consume_pos_args_known(self):
        test_line = "known_command1 prod|"
        self.run_test(test_line)
        test_line = "known_command2 prod|"
        self.run_test(test_line)

    def test_consume_pos_args_with_no_args(self):
        test_line = "  | "
        with self.assertRaises(IndexError):
            self.run_test(test_line)
