from __future__ import annotations

import unittest

from argrelay.custom_integ.BaseConfigDelegatorConfigSchema import func_configs_
from argrelay.custom_integ.ConfigOnlyDelegator import ConfigOnlyDelegator
from argrelay.custom_integ.ConfigOnlyLoader import ConfigOnlyLoader
from argrelay.custom_integ.ConfigOnlyLoaderConfigSchema import collection_name_to_index_props_map_
from argrelay.custom_integ.FuncConfigSchema import func_envelope_
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_, instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import search_control_list_
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, plugin_instance_entries_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
    mock_subprocess_popen,
    EnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


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
                        "severity_level": AssignedValue("ERROR", ArgSource.ExplicitPosArg),
                        "exit_code": AssignedValue("1", ArgSource.ExplicitPosArg),
                    },
                    2: {
                        "severity_level": AssignedValue("ERROR", ArgSource.DefaultValue),
                        "exit_code": AssignedValue("1", ArgSource.DefaultValue),
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

        This test relies on `ConfigOnlyDelegator` to specify `search_control`.

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
                        plugin_instance_entries_
                    ][
                        # TODO: TODO_62_75_33_41: do not hardcode `plugin_instance_id`:
                        f"{ConfigOnlyDelegator.__name__}.default"
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
                        keys_to_types_list_
                    ].append({
                        "some_key": UNKNOWN_INDEX_PROP_NAME,
                    })

                    env_mock_builder.set_plugin_config_dict(plugin_config_dict)

                    with self.assertRaises(ValueError) as cm:
                        self._init_local_server(env_mock_builder)
                    self.assertEqual(
                        (
                            f"`search_control` components not in `data_model`: "
                            f"`collection_name` [ConfigOnlyClass] "
                            # TODO: TODO_98_35_14_72: exclude `class_name` from `search_control`:
                            f"`class_name` [ConfigOnlyClass] "
                            f"`search_props`: {UNKNOWN_INDEX_PROP_NAME} "
                        ),
                        cm.exception.args[0],
                    )
                else:
                    # Should start successfully by default:
                    self._init_local_server(env_mock_builder)

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
