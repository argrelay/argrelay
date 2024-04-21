from argrelay.enum_desc.TokenType import get_token_type, TokenType
from argrelay.test_infra import line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass


class ThisTestClass(BaseTestClass):

    def test_get_token_type(self):
        test_cases = [
            (line_no(), ["KeyArg1:", "ValArg1", "PosArg1"], 0, TokenType.KeyArg, ""),
            (line_no(), ["KeyArg1:", "ValArg1", "PosArg1"], 1, TokenType.ValArg, ""),
            (line_no(), ["KeyArg1:", "ValArg1", "PosArg1"], 2, TokenType.PosArg, ""),
            (line_no(), ["KeyArg1:", "ValArg1", "KeyArg2:"], 2, TokenType.KeyArg, ""),
            (line_no(), ["KeyArg1:", "KeyArg2:", "ValArg2"], 2, TokenType.ValArg, ""),
            (line_no(), ["PosArg1", "PosArg2", "PosArg3"], 0, TokenType.PosArg, ""),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (line_number, all_tokens, token_ipos, expected_token_type, case_comment) = test_case
                actual_token_type = get_token_type(all_tokens, token_ipos)
                self.assertEqual(expected_token_type, actual_token_type)
