from typing import Union

from argrelay.enum_desc.CompType import CompType
from argrelay.test_infra import parse_line_and_cpos
from argrelay.test_infra.TestCase import TestCase


class ShellInputTestCase(TestCase):

    def __init__(
        self,
        line_no: int,
        case_comment: str,
    ):
        super().__init__(
            line_no,
            case_comment,
        )
        self.test_line: Union[str, None] = None
        self.command_line: Union[str, None] = None
        self.cursor_cpos: Union[int, None] = None
        self.comp_type: Union[CompType, None] = None

    def set_command_line(
        self,
        given_command_line: str,
    ):
        assert self.command_line is None
        self.command_line = given_command_line

    def set_cursor_cpos(
        self,
        given_cursor_cpos: int,
    ):
        assert self.cursor_cpos is None
        self.cursor_cpos = given_cursor_cpos

    def set_test_line(
        self,
        given_test_line: str,
    ):
        assert self.test_line is None
        assert self.command_line is None
        assert self.cursor_cpos is None
        self.test_line = given_test_line
        (
            self.command_line,
            self.cursor_cpos
        ) = parse_line_and_cpos(given_test_line)

    def set_comp_type(
        self,
        given_comp_type: CompType,
    ):
        assert self.comp_type is None
        self.comp_type = given_comp_type
