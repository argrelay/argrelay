import copy

from marshmallow import ValidationError

from argrelay.composite_forest.CompositeForestSchema import composite_forest_desc
from argrelay.composite_forest.CompositeNodeSchema import (
    base_node_desc,
    interp_tree_node_desc,
    zero_arg_node_desc,
    func_tree_node_desc,
    tree_path_node_desc,
)
from argrelay.custom_integ.ConfigOnlyLoaderConfigSchema import config_only_loader_config_desc
from argrelay.custom_integ.FuncConfigSchema import func_config_desc
from argrelay.custom_integ.GitRepoLoaderConfigSchema import git_repo_loader_config_desc
from argrelay.custom_integ.SchemaConfigDelegatorConfigBase import base_config_delegator_config_desc
from argrelay.custom_integ.SchemaConfigDelegatorConfigOnly import (
    config_only_delegator_config_desc,
    config_only_delegator_envelope_payload_desc,
)
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import (
    schema_plugin_check_evn_server_response_abstract_desc,
)
from argrelay.misc_helper_common.ObjectSchema import object_desc
from argrelay.plugin_config.ConfiguratorDefaultConfigSchema import configurator_default_config_desc
from argrelay.plugin_delegator.SchemaConfigDelegatorJumpAbstract import abstract_jump_delegator_config_desc
from argrelay.plugin_delegator.SchemaCustomDataDelegatorError import error_delegator_custom_data_desc
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_interp_factory_config_desc
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import func_tree_interp_config_desc
from argrelay.relay_server.UsageStatsEntrySchema import usage_stats_entry_desc
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc, redundant_servers_
from argrelay.schema_config_core_client.ConnectionConfigSchema import (
    connection_config_desc,
    server_host_name_,
    server_port_number_,
)
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import envelope_collection_desc
from argrelay.schema_config_core_server.MongoClientConfigSchema import mongo_client_config_desc
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.MongoServerConfigSchema import mongo_server_config_desc
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_core_server.ServerPluginControlSchema import server_plugin_control_desc
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_config_interp.FuncEnvelopeSchema import func_envelope_desc
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import function_envelope_instance_data_desc
from argrelay.schema_config_interp.InitControlSchema import init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc
from argrelay.schema_config_plugin.CheckEnvPluginConfigSchema import check_env_plugin_config_desc
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.test_infra import line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay_api_server_cli.schema_request.CallContextSchema import call_context_desc
from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_desc
from argrelay_api_server_cli.schema_response.AssignedValueSchema import assigned_value_desc
from argrelay_api_server_cli.schema_response.EnvelopeContainerSchema import envelope_container_desc
from argrelay_api_server_cli.schema_response.InterpResultSchema import interp_result_desc
from argrelay_api_server_cli.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay_api_server_cli.server_spec.const_int import DEFAULT_IP_ADDRESS, DEFAULT_PORT_NUMBER


class ThisTestClass(BaseTestClass):
    test_cases = [
        (line_no(), object_desc),
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
        (line_no(), plugin_config_desc),
        (line_no(), data_envelope_desc),
        (line_no(), func_envelope_desc),
        (line_no(), search_control_desc),
        (line_no(), init_control_desc),
        (line_no(), function_envelope_instance_data_desc),
        (line_no(), func_tree_interp_config_desc),
        (line_no(), arg_values_desc),
        (line_no(), interp_result_desc),
        (line_no(), assigned_value_desc),
        (line_no(), envelope_container_desc),
        (line_no(), error_delegator_custom_data_desc),
        (line_no(), abstract_jump_delegator_config_desc),
        (line_no(), server_plugin_control_desc),
        (line_no(), envelope_collection_desc),
        (line_no(), configurator_default_config_desc),
        (line_no(), config_only_loader_config_desc),
        (line_no(), base_config_delegator_config_desc),
        (line_no(), config_only_delegator_envelope_payload_desc),
        (line_no(), config_only_delegator_config_desc),
        (line_no(), func_config_desc),
        (line_no(), schema_plugin_check_evn_server_response_abstract_desc),
        (line_no(), usage_stats_entry_desc),
        (line_no(), check_env_plugin_config_desc),

        # FS_33_76_82_84 composite forest and its nodes:
        (line_no(), composite_forest_desc),
        (line_no(), base_node_desc),
        (line_no(), zero_arg_node_desc),
        (line_no(), interp_tree_node_desc),
        (line_no(), func_tree_node_desc),
        (line_no(), tree_path_node_desc),
    ]

    def test_type_desc_load_of_minimal_dict(self):
        """
        Ensure schema can load empty dict
        """

        for test_case in self.test_cases:
            with self.subTest(test_case):
                (line_number, type_desc) = test_case

                # TODO: Ensure (test) that minimal dict is minimal
                #       (by trying to remove any field and reload - it should fail).
                # TODO: Load minimal dict per schema (to test defaults are loaded):
                #       Currently, only test selected dict to load their minimal dict:
                if type_desc is configurator_default_config_desc:
                    type_desc.dict_schema.load({})

    def test_type_desc_example_is_loadable_and_dumpable(self):
        """
        Uses each schema definition to load and dump its own example.
        """

        for test_case in self.test_cases:
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
        `Schema.dump` cannot be used (without a workaround) as it does not preserve all extra keys.
        See `DataEnvelopeSchema` for details.
        """
        type_desc = data_envelope_desc

        orig_dict = type_desc.dict_example
        loaded_dict = type_desc.dict_schema.load(orig_dict)
        assert type(loaded_dict) is dict

        dumped_orig_json = type_desc.dict_schema.dumps(orig_dict, sort_keys = True)
        dumped_loaded_json = type_desc.dict_schema.dumps(loaded_dict, sort_keys = True)

        dumped_dict = type_desc.dict_schema.dump(loaded_dict)
        # Expect no problem:
        # `Schema.dump` does not preserve all keys of original `dict` - only those which mentioned in the schema
        # (but there is a special workaround to keep all keys):
        self.assertEqual(
            orig_dict,
            dumped_dict,
        )

        self.assertEqual(
            orig_dict,
            loaded_dict,
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

        client_config: ClientConfig = client_config_desc.obj_from_yaml_str(
            f"""
            {{
                "{redundant_servers_}": [
                    {{
                        "{server_host_name_}": "localhost",
                        "{server_port_number_}": 8787,
                    }}
                ]
            }}
            """
        )
        # Checking only one server index:
        server_index = 0
        self.assertEqual(
            client_config.use_local_requests,
            False,
        )
        self.assertEqual(
            client_config.optimize_completion_request,
            True,
        )
        self.assertEqual(
            client_config.redundant_servers[server_index].server_host_name,
            DEFAULT_IP_ADDRESS,
        )
        self.assertEqual(
            client_config.redundant_servers[server_index].server_port_number,
            DEFAULT_PORT_NUMBER,
        )
        self.assertEqual(
            client_config.show_pending_spinner,
            False,
        )
        self.assertEqual(
            client_config.spinless_sleep_sec,
            0.0,
        )
