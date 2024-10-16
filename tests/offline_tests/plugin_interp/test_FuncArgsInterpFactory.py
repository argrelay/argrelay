from __future__ import annotations

import unittest

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.NoopDelegator import NoopDelegator
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory, func_search_control_
from argrelay.relay_client import __main__
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import data_envelopes_
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
)
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import (
    keys_to_props_list_,
    collection_name_,
    props_to_values_dict_,
)
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, server_plugin_instances_
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_config_,
    plugin_module_name_,
    plugin_class_name_,
    plugin_dependencies_,
)
from argrelay.test_infra import parse_line_and_cpos
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)


class ThisTestClass(BaseTestClass):

    # TODO: This test is not adequate anymore:
    #       *   Instead of manually adding search control and func envelope properties, they are automatic based on func tree.
    #       *   Instead of adding func envelope to the collection directly, they are requested automatically from delegators in func load process.
    #       Can there be equivalent for similar test coverage? I think no - when it is all automatic, func envelopes are unambiguously qualified by construction.
    @unittest.skip
    def test_validate_function_envelopes_unambiguously_qualified(self):
        client_config_dict = client_config_desc.dict_from_default_file()
        server_config_dict = server_config_desc.dict_from_default_file()
        plugin_config_dict = plugin_config_desc.dict_from_default_file()

        envelope_collection = server_config_dict[static_data_][envelope_collections_].setdefault(
            ReservedEnvelopeClass.ClassFunction.name,
            {
                data_envelopes_: [],
            },
        )
        func_envelopes = envelope_collection[ReservedEnvelopeClass.ClassFunction.name]

        (command_line, cursor_cpos) = parse_line_and_cpos("some_command |")

        type_1 = "whatever_type_1"
        type_2 = "whatever_type_2"

        plugin_instance_id = f"{FuncTreeInterpFactory.__name__}.test"
        assert plugin_instance_id not in plugin_config_dict[server_plugin_instances_]
        plugin_config_dict[server_plugin_instances_][plugin_instance_id] = {
            plugin_module_name_: FuncTreeInterpFactory.__module__,
            plugin_class_name_: FuncTreeInterpFactory.__name__,
            plugin_dependencies_: [],
            plugin_config_: {
                func_search_control_: {
                    collection_name_: ReservedEnvelopeClass.ClassFunction.name,
                    props_to_values_dict_: {
                        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                    },
                    keys_to_props_list_: [
                        {type_1: type_1},
                        {type_2: type_2},
                    ],
                },
            }
        }

        # Add two functions with unique "coordinates":
        given_function_envelope = {
            instance_data_: {
                func_id_: "func_1",
                delegator_plugin_instance_id_: f"{NoopDelegator.__name__}.default",
                search_control_list_: [],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedPropName.func_state.name: FuncState.fs_demo.name,
            ReservedPropName.func_id.name: "func_1",
            type_1: "type_1_value_1",
            type_2: "type_2_value_1",
        }
        func_envelopes.append(given_function_envelope)
        given_function_envelope = {
            instance_data_: {
                func_id_: "func_2",
                delegator_plugin_instance_id_: f"{NoopDelegator.__name__}.default",
                search_control_list_: [],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedPropName.func_state.name: FuncState.fs_demo.name,
            ReservedPropName.func_id.name: "func_2",
            type_1: "type_1_value_2",
            type_2: "type_2_value_2",
        }
        func_envelopes.append(given_function_envelope)

        # Test 1: should pass
        env_mock_builder = (
            LocalClientEnvMockBuilder()
            .set_command_line(command_line)
            .set_cursor_cpos(cursor_cpos)
            .set_comp_type(CompType.PrefixShown)
            .set_server_config_dict(server_config_dict)
            .set_plugin_config_dict(plugin_config_dict)
        )
        with env_mock_builder.build():
            __main__.main()
            self.assertTrue(True)

        # Add function with non-unique "coordinates":
        given_function_envelope = {
            instance_data_: {
                func_id_: "func_3",
                delegator_plugin_instance_id_: f"{NoopDelegator.__name__}.default",
                search_control_list_: [],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedPropName.func_state.name: FuncState.fs_demo.name,
            ReservedPropName.func_id.name: "func_3",
            type_1: "type_1_value_1",
            type_2: "type_2_value_1",
        }
        func_envelopes.append(given_function_envelope)

        # Test 2: should fail
        with self.assertRaises(AssertionError):
            env_mock_builder = (
                LocalClientEnvMockBuilder()
                .set_command_line(command_line)
                .set_cursor_cpos(cursor_cpos)
                .set_comp_type(CompType.PrefixShown)
                .set_server_config_dict(server_config_dict)
                .set_plugin_config_dict(plugin_config_dict)
            )
            with env_mock_builder.build():
                __main__.main()
                self.assertTrue("unreachable")
