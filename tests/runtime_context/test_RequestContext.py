from unittest import TestCase

from argrelay.data_schema.RequestContextSchema import request_context_desc
from argrelay.meta_data.CompType import CompType
from argrelay.runtime_context.RequestContext import RequestContext
from argrelay.test_helper import line_no, parse_line_and_cpos


class ThisTestCase(TestCase):

    def test_to_json(self):
        # @formatter:off
        test_cases = [
            (
                line_no(), "basic conversion",
                "some_command prod amer upstream sdfg|  ", CompType.PrefixShown,
                '{"command_line": "some_command prod amer upstream sdfg  ", "cursor_cpos": 36, "comp_type": "PrefixShown", "is_debug_enabled": false}',
            ),
        ]
        # @formatter:on
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, case_comment, test_line, comp_type, expected_json) = test_case
                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
                request_ctx = RequestContext(
                    command_line = command_line,
                    cursor_cpos = cursor_cpos,
                    comp_type = comp_type,
                    is_debug_enabled = False,
                )
                actual_json = request_context_desc.object_schema.dumps(request_ctx)
                self.assertEqual(expected_json, actual_json)
