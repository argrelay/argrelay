"""
"""
import os
from contextlib import contextmanager
from inspect import getframeinfo, currentframe, Traceback
from pathlib import PurePath

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


def line_no_from_ctor() -> int:
    """
    Same as `line_no` but used inside `TestCase` ctor (behind one more stack frame).
    """
    return getframeinfo(currentframe().f_back.f_back).lineno


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
    This function changes current dir to known path within repo root.

    This allows any other code accessing files by relative paths rely on the stable path within the repo.
    """

    old_pwd = os.getcwd()
    try:
        # When IDE runs, CWD is somewhere under "tests".
        # Keep climbing up until directory becomes "tests":
        if "tests" in PurePath(os.getcwd()).parts:
            while os.path.basename(os.getcwd()) != "tests":
                os.chdir("..")

        # When `tox` runs, CWD = [repo root]:
        if os.path.basename(os.getcwd()) != "tests":
            os.chdir("tests")

        # Now, when same baseline is set regardless `tox` or IDE, change to repo root:
        os.chdir("..")

        # Desired path:
        os.chdir(path_from_repo_root)
        yield
    finally:
        os.chdir(old_pwd)


def assert_test_func_name_embeds_prod_class_name(
    prod_class: type,
):
    """
    Ensure caller test function name contains given prod class name.
    """
    caller_func_name = currentframe().f_back.f_code.co_name
    simple_prod_class_name = prod_class.__name__.split(".")[-1]
    _assert_test_name_embeds_prod_name(simple_prod_class_name, caller_func_name)


def assert_test_module_name_embeds_prod_class_name(
    prod_class: type,
):
    """
    Ensure caller test module name contains given prod class name.
    """
    caller_frame = currentframe().f_back
    simple_test_module_name = caller_frame.f_globals["__name__"].split(".")[-1]
    simple_prod_class_name = prod_class.__name__.split(".")[-1]
    _assert_test_name_embeds_prod_name(simple_prod_class_name, simple_test_module_name)


def _assert_test_name_embeds_prod_name(
    prod_name: str,
    test_name: str,
):
    """
    This function ensures that names in prod code and test code do not diverge due to refactoring.

    That programmatically establishes relationship between prod code and test code via cross-references.
    The function should not be called directly (with strings which defeats the purpose as strings easily diverge).
    Instead, an appropriate wrapper function should be called with references (e.g. to classes).
    """
    assert prod_name in test_name
