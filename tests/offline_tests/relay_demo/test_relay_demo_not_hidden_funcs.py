from __future__ import annotations

import json
from copy import deepcopy

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.SpecialChar import SpecialChar
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorConfigOnly import DelegatorConfigOnly
from argrelay_lib_server_plugin_core.plugin_delegator.FuncConfigSchema import func_envelope_
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaConfigDelegatorConfigOnly import func_configs_
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import (
    FuncTreeInterpFactory,
    tree_step_prop_name_prefix_,
)
from argrelay_lib_server_plugin_demo.demo_git.DelegatorGitRepoDescTag import func_id_desc_git_tag_
from argrelay_schema_config_server.runtime_data_server_app.CompositeNodeType import CompositeNodeType
from argrelay_schema_config_server.schema_config_server_app.CompositeForestSchema import tree_roots_
from argrelay_schema_config_server.schema_config_server_app.CompositeNodeSchema import (
    func_id_,
    node_type_,
    sub_tree_,
)
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import (
    server_config_desc,
    server_plugin_control_,
)
from argrelay_schema_config_server.schema_config_server_app.ServerPluginControlSchema import composite_forest_
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import (
    plugin_config_desc,
    server_plugin_instances_,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginEntrySchema import plugin_config_
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EnvMockBuilder,
    LocalClientEnvMockBuilder,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_start_server(self):
        env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(True)
        self._start_server(env_mock_builder)

    def test_arg_assignments_does_not_hide_funcs(self):
        test_cases = [
            (
                line_no(), "some_command desc |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    0: {
                        f"{tree_step_prop_name_prefix_}{0}": AssignedValue("some_command", ValueSource.init_value),
                        f"{tree_step_prop_name_prefix_}{1}": AssignedValue("desc", ValueSource.explicit_offered_arg),
                        f"{tree_step_prop_name_prefix_}{2}": [
                            "commit",
                            "host",
                            "service",
                            "tag",
                        ],
                    },
                    1: None,
                },
                False,
                "TODO_39_25_11_76: Step 1: funcs are not hidden",
            ),
            (
                line_no(), "some_command desc |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    0: {
                        f"{tree_step_prop_name_prefix_}{0}": AssignedValue("some_command", ValueSource.init_value),
                        f"{tree_step_prop_name_prefix_}{1}": AssignedValue("desc", ValueSource.explicit_offered_arg),
                        f"{tree_step_prop_name_prefix_}{2}": [
                            "commit",
                            "host",
                            "retag",
                            "service",
                            "tag",
                        ],
                        f"{tree_step_prop_name_prefix_}{3}": [
                            "qwer",
                            SpecialChar.NoPropValue.value,
                        ],
                    },
                    1: None,
                },
                True,
                "TODO_39_25_11_76: Step 2: funcs are still not hidden",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    is_func_hidden,
                    case_comment,
                ) = test_case

                server_config_dict = deepcopy(server_config_desc.dict_from_default_file())
                plugin_config_dict = deepcopy(plugin_config_desc.dict_from_default_file())

                # TODO: clean this up after investigation:
                if False:
                    func_selector_tree_ = "func_selector_tree"
                    val_a = plugin_config_dict[server_plugin_instances_][
                        f"{FuncTreeInterpFactory.__name__}.default"
                    ][plugin_config_][func_selector_tree_]["some_command"][""]
                    val_b = plugin_config_dict[server_plugin_instances_][
                        f"{FuncTreeInterpFactory.__name__}.default"
                    ][plugin_config_][func_selector_tree_]["some_command"]["duplicates"][""]
                    print("1:", id(val_a))
                    print("2:", id(val_b))
                    # TODO: this is impossible (after deepcopy):
                    assert id(val_a) == id(val_b), "this should not happen but it does"
                    # TODO: fixing the issue above (by dumping and re-loading)
                    plugin_config_dict = json.loads(json.dumps(plugin_config_dict))
                    val_a = plugin_config_dict[server_plugin_instances_][
                        f"{FuncTreeInterpFactory.__name__}.default"
                    ][plugin_config_][func_selector_tree_]["some_command"][""]
                    val_b = plugin_config_dict[server_plugin_instances_][
                        f"{FuncTreeInterpFactory.__name__}.default"
                    ][plugin_config_][func_selector_tree_]["some_command"]["duplicates"][""]
                    print("1:", id(val_a))
                    print("2:", id(val_b))
                    assert id(val_a) != id(val_b), "this should not happen but it does"

                if is_func_hidden:
                    # Patch existing config with extra level:
                    server_config_dict[
                        server_plugin_control_
                    ][composite_forest_][tree_roots_]["some_command"][sub_tree_][""][sub_tree_][
                        "desc"
                    ][sub_tree_]["retag"] = {
                        node_type_: CompositeNodeType.tree_path_node.name,
                        sub_tree_: {
                            "qwer": {
                                node_type_: CompositeNodeType.func_tree_node.name,
                                func_id_: func_id_desc_git_tag_,
                            },
                        },
                    }

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder()
                    .set_reset_local_server(True)
                    .set_server_config_dict(server_config_dict)
                    .set_plugin_config_dict(plugin_config_dict),
                )

    def test_validation_for_plugin_search_control_with_func_envelope_having_missing_props(self):
        """
        This test relies on `DelegatorConfigOnly` to remove some `prop_name`-s in its `func_envelope`.

        TODO: TODO_39_25_11_76: `data_envelope`-s with missing props.

        The validation should prevent using any `func_envelope` which does not contain `prop_name`-s
        used by some of `search_control`-s anywhere (e.g. by `search_control` used by some plugin).
        """

        env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(True)

        for is_missing_prop in [
            False,
            True,
        ]:
            with self.subTest(is_missing_prop):
                if is_missing_prop:
                    # Change config to cause validation error:
                    plugin_config_dict = plugin_config_desc.dict_from_default_file()
                    func_envelope = plugin_config_dict[
                        server_plugin_instances_
                    ][
                        # TODO: TODO_62_75_33_41: do not hardcode `plugin_instance_id`:
                        f"{DelegatorConfigOnly.__name__}.default"
                    ][
                        plugin_config_
                    ][
                        func_configs_
                    ][
                        # Any `func_id` from the config:
                        "func_id_print_with_severity_level"
                    ][
                        func_envelope_
                    ]
                    del func_envelope["func_state"]
                    env_mock_builder.set_plugin_config_dict(plugin_config_dict)

                    with self.assertRaises(ValueError) as cm:
                        self._start_server(env_mock_builder)
                    self.assertTrue(
                        cm.exception.args[0].startswith(
                            "`data_envelope` of `collection_name` [class_function] does not have `prop_name` [func_state] while another one had:",
                        ),
                    )
                else:
                    # Should start successfully by default:
                    self._start_server(env_mock_builder)

    def _start_server(
        self,
        env_mock_builder: EnvMockBuilder,
    ):
        self.verify_output_via_local_client(
            self.__class__.same_test_data_per_class,
            "some_command |",
            CompType.PrefixShown,
            None,
            None,
            None,
            None,
            None,
            None,
            env_mock_builder,
        )
