from __future__ import annotations

from marshmallow import ValidationError

from argrelay_lib_server_plugin_core.plugin_interp.NoopInterpFactory import NoopInterp
from argrelay_lib_server_plugin_demo.demo_git.GitRepoLoader import GitRepoLoader
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import (
    plugin_config_desc,
    server_plugin_instances_,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginEntrySchema import (
    plugin_class_name_,
    plugin_enabled_,
    plugin_entry_desc,
    plugin_module_name_,
)
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):

    def test_from_yaml_str(self):
        """
        This is not a test of `TypeDesc` specifically.
        It tests assumptions of schema validation.
        It uses `PluginEntrySchema` with `TypeDesc` to trigger validation
        (and `PluginEntrySchema` has all types of fields: required, optional, arbitrary `dict`).
        """

        test_cases = [
            (
                line_no(), "basic sample",
                {
                    plugin_enabled_: True,
                    plugin_module_name_: NoopInterp.__module__,
                    plugin_class_name_: NoopInterp.__name__,
                },
                {
                    plugin_enabled_: True,
                    plugin_module_name_: NoopInterp.__module__,
                    plugin_class_name_: NoopInterp.__name__,
                },
                None,
            ),
            (
                line_no(), "demo test data: expanded (realistic) sample",
                plugin_config_desc.dict_from_default_file()[server_plugin_instances_][
                    f"{GitRepoLoader.__name__}.default"
                ],
                {
                    plugin_module_name_: GitRepoLoader.__module__,
                },
                None,
            ),
            (
                line_no(), f"without required field `{plugin_module_name_}`",
                {
                    plugin_enabled_: True,
                    plugin_class_name_: NoopInterp.__name__,
                },
                None,
                ValidationError,
            ),
            (
                line_no(), "with extra key (`whatever_extra_key`) which is not allowed",
                {
                    plugin_enabled_: True,
                    plugin_module_name_: NoopInterp.__module__,
                    plugin_class_name_: NoopInterp.__name__,
                    "whatever_extra_key": "whatever_extra_val",
                },
                None,
                ValidationError,
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    case_comment,
                    input_dict,
                    expected_dict_part,
                    expected_exception,
                ) = test_case
                if not expected_exception:
                    static_data = plugin_entry_desc.obj_from_input_dict(input_dict)

                    # Assert those files which were specified in the `expected_dict_part`:
                    for key_to_verify in expected_dict_part:
                        self.assertEqual(expected_dict_part[key_to_verify], getattr(static_data, key_to_verify))

                else:
                    self.assertIsNone(
                        expected_dict_part,
                        self.confusing_result_presence_msg,
                    )
                    with self.assertRaises(expected_exception):
                        plugin_entry_desc.obj_from_input_dict(input_dict)
