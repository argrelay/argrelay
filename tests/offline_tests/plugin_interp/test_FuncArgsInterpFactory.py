from __future__ import annotations

from unittest import TestCase

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.NoopDelegator import NoopDelegator
from argrelay.plugin_interp.FuncArgsInterpFactory import FuncArgsInterpFactory
from argrelay.relay_client import __main__
from argrelay.schema_config_core_server.ServerConfigSchema import (
    plugin_instance_id_load_list_,
    static_data_,
    plugin_dict_,
)
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_, instance_data_
from argrelay.schema_config_interp.FuncArgsInterpConfigSchema import (
    function_search_control_,
    function_init_control_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_
from argrelay.schema_config_interp.SearchControlSchema import envelope_class_, keys_to_types_list_
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_config_,
    plugin_module_name_,
    plugin_class_name_,
    plugin_type_,
)
from argrelay.test_helper import parse_line_and_cpos
from argrelay.test_helper.EnvMockBuilder import (
    load_custom_integ_server_config_dict,
    load_custom_integ_client_config_dict,
    LocalClientEnvMockBuilder,
)


class ThisTestCase(TestCase):

    def test_validate_function_envelopes_unambiguously_qualified(self):
        client_config_dict = load_custom_integ_client_config_dict()
        server_config_dict = load_custom_integ_server_config_dict()
        data_envelopes = server_config_dict[static_data_][data_envelopes_]

        (command_line, cursor_cpos) = parse_line_and_cpos("some_command |")

        type_1 = "whatever_type_1"
        type_2 = "whatever_type_2"

        # Configure new `FuncArgsInterpFactory`:
        plugin_instance_id = FuncArgsInterpFactory.__name__ + ".test"
        assert plugin_instance_id not in server_config_dict[plugin_instance_id_load_list_]
        assert plugin_instance_id not in server_config_dict[plugin_dict_]
        server_config_dict[plugin_instance_id_load_list_].append(plugin_instance_id)
        server_config_dict[plugin_dict_][plugin_instance_id] = {
            plugin_module_name_: FuncArgsInterpFactory.__module__,
            plugin_class_name_: FuncArgsInterpFactory.__name__,
            plugin_type_: PluginType.InterpFactoryPlugin.name,
            plugin_config_: {
                function_search_control_: {
                    envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                    keys_to_types_list_: [
                        {type_1: type_1},
                        {type_2: type_2},
                    ]
                },
                function_init_control_: {
                    init_types_to_values_: {
                    },
                },
            }
        }

        # Add two functions with unique "coordinates":
        given_function_envelope = {
            envelope_id_: "func_1",
            instance_data_: {
                delegator_plugin_instance_id_: NoopDelegator.__name__,
                search_control_list_: [],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            type_1: "type_1_value_1",
            type_2: "type_2_value_1",
        }
        data_envelopes.append(given_function_envelope)
        given_function_envelope = {
            envelope_id_: "func_2",
            instance_data_: {
                delegator_plugin_instance_id_: NoopDelegator.__name__,
                search_control_list_: [],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            type_1: "type_1_value_2",
            type_2: "type_2_value_2",
        }
        data_envelopes.append(given_function_envelope)

        # Test 1: should pass
        env_mock_builder = (
            LocalClientEnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_server_config_dict(server_config_dict)
        )
        with env_mock_builder.build():
            __main__.main()
            self.assertTrue(True)

        # Add function with non-unique "coordinates":
        given_function_envelope = {
            envelope_id_: "func_3",
            instance_data_: {
                delegator_plugin_instance_id_: NoopDelegator.__name__,
                search_control_list_: [],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            type_1: "type_1_value_1",
            type_2: "type_2_value_1",
        }
        data_envelopes.append(given_function_envelope)

        # Test 2: should fail
        with self.assertRaises(AssertionError):
            env_mock_builder = (
                LocalClientEnvMockBuilder()
                .set_command_line(command_line)
                .set_cursor_cpos(cursor_cpos)
                .set_comp_type(CompType.PrefixShown)
                .set_server_config_dict(server_config_dict)
            )
            with env_mock_builder.build():
                __main__.main()
                self.assertTrue("unreachable")
