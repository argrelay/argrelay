from __future__ import annotations

from argrelay_api_server_cli.schema_response.AssignedValue import AssignedValue
from argrelay_app_client.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay_app_client.relay_client import __main__
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.ValueSource import ValueSource
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorConfigOnly import DelegatorConfigOnly
from argrelay_lib_server_plugin_core.plugin_delegator.FuncConfigSchema import func_envelope_
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaConfigDelegatorConfigOnly import func_configs_
from argrelay_lib_server_plugin_core.plugin_loader.ConfigOnlyLoader import ConfigOnlyLoader
from argrelay_lib_server_plugin_core.plugin_loader.ConfigOnlyLoaderConfigSchema import (
    envelope_class_to_collection_name_map_,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import search_control_list_
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import arg_name_to_prop_name_map_
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import (
    plugin_config_desc,
    server_plugin_instances_,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginEntrySchema import plugin_config_
from argrelay_test_infra.test_infra import (
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.EnvMockBuilder import (
    EnvMockBuilder,
    LocalClientEnvMockBuilder,
    mock_subprocess_popen,
)
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Test FS_49_96_50_77 config_only_plugins
    """

    same_test_data_per_class = "TD_63_37_05_36"  # demo

    def test_init_server(self):
        self._init_local_server(
            LocalClientEnvMockBuilder().set_reset_local_server(False),
        )

    def test_config_only_suggestions(self):

        test_cases = [
            (
                line_no(), "some_command config |", CompType.PrefixHidden,
                [
                    "double_execution",
                    "print_with_exit",
                    "print_with_io_redirect",
                    "print_with_level",
                ],
                "Suggest next step in path to select existing config-only function",
            ),
            (
                line_no(), "some_command config print_with_level |", CompType.PrefixHidden,
                [
                    "ERROR",
                    "INFO",
                    "WARN",
                ],
                "Suggest next step in path to select existing config-only function",
            ),
            (
                line_no(), "some_command config ERROR print_with_exit |", CompType.PrefixHidden,
                [
                    "1",
                    "2",
                ],
                "Suggest next step in path to select existing config-only function",
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

                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    None,
                    None,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )


    def test_FS_49_96_50_77_config_only_with_FS_72_53_55_13_default_overrides(self):
        test_cases = [
            (
                line_no(), "some_command config double_execution ERROR 1 |", CompType.DescribeArgs,
                {
                    1: {
                        "severity_level": AssignedValue("ERROR", ValueSource.explicit_offered_arg),
                        "exit_code": AssignedValue("1", ValueSource.explicit_offered_arg),
                    },
                    2: {
                        "severity_level": AssignedValue("ERROR", ValueSource.default_value),
                        "exit_code": AssignedValue("1", ValueSource.default_value),
                    },
                    3: None,
                },
                {
                    2: {
                        "severity_level": [
                            "ERROR",
                            "INFO",
                            "WARN",
                        ],
                        "exit_code": [
                            "0",
                            "1",
                            "2",
                        ],
                    },
                    3: None,
                },
                None,
                "FS_72_53_55_13: Provide options hidden by defaults.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    expected_suggestions,
                    case_comment,
                ) = test_case
                self.verify_output_via_local_client(
                    self.__class__.same_test_data_per_class,
                    test_line,
                    comp_type,
                    expected_suggestions,
                    container_ipos_to_expected_assignments,
                    container_ipos_to_options_hidden_by_default_value,
                    None,
                    None,
                    None,
                    LocalClientEnvMockBuilder().set_reset_local_server(False),
                )

    def test_config_only_invocation(self):
        """
        NOTE: These tests only assert command line to be executed externally: exit_code, stderr, stdout are mocked.
        """

        test_cases = [
            (
                line_no(), "some_command config ERROR print_with_level 1 |", CompType.InvokeAction,
                {
                    """
echo \"ERROR: text message C\"
""": (
                        0,
                        "text message C",
                        "",
                    ),
                },
                "Assert (mocked) command execution with exit code == 0",
            ),
            (
                line_no(), "some_command config ERROR print_with_exit 2 |", CompType.InvokeAction,
                {
                    """
echo \"text message D\"
exit 2

""": (
                        2,
                        "ERROR: text message D",
                        "",
                    ),
                },
                "Assert (mocked) command execution with exit code != 0",
            ),
            (
                line_no(), "some_command config print_with_io_redirect ERROR 1 |", CompType.InvokeAction,
                {
                    """
if [[ 1 -eq 0 ]]
then
    echo \"text message C\" 1>&1
else
    echo \"text message C\" 1>&2
fi
exit 1

""": (
                        1,
                        "text message C",
                        "",
                    ),
                },
                "Assert (mocked) command with IO redirection (but it is not executed)",
            ),
        ]

        self._init_local_server(
            LocalClientEnvMockBuilder().set_reset_local_server(False),
        )

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    comp_type,
                    popen_mock_config,
                    case_comment,
                ) = test_case

                with mock_subprocess_popen(popen_mock_config) as popen_mock:
                    with self.assertRaises(SystemExit) as cm:
                        self.verify_output_via_local_client(
                            self.__class__.same_test_data_per_class,
                            test_line,
                            comp_type,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            LocalClientEnvMockBuilder().set_reset_local_server(False),
                        )
                    expected_exit_code = next(iter(popen_mock_config.values()))[0]
                    self.assertEqual(cm.exception.code, expected_exit_code)

    def test_validation_for_dangling_search_prop(self):
        """
        Test that validation preventing `search_control` referencing unknown `index_prop`-s works.

        This test relies on `DelegatorConfigOnly` to specify `search_control`.

        Server should not start if `search_prop` does not exists in `index_prop`-s.
        """

        env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(True)

        for add_dangling_search_prop in [
            False,
            True,
        ]:
            with self.subTest(add_dangling_search_prop):
                if add_dangling_search_prop:
                    UNKNOWN_INDEX_PROP_NAME = "UNKNOWN_INDEX_PROP_NAME"

                    # Change config to cause validation error:
                    plugin_config_dict = plugin_config_desc.dict_from_default_file()
                    instance_config_dict: dict = plugin_config_dict[
                        server_plugin_instances_
                    ][
                        # TODO: TODO_62_75_33_41: do not hardcode `plugin_instance_id`:
                        f"{DelegatorConfigOnly.__name__}.default"
                    ][
                        plugin_config_
                    ]

                    instance_config_dict[
                        func_configs_
                    ][
                        "func_id_print_with_severity_level"
                    ][
                        func_envelope_
                    ][
                        instance_data_
                    ][
                        search_control_list_
                    ][
                        0
                    ][
                        arg_name_to_prop_name_map_
                    ].append({
                        "some_arg_name": UNKNOWN_INDEX_PROP_NAME,
                    })

                    env_mock_builder.set_plugin_config_dict(plugin_config_dict)

                    with self.assertRaises(ValueError) as cm:
                        self._init_local_server(env_mock_builder)
                    self.assertEqual(
                        (
                            f"`search_control` components not in `index_model`: "
                            f"`collection_name` [class_config_only] "
                            f"`search_props`: {UNKNOWN_INDEX_PROP_NAME} "
                        ),
                        cm.exception.args[0],
                    )
                else:
                    # Should start successfully by default:
                    self._init_local_server(env_mock_builder)

    def test_config_only_loaded_data(
        self,
    ):
        """
        Start the server, run (irrelevant) command, inspect loaded data
        """

        test_cases = [
            (
                line_no(),
                "class_config_only",
                {
                    "severity_level": "ERROR",
                },
                2,
                f"Query `data_envelope` of `class_config_only` without "
                f"specified `{ReservedPropName.envelope_class.name}`.",
            ),
            (
                line_no(),
                "class_config_only",
                {
                    ReservedPropName.envelope_class.name: "class_config_only",
                    "severity_level": "ERROR",
                },
                2,
                f"Query `data_envelope` of `class_config_only` with "
                f"specified `{ReservedPropName.envelope_class.name}`.",
            ),
            (
                line_no(),
                "class_output_format",
                {
                },
                4,
                f"Query `data_envelope` of `class_output_format` (without any query criteria).",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    class_name,
                    query_dict,
                    result_size,
                    case_comment,
                ) = test_case

                # Get `envelope_class_to_collection_name_map` config of FS_49_96_50_77 config_only_loader plugin:
                plugin_config_dict = plugin_config_desc.dict_from_default_file()
                instance_config_dict: dict = plugin_config_dict[
                    server_plugin_instances_
                ][
                    # TODO: TODO_62_75_33_41: do not hardcode `plugin_instance_id`:
                    f"{ConfigOnlyLoader.__name__}.default"
                ][
                    plugin_config_
                ]
                envelope_class_to_collection_name_map: dict[str, str] = instance_config_dict[
                    envelope_class_to_collection_name_map_
                ]

                test_line = "some_command config |"
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                comp_type = CompType.PrefixHidden
                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_reset_local_server(True)
                    .set_command_line(command_line)
                    .set_cursor_cpos(cursor_cpos)
                    .set_comp_type(comp_type)
                )

                with env_mock_builder.build():
                    command_obj: ClientCommandLocal = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)
                    query_engine = command_obj.local_server.query_engine

                    collection_name = envelope_class_to_collection_name_map.get(class_name)
                    data_envelopes = query_engine.query_data_envelopes(
                        collection_name,
                        query_dict,
                    )
                    for data_envelope in data_envelopes:
                        for query_prop in query_dict:
                            self.assertEqual(
                                query_dict[query_prop],
                                data_envelope[query_prop],
                            )
                    self.assertEqual(
                        result_size,
                        len(data_envelopes),
                    )

    def _init_local_server(
        self,
        env_mock_builder: EnvMockBuilder,
    ):
        """
        Init `LocalServer` (for one or all subsequent `test_cases`).
        """

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
