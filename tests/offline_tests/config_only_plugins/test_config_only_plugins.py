from __future__ import annotations

import unittest

from argrelay.custom_integ.ConfigOnlyLoader import ConfigOnlyLoader
from argrelay.custom_integ.ConfigOnlyLoaderConfigSchema import collection_name_to_index_props_map_
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
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

    def test_validation_for_unused_data_envelope(self):
        """
        Test that unused data is not loaded.
        TODO: Why do we need that?
              Loaded data at least allows browsing via FS_74_69_61_79 get set data envelope.
        TODO: What we need is to ensure every `data_envelope` has `class_name` which is defined in `data_model`.
        TODO: We may check if `data_model` is used against any `search_control` just to avoid unused data.

        This test relies on `ConfigOnlyLoader` to load `data_envelope` with a class unused by anything.

        The validation should prevent starting server (unless `data_envelope` is used by some of
        `search_control`-s anywhere which should not be the case).
        """

        env_mock_builder = LocalClientEnvMockBuilder().set_reset_local_server(True)

        for add_unused_data_envelope in [
            False,
            True,
        ]:
            with self.subTest(add_unused_data_envelope):
                if add_unused_data_envelope:
                    class_name = "THIS_CLASS_IS_UNUSED"

                    # Change config to cause validation error:
                    plugin_config_dict = plugin_config_desc.dict_from_default_file()
                    instance_config_dict: dict = plugin_config_dict[
                        plugin_instance_entries_
                    ][
                        # TODO: TODO_62_75_33_41: do not hardcode `plugin_instance_id`:
                        f"{ConfigOnlyLoader.__name__}.default"
                    ][
                        plugin_config_
                    ]

                    instance_config_dict[
                        data_envelopes_
                    ].append({
                        envelope_payload_: {
                        },
                        ReservedPropName.envelope_class.name: class_name,
                    })

                    instance_config_dict[collection_name_to_index_props_map_][class_name] = []

                    env_mock_builder.set_plugin_config_dict(plugin_config_dict)

                    with self.assertRaises(ValueError) as cm:
                        self._init_local_server(env_mock_builder)
                    self.assertTrue(
                        cm.exception.args[0].startswith(
                            f"`collection_name` [{class_name}] "
                            f"of this `data_envelope` is not used by any any `search_control`:",
                        ),
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
