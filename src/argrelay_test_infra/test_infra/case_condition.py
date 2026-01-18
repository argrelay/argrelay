from __future__ import annotations

import argparse
import os
import pathlib

import pytest

from protoprimer.primer_kernel import str_to_bool

integ_test_env_var = "CI"
gui_test_env_var = "GUI_TEST"
env_test_env_var = "ENV_TEST"


def any_to_bool(v) -> bool:
    """
    Checks if given `str` value is set to `true`.
    """

    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if len(v) == 0:
            return False
        else:
            return str_to_bool(v)
    raise argparse.ArgumentTypeError(
        f"Unable to convert type [{type(v)}] to [{bool.__name__}]."
    )


is_integ_run = any_to_bool(os.environ.get(integ_test_env_var))
is_gui_run = any_to_bool(os.environ.get(gui_test_env_var))
is_env_run = any_to_bool(os.environ.get(env_test_env_var))


def skip_test_integ(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
) -> None:
    _skip_tests(
        parent_dir_abs_path,
        pytest_config,
        pytest_items,
        is_integ_run,
        integ_test_env_var,
    )


def skip_test_gui(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
) -> None:
    _skip_tests(
        parent_dir_abs_path,
        pytest_config,
        pytest_items,
        is_gui_run,
        gui_test_env_var,
    )


def skip_test_env(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
) -> None:
    _skip_tests(
        parent_dir_abs_path,
        pytest_config,
        pytest_items,
        is_env_run,
        env_test_env_var,
    )


def _skip_tests(
    parent_dir_abs_path: str,
    pytest_config,
    pytest_items,
    is_run: bool,
    env_var: str,
) -> None:
    """
    Skips all collected tests in this directory and its sub-directories if the given `is_run` is false.
    """

    reason_text = (
        f"Tests under `{parent_dir_abs_path}` skipped by default. "
        f"Run with environment variable `{env_var}` set to `true` to enable. "
    )

    if not is_run:
        skip_tests_in_curr_dir(parent_dir_abs_path, pytest_items, reason_text)


def skip_tests_in_curr_dir(
    parent_dir_abs_path: str,
    pytest_items,
    reason_text: str,
) -> None:

    skip_int_marker = pytest.mark.skip(reason=reason_text)

    for pytest_item in pytest_items:

        test_path: pathlib.Path
        if hasattr(pytest_item, "path"):
            test_path = pytest_item.path
        else:
            # legacy:
            test_path = pathlib.Path(pytest_item.fspath)

        if test_path.is_relative_to(parent_dir_abs_path):
            pytest_item.add_marker(skip_int_marker)
