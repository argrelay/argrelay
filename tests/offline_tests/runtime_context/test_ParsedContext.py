from argrelay_test_infra.test_infra import (
    line_no,
    parse_line_and_cpos,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.EnvMockBuilder import default_test_parsed_context


class ThisTestClass(BaseTestClass):
    """
    Tests `FS_27_16_67_19` line syntax.
    """

    def test_parse_input(self):
        test_cases = [
            # blank:
            (line_no(), "|", -1, -1, "", -1, -1, [], "empty line"),
            (line_no(), "| ", -1, -1, "", -1, -1, [], "blank line len = 1, cpos = 0"),
            (line_no(), " |", -1, -1, "", -1, -1, [], "blank line len = 1, cpos = 1"),
            (line_no(), "|  ", -1, -1, "", -1, -1, [], "blank line len = 2, cpos = 0"),
            (line_no(), " | ", -1, -1, "", -1, -1, [], "blank line len = 2, cpos = 1"),
            (line_no(), "  |", -1, -1, "", -1, -1, [], "blank line len = 2, cpos = 2"),
            # 1 token, no leading delimiters, no trailing delimiters:
            (line_no(), "|a", 0, 1, "a", 0, -1, ["a"], ""),
            (line_no(), "a|", 0, 1, "a", 0, -1, ["a"], ""),
            # 1 token, no leading delimiters, has trailing delimiters:
            (line_no(), "|a ", 0, 1, "a", 0, -1, ["a"], ""),
            (line_no(), "a| ", 0, 1, "a", 0, -1, ["a"], ""),
            (line_no(), "a |", -1, -1, "", -1, 0, ["a"], ""),
            # 1 token, has leading delimiters, no trailing delimiters:
            (line_no(), "| a", -1, -1, "", -1, -1, ["a"], ""),
            (line_no(), " |a", 1, 2, "a", 0, -1, ["a"], ""),
            (line_no(), " a|", 1, 2, "a", 0, -1, ["a"], ""),
            # 1 token, has leading delimiters, has trailing delimiters:
            (line_no(), "| a ", -1, -1, "", -1, -1, ["a"], ""),
            (line_no(), " |a ", 1, 2, "a", 0, -1, ["a"], ""),
            (line_no(), " a| ", 1, 2, "a", 0, -1, ["a"], ""),
            (line_no(), " a |", -1, -1, "", -1, 0, ["a"], ""),
            # 2 tokens, no leading delimiters, no trailing delimiters:
            (line_no(), "|a b", 0, 1, "a", 0, -1, ["a", "b"], ""),
            (line_no(), "a| b", 0, 1, "a", 0, -1, ["a", "b"], ""),
            (line_no(), "a |b", 2, 3, "b", 1, 0, ["a", "b"], ""),
            (line_no(), "a b|", 2, 3, "b", 1, 0, ["a", "b"], ""),
            # 2 tokens, no leading delimiters, has trailing delimiters:
            (line_no(), "|a b ", 0, 1, "a", 0, -1, ["a", "b"], ""),
            (line_no(), "a| b ", 0, 1, "a", 0, -1, ["a", "b"], ""),
            (line_no(), "a |b ", 2, 3, "b", 1, 0, ["a", "b"], ""),
            (line_no(), "a b| ", 2, 3, "b", 1, 0, ["a", "b"], ""),
            (line_no(), "a b |", -1, -1, "", -1, 1, ["a", "b"], ""),
            # 2 tokens, has leading delimiters, no trailing delimiters:
            (line_no(), "| a b", -1, -1, "", -1, -1, ["a", "b"], ""),
            (line_no(), " |a b", 1, 2, "a", 0, -1, ["a", "b"], ""),
            (line_no(), " a| b", 1, 2, "a", 0, -1, ["a", "b"], ""),
            (line_no(), " a |b", 3, 4, "b", 1, 0, ["a", "b"], ""),
            (line_no(), " a b|", 3, 4, "b", 1, 0, ["a", "b"], ""),
            # 2 tokens, has leading delimiters, has trailing delimiters:
            (line_no(), "| a b ", -1, -1, "", -1, -1, ["a", "b"], ""),
            (line_no(), " |a b ", 1, 2, "a", 0, -1, ["a", "b"], ""),
            (line_no(), " a| b ", 1, 2, "a", 0, -1, ["a", "b"], ""),
            (line_no(), " a |b ", 3, 4, "b", 1, 0, ["a", "b"], ""),
            (line_no(), " a b| ", 3, 4, "b", 1, 0, ["a", "b"], ""),
            (line_no(), " a b |", -1, -1, "", -1, 1, ["a", "b"], ""),
            # 2 tokens, double length for both tokens and delimiters:
            (line_no(), "|  aa  bb  ", -1, -1, "", -1, -1, ["aa", "bb"], ""),
            (line_no(), " | aa  bb  ", -1, -1, "", -1, -1, ["aa", "bb"], ""),
            (line_no(), "  |aa  bb  ", 2, 4, "aa", 0, -1, ["aa", "bb"], ""),
            (line_no(), "  a|a  bb  ", 2, 4, "aa", 0, -1, ["aa", "bb"], ""),
            (line_no(), "  aa|  bb  ", 2, 4, "aa", 0, -1, ["aa", "bb"], ""),
            (line_no(), "  aa | bb  ", -1, -1, "", -1, 0, ["aa", "bb"], ""),
            (line_no(), "  aa  |bb  ", 6, 8, "bb", 1, 0, ["aa", "bb"], ""),
            (line_no(), "  aa  b|b  ", 6, 8, "bb", 1, 0, ["aa", "bb"], ""),
            (line_no(), "  aa  bb|  ", 6, 8, "bb", 1, 0, ["aa", "bb"], ""),
            (line_no(), "  aa  bb | ", -1, -1, "", -1, 1, ["aa", "bb"], ""),
            (line_no(), "  aa  bb  |", -1, -1, "", -1, 1, ["aa", "bb"], ""),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    test_line,
                    expected_tan_l_cpos,
                    expected_tan_r_cpos,
                    expected_tan_token_value,
                    expected_tan_token_ipos,
                    expected_prev_token_ipos,
                    expected_all_tokens,
                    case_comment,
                ) = test_case

                (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

                parsed_ctx = default_test_parsed_context(command_line, cursor_cpos)

                self.assertEqual(expected_tan_l_cpos, parsed_ctx.tan_token_l_cpos)
                self.assertEqual(expected_tan_r_cpos, parsed_ctx.tan_token_r_cpos)
                self.assertEqual(expected_tan_token_value, parsed_ctx.tan_token_value)
                self.assertEqual(expected_tan_token_ipos, parsed_ctx.tan_token_ipos)
                self.assertEqual(expected_prev_token_ipos, parsed_ctx.prev_token_ipos)
                self.assertEqual(expected_all_tokens, parsed_ctx.all_tokens)
