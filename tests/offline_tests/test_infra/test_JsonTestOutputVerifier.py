from icecream import ic
from jsonpath_ng import DatumInContext

from argrelay_api_server_cli.schema_response.InterpResultSchema import (
    consumed_token_buckets_,
)
from argrelay_api_server_cli.schema_response.InvocationInputSchema import (
    delegator_plugin_entry_,
    invocation_input_desc,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginEntrySchema import (
    plugin_config_,
    plugin_module_name_,
)
from argrelay_test_infra.test_infra import line_no
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.JsonTestOutputVerifier import JsonTestOutputVerifier


class ThisTestClass(BaseTestClass):

    @staticmethod
    def print_m(m: DatumInContext):
        ic(m)

    def test_assert_via_json_query(self):
        """
        Test assumptions that `JsonTestOutputVerifier` actually assert things as expected.
        """

        sample_dict = invocation_input_desc.dict_example

        test_cases = [
            (
                line_no(),
                sample_dict,
                JsonTestOutputVerifier().add_verifier(
                    f"$.{delegator_plugin_entry_}.{plugin_module_name_}",
                    lambda m: self.print_m(m),
                    lambda m: self.assertEqual(1, len(m)),
                    lambda m: self.assertEqual("SomePluginModule", m[0].value),
                ),
                "Assert single value.",
            ),
            (
                line_no(),
                sample_dict,
                JsonTestOutputVerifier()
                .add_verifier(
                    f"$.{delegator_plugin_entry_}.{plugin_config_}",
                    lambda m: self.assertEqual(1, len(m)),
                )
                .add_verifier(
                    f"$.{plugin_config_}",
                    lambda m: self.print_m(m),
                    lambda m: self.assertEqual(0, len(m)),
                ),
                f"No `{plugin_config_}` key at root `dict` level",
            ),
            (
                line_no(),
                sample_dict,
                JsonTestOutputVerifier().add_verifier(
                    f"$.{consumed_token_buckets_}.[*]",
                    lambda m: self.print_m(m),
                    lambda m: self.assertEqual(2, len(m)),
                    lambda m: self.assertEqual(4, len(m[0].value)),
                    lambda m: self.assertEqual(0, len(m[1].value)),
                    lambda m: self.assertEqual(0, m[0].value[0]),
                    lambda m: self.assertEqual(2, m[0].value[1]),
                    lambda m: self.assertEqual(3, m[0].value[2]),
                    lambda m: self.assertEqual(4, m[0].value[3]),
                ),
                f"Assert every value in `{consumed_token_buckets_}` list.",
            ),
        ]

        for test_case in test_cases:
            with self.subTest(f"line:{test_case[0]}"):
                (
                    line_number,
                    json_dict,
                    json_verifier,
                    case_comment,
                ) = test_case

                data_obj = invocation_input_desc.dict_schema.load(json_dict)
                json_str = invocation_input_desc.dict_schema.dumps(data_obj)
                json_verifier.verify_all(json_str)
