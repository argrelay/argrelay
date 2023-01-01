"""
"""
from inspect import getframeinfo, currentframe

from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.ParsedContext import ParsedContext


def line_no() -> int:
    """
    Get source line in the callee frame
    """
    return getframeinfo(currentframe().f_back).lineno


def parse_line_and_cpos(test_line: str) -> (str, int):
    """
    Translate test line with pipe as cursor place into command line string and cursor char position (cpos)
    """
    assert test_line.count('|') == 1
    cursor_cpos = test_line.index('|')
    command_line = test_line.replace('|', "")
    return command_line, cursor_cpos


def default_test_input_context(command_line: str, cursor_cpos: int) -> InputContext:
    return InputContext(
        command_line = command_line,
        cursor_cpos = cursor_cpos,
        comp_type = CompType.PrefixShown,
        is_debug_enabled = False,
        run_mode = RunMode.CompletionMode,
        comp_key = str(0),
    )


def default_test_parsed_context(command_line: str, cursor_cpos: int) -> ParsedContext:
    return ParsedContext.from_instance(
        default_test_input_context(command_line, cursor_cpos),
    )
