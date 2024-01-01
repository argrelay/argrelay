import copy

from marshmallow import ValidationError

from argrelay.custom_integ.GitRepoLoaderConfigSchema import git_repo_loader_config_desc
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_delegator_custom_data_desc
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_interp_factory_config_desc
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import func_tree_interp_config_desc
from argrelay.plugin_interp.JumpTreeInterpFactoryConfigSchema import jump_tree_interp_config_desc
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_config_core_client.ConnectionConfigSchema import connection_config_desc
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import envelope_collection_desc
from argrelay.schema_config_core_server.MongoClientConfigSchema import mongo_client_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.MongoServerConfigSchema import mongo_server_config_desc
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_core_server.ServerPluginControlSchema import server_plugin_control_desc
from argrelay.schema_config_core_server.StaticDataSchema import static_data_desc
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import function_envelope_instance_data_desc
from argrelay.schema_config_interp.InitControlSchema import init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc
from argrelay.schema_response.AssignedValueSchema import assigned_value_desc
from argrelay.schema_response.EnvelopeContainerSchema import envelope_container_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec.const_int import DEFAULT_IP_ADDRESS, DEFAULT_PORT_NUMBER
from argrelay.test_infra import line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass


class ThisTestClass(BaseTestClass):

    def test_type_desc_example_is_loadable_and_dumpable(self):
        """
        Uses each schema definition to load and dump its own example.
        """

        test_cases = [
            (line_no(), call_context_desc),
            (line_no(), invocation_input_desc),
            (line_no(), plugin_entry_desc),
            (line_no(), git_repo_loader_config_desc),
            (line_no(), client_config_desc),
            (line_no(), connection_config_desc),
            (line_no(), first_arg_interp_factory_config_desc),
            (line_no(), mongo_client_config_desc),
            (line_no(), mongo_config_desc),
            (line_no(), mongo_server_config_desc),
            (line_no(), server_config_desc),
            (line_no(), static_data_desc),
            (line_no(), data_envelope_desc),
            (line_no(), search_control_desc),
            (line_no(), init_control_desc),
            (line_no(), function_envelope_instance_data_desc),
            (line_no(), func_tree_interp_config_desc),
            (line_no(), arg_values_desc),
            (line_no(), interp_result_desc),
            (line_no(), assigned_value_desc),
            (line_no(), envelope_container_desc),
            (line_no(), error_delegator_custom_data_desc),
            (line_no(), jump_tree_interp_config_desc),
            (line_no(), server_plugin_control_desc),
            (line_no(), envelope_collection_desc),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, type_desc) = test_case

                # Special cases:
                if type_desc == data_envelope_desc:
                    self.test_data_envelope_desc()
                    return

                loaded_obj = type_desc.dict_schema.load(type_desc.dict_example)
                dumped_dict = type_desc.dict_schema.dump(loaded_obj)
                reloaded_obj = type_desc.dict_schema.load(dumped_dict)

                dumped_loaded_json = type_desc.dict_schema.dumps(loaded_obj, sort_keys = True)
                dumped_reloaded_json = type_desc.dict_schema.dumps(reloaded_obj, sort_keys = True)

                self.assertEqual(
                    loaded_obj,
                    reloaded_obj,
                )
                self.assertEqual(
                    dumped_loaded_json,
                    dumped_reloaded_json,
                )

                # Expect no problem:
                type_desc.validate_dict(dumped_dict)
                # Expect some problem:
                dumped_dict["intentionally_unknown_key"] = "whatever"
                self.assertRaises(
                    ValidationError,
                    lambda: type_desc.validate_dict(dumped_dict),
                )

    def test_data_envelope_desc(self):
        """
        Special case for `DataEnvelopeSchema` (as its object is actually an arbitrary dict).
        `Schema.dump` cannot be used as it does not preserve all extra keys - see `DataEnvelopeSchema` for details.
        """
        type_desc = data_envelope_desc

        orig_dict = type_desc.dict_example
        loaded_dict = type_desc.dict_schema.load(orig_dict)
        assert type(loaded_dict) is dict

        dumped_orig_json = type_desc.dict_schema.dumps(orig_dict, sort_keys = True)
        dumped_loaded_json = type_desc.dict_schema.dumps(loaded_dict, sort_keys = True)

        dumped_dict = type_desc.dict_schema.dump(loaded_dict)
        # Expect problem:
        # `Schema.dump` does not preserve all keys of original `dict` - only those which mentioned in the schema:
        self.assertRaises(
            KeyError,
            lambda: type_desc.validate_dict(dumped_dict),
        )

        self.assertEqual(
            orig_dict,
            loaded_dict,
        )
        self.assertNotEqual(
            orig_dict,
            dumped_dict,
        )
        self.assertEqual(
            dumped_orig_json,
            dumped_loaded_json,
        )

        valid_dict = copy.deepcopy(orig_dict)
        # Expect no problem:
        type_desc.validate_dict(valid_dict)

        valid_dict_with_extra_keys = copy.deepcopy(valid_dict)
        valid_dict_with_extra_keys["intentionally_unknown_key"] = "whatever"
        # Expect no problem (still because `DataEnvelopeSchema` does not care about extra keys):
        type_desc.validate_dict(valid_dict_with_extra_keys)

    def test_minimal_client_config_desc(self):
        """
        Makes sure the minimal config data for client is loadable.
        """

        client_config: ClientConfig = client_config_desc.from_yaml_str(
            """
            {
                "connection_config": {
                    "server_host_name": "localhost",
                    "server_port_number": 8787,
                }
            }
            """
        )
        self.assertEqual(
            client_config.connection_config.server_host_name,
            DEFAULT_IP_ADDRESS,
        )
        self.assertEqual(
            client_config.connection_config.server_port_number,
            DEFAULT_PORT_NUMBER,
        )
        self.assertEqual(
            client_config.use_local_requests,
            False,
        )
        self.assertEqual(
            client_config.optimize_completion_request,
            True,
        )
