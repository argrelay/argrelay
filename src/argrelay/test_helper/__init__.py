"""
"""
import os
from contextlib import contextmanager
from inspect import getframeinfo, currentframe

test_data_ = "test_data"

# Enable/disable breakpoints programmatically:
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


@contextmanager
def change_to_known_repo_path(path_from_repo_root = "./tests"):
    """
    This function changes to known path within repo root.

    This allows any other code relying on the file access within the repo use reliable relative paths.
    """

    old_pwd = os.getcwd()
    try:
        # When IDE runs, CWD = "tests", when `tox` runs, CWD = [repo root], change to `tests` subdir:
        if os.path.basename(os.getcwd()) != "tests":
            os.chdir("tests")
        # Base path = repo root:
        os.chdir("..")
        # Desired path:
        os.chdir(path_from_repo_root)
        yield
    finally:
        os.chdir(old_pwd)
