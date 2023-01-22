"""
"""
from inspect import getframeinfo, currentframe

# Enable/Disable breakpoints programmatically:
__is_breakpoint_enabled = False


def enable_breakpoint():
    global __is_breakpoint_enabled
    __is_breakpoint_enabled = True


def disable_breakpoint():
    global __is_breakpoint_enabled
    __is_breakpoint_enabled = False


def is_breakpoint_enabled() -> bool:
    return __is_breakpoint_enabled


def line_no() -> int:
    """
    Get source line in the caller frame
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
