from unittest import TestCase

from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.test_helper import line_no


class ThisTestCase(TestCase):

    def test_type_desc_example_is_loadable_and_dumpable(self):
        test_cases = [
            (line_no(), request_context_desc),
            (line_no(), invocation_input_desc),
            (line_no(), plugin_entry_desc),
            # TODO: add all other `TypeDesc`s here
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, type_desc) = test_case
                loaded_obj = type_desc.dict_schema.load(type_desc.dict_example)
                dumped_dict = type_desc.dict_schema.dump(loaded_obj)
                # Compare via JSON strings:
                orig_json = type_desc.dict_schema.dumps(type_desc.dict_example, sort_keys = True)
                dumped_json = type_desc.dict_schema.dumps(dumped_dict, sort_keys = True)
                self.maxDiff = None
                self.assertEqual(
                    orig_json,
                    dumped_json,
                )
