from argrelay.client_spec.ShellContext import UNKNOWN_COMP_KEY, ShellContext
from argrelay.enum_desc.CompType import CompType
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.test_infra import line_no, parse_line_and_cpos
from argrelay.test_infra.BaseTestClass import BaseTestClass


class ThisTestClass(BaseTestClass):

    def test_to_json(self):
        """
        Test CallContext JSON-dump
        """

        test_cases = [
            (
                line_no(), "basic conversion",
                "some_command prod amer upstream sdfg|  ", CompType.PrefixShown,
                '{"server_action": "ProposeArgValues", "command_line": "some_command prod amer upstream sdfg  ", "cursor_cpos": 36, "comp_scope": "ScopeInitial", "is_debug_enabled": false}',
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, case_comment, test_line, comp_type, expected_json) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                call_ctx = ShellContext(
                    command_line = command_line,
                    cursor_cpos = cursor_cpos,
                    comp_type = comp_type,
                    is_debug_enabled = False,
                    comp_key = UNKNOWN_COMP_KEY,
                ).create_call_context()
                actual_json = call_context_desc.dict_schema.dumps(call_ctx)
                self.assertEqual(expected_json, actual_json)
