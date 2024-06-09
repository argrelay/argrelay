from __future__ import annotations

from argrelay.composite_tree.CompositeForestSchema import tree_roots_
from argrelay.composite_tree.CompositeNodeSchema import sub_tree_, node_type_, func_id_
from argrelay.composite_tree.CompositeNodeType import CompositeNodeType
from argrelay.custom_integ.value_constants import desc_git_tag_func_
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory, tree_path_selector_prefix_
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import func_selector_tree_
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc, server_plugin_control_
from argrelay.schema_config_core_server.ServerPluginControlSchema import composite_forest_
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, plugin_instance_entries_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import LocalClientEnvMockBuilder
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_arg_assignments_and_suggestions_hidde_funcs(self):
        test_cases = [
            (
                line_no(), "relay_demo desc |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    0: {
                        f"{tree_path_selector_prefix_}{0}": AssignedValue("relay_demo", ArgSource.InitValue),
                        f"{tree_path_selector_prefix_}{1}": AssignedValue("desc", ArgSource.ExplicitPosArg),
                        f"{tree_path_selector_prefix_}{2}": [
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
                line_no(), "relay_demo desc |", CompType.DescribeArgs,
                # `CompType.DescribeArgs`: does not provide suggestion:
                None,
                {
                    0: {
                        f"{tree_path_selector_prefix_}{0}": AssignedValue("relay_demo", ArgSource.InitValue),
                        f"{tree_path_selector_prefix_}{1}": AssignedValue("desc", ArgSource.ExplicitPosArg),
                        # NOTE: even if it is single value, it is not assigned:
                        f"{tree_path_selector_prefix_}{2}": [
                            "retag",
                        ],
                        f"{tree_path_selector_prefix_}{3}": AssignedValue("qwer", ArgSource.ImplicitValue),
                    },
                    1: {},
                    2: None,
                },
                True,
                "TODO_39_25_11_76: Step 2: funcs are hidden",
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

                server_config_dict = server_config_desc.dict_from_default_file()
                plugin_config_dict = plugin_config_desc.dict_from_default_file()

                if is_func_hidden:
                    # Patch existing config with extra level:
                    server_config_dict[
                        server_plugin_control_
                    ][
                        composite_forest_
                    ][tree_roots_]["relay_demo"][sub_tree_][""][sub_tree_]["desc"][sub_tree_]["retag"] = {
                        node_type_: CompositeNodeType.tree_path_node.name,
                        sub_tree_: {
                            "qwer": {
                                node_type_: CompositeNodeType.func_tree_node.name,
                                func_id_: desc_git_tag_func_,
                            },
                        },
                    }

                    # TODO: FS_33_76_82_84 composite tree:
                    #       once composite tree is complete,
                    #       this extra (duplicated) config will not be required:
                    plugin_config_dict[plugin_instance_entries_][
                        f"{FuncTreeInterpFactory.__name__}.default"
                    ][plugin_config_][func_selector_tree_]["desc"]["retag"] = {
                        "qwer": desc_git_tag_func_,
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
