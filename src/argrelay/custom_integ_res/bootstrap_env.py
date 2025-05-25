#!/usr/bin/env python3
"""
NOTE: The script must be run with Python 3.
      Ensure that `python3` is in `PATH` for shebang to work.

TODO: TODO_11_66_62_70: python_bootstrap: this is an experimental alternative to `bootstrap_env.bash`.

See more:
*   FS_28_84_41_40: flexible bootstrap

Typical usage:
    ./exe/bootstrap_env.py

To initialize the env with specific Python version:
    /path/to/pythonX ./exe/bootstrap_env.py

"""

import argparse
import logging
import os
import sys
import venv
from datetime import datetime
from pathlib import (
    Path,
    PurePath,
)

logger = logging.getLogger()


def main():
    configure_logger()
    parsed_args = init_arg_parser().parse_args()

    ensure_argrelay_dir()
    ensure_conf_dir(parsed_args.target_dst_dir_path)
    recurse_with_required_python_interpreter()
    ensure_min_python_version()


def init_arg_parser():

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    arg_parser = argparse.ArgumentParser(
        description="Bootstraps the argrelay env in current directory as `argrelay_dir` `@/`."
    )
    arg_parser.add_argument(
        "--recursion_flag",
        type=str2bool,
        nargs="?",
        const=False,
        default=False,
        help=f"Indicate recursion to prevent infinite recursion (default: {False}).",
    )
    arg_parser.add_argument(
        # TODO: This should be changed for Python (vs Bash) to only ensure `venv` is activate-able.
        "--activate_venv_only_flag",
        type=str2bool,
        nargs="?",
        const=False,
        default=False,
        help=f"Run only until `venv` is activated and exit (default: {False}).",
    )
    arg_parser.add_argument(
        "target_dst_dir_path",
        nargs="?",
        default=None,
        help="Path to one of the dirs (normally under `@/dst/`) to be used as target for `@/conf/` symlink.",
    )
    return arg_parser


def get_argrelay_dir():
    return os.getcwd()


def get_path_to_python_or_default():
    path_to_python_path = os.path.join(
        get_argrelay_dir(),
        "conf",
        "python_env.path_to_python.conf.txt",
    )
    if os.path.isfile(path_to_python_path):
        path_to_python_value = read_line_file(path_to_python_path)
    else:
        path_to_curr_python = get_path_to_curr_python()
        path_to_venv_value = get_path_to_venv_or_default()
        if is_sub_path(path_to_curr_python, path_to_venv_value):
            # Already inside `venv`, but `path_to_python_path` still does not exists:
            raise AssertionError(
                f"Current `python` interpreter [{path_to_curr_python}] is already under `venv` [{path_to_venv_value}], "
                f"while the `path_to_python` file [{path_to_python_path}] still does not exists. "
                f"This is not expected - deactivate `venv` and re-run the `@/exe/bootstrap_env.py`. "
            )
        else:
            # If not inside `venv`, save path of current `python` interpreter as default:
            ensure_min_python_version()
            write_line_file(path_to_python_path, path_to_curr_python)
            path_to_python_value = path_to_curr_python

    if not os.path.isabs(path_to_python_value):
        path_to_python_value = os.path.join(
            get_argrelay_dir(),
            path_to_python_value,
        )

    return path_to_python_value


def get_path_to_venv_or_default():
    path_to_venv_path = os.path.join(
        get_argrelay_dir(),
        "conf",
        "python_env.path_to_venv.conf.txt",
    )
    if os.path.isfile(path_to_venv_path):
        path_to_venv_value = read_line_file(path_to_venv_path)
    else:
        path_to_venv_value = os.path.join(
            "venv",
        )
        write_line_file(path_to_venv_path, path_to_venv_value)

    if not os.path.isabs(path_to_venv_value):
        path_to_venv_value = os.path.join(
            get_argrelay_dir(),
            path_to_venv_value,
        )

    return path_to_venv_value


def is_sub_path(abs_sub_path, abs_base_base):
    try:
        PurePath(abs_sub_path).relative_to(PurePath(abs_base_base))
        return True
    except ValueError:
        return False


def get_path_to_curr_python():
    return sys.executable


def ensure_argrelay_dir():
    signature_file_path = os.path.join(get_argrelay_dir(), "exe", "bootstrap_env.py")
    if not os.path.isfile(signature_file_path):
        raise AssertionError(
            f"The `argrelay_dir` `@/` [{get_argrelay_dir()}] does not contain the required signature file [{signature_file_path}]"
        )


def ensure_conf_dir(
    target_dst_dir_path: str,
):
    conf_symlink_path = os.path.join(get_argrelay_dir(), "conf")
    if os.path.exists(conf_symlink_path):
        if os.path.islink(conf_symlink_path):
            if os.path.isdir(conf_symlink_path):
                if target_dst_dir_path is None:
                    pass
                else:
                    conf_dir_path = os.readlink(conf_symlink_path)
                    if target_dst_dir_path == conf_dir_path:
                        pass
                    else:
                        raise AssertionError(
                            f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{target_dst_dir_path}]."
                        )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{conf_symlink_path}] target is not a directory.",
                )
        else:
            raise AssertionError(
                f"The `@/conf/` [{conf_symlink_path}] is not a symlink.",
            )
    else:
        if target_dst_dir_path is None:
            raise AssertionError(
                f"The `@/conf/` dir does not exists and `target_dst_dir_path` is not provided - see `--help`.",
            )
        else:
            ensure_allowed_conf_symlink_target(target_dst_dir_path)
            os.symlink(target_dst_dir_path, conf_symlink_path)


def ensure_allowed_conf_symlink_target(
    target_dst_dir_path: str,
):
    """
    Raises exception if the target of the `@/conf/` symlink is not allowed.

    NOTE:
    At the moment, only targets under `argrelay_dir` (under `@/`) are allowed.
    This is not a strict requirement and can be relaxed in the future.
    """
    if os.path.isabs(target_dst_dir_path):
        raise AssertionError(
            f"Target for `@/conf/` symlink [{target_dst_dir_path}] must not be absolute path."
        )
    elif ".." in Path(target_dst_dir_path).parts:
        raise AssertionError(
            f"Target for `@/conf/` symlink [{target_dst_dir_path}] must not contain `..` path segments."
        )
    elif not os.path.isdir(target_dst_dir_path):
        raise AssertionError(
            f"Target for `@/conf/` symlink [{target_dst_dir_path}] must lead to a directory."
        )
    return True


def recurse_with_required_python_interpreter():
    """
    Recursively runs this script inside the Python interpreter required by the user.

    The Python interpreter required by the user is saved into
    the `@/conf/python_env.path_to_python.conf.txt` file,
    and it matches the interpreter the bootstrap script is executed with at the moment.
    """

    path_to_python_value = get_path_to_python_or_default()
    path_to_venv_value = get_path_to_venv_or_default()

    if is_sub_path(path_to_python_value, path_to_venv_value):
        raise AssertionError(
            f"The `path_to_python` [{path_to_python_value}] is a sub-path of the `path_to_venv` [{path_to_venv_value}]. "
            f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
            f"Specify different `path_to_python` (e.g. `/usr/bin/python3`). "
            f"Alternatively, remove `@/conf/python_env.path_to_python.conf.txt` and re-run `@/exe/bootstrap_env.py` "
            f"to re-create it automatically. "
        )

    venv_path_to_python = os.path.join(
        path_to_venv_value,
        "bin",
        "python",
    )
    path_to_curr_python = get_path_to_curr_python()
    if is_sub_path(path_to_curr_python, path_to_venv_value):
        # If already under `venv`, nothing to do - just ensure `python` is from the correct `venv` path.
        if path_to_curr_python != venv_path_to_python:
            raise AssertionError(
                f"Current `python` interpreter [{path_to_curr_python}] points under `venv` [{path_to_venv_value}], "
                f"but it does not match expected interpreter there [{venv_path_to_python}]."
            )
    else:
        if path_to_curr_python != path_to_python_value:
            logger.info(
                f"switching from current `python` interpreter [{path_to_curr_python}] to required one [{path_to_python_value}]"
            )
            os.execv(
                path_to_python_value,
                [
                    path_to_python_value,
                    *sys.argv,
                ],
            )
        else:
            if not os.path.exists(path_to_venv_value):
                logger.info(f"creating `venv` [{path_to_venv_value}]")
                venv.create(
                    path_to_venv_value,
                    with_pip=True,
                )
            else:
                logger.info(f"reusing existing `venv` [{path_to_venv_value}]")
            logger.info(
                f"switching from current `python` interpreter [{path_to_python_value}] to `venv` interpreter [{venv_path_to_python}]"
            )
            os.execv(
                venv_path_to_python,
                [
                    venv_path_to_python,
                    *sys.argv,
                ],
            )


def write_line_file(file_path, file_line):
    assert os.path.isabs(file_path)
    with open(file_path, "w") as line_file:
        line_file.write(file_line)
        line_file.write("\n")


def read_line_file(file_path):
    assert os.path.isabs(file_path)
    with open(file_path, "r", encoding="utf-8") as line_file:
        file_line = line_file.read().strip()
    return file_line


def ensure_min_python_version():
    """
    Ensure the running Python interpreter is >= (major, minor, patch).
    """

    # FS_84_11_73_28: supported python versions:
    version_tuple: tuple[int, int, int] = (3, 8, 0)

    if sys.version_info < version_tuple:
        raise AssertionError(
            f"The version of Python used [{sys.version_info}] is below the min required [{version_tuple}]"
        )


class CustomFormatter(logging.Formatter):
    """
    Custom formatter with color and proper timestamp.
    """

    def __init__(
        self,
    ):
        # noinspection SpellCheckingInspection
        super().__init__(
            fmt="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d %(message)s",
        )

    # noinspection SpellCheckingInspection
    def formatTime(
        self,
        log_record,
        datefmt=None,
    ):
        # Format date without millis:
        formatted_timestamp = datetime.fromtimestamp(log_record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Append millis with dot `.` as a separator:
        return f"{formatted_timestamp}.{int(log_record.msecs):03d}"

    # ANSI escape codes for colors:
    color_reset = "\033[0m"
    color_set = {
        # cyan:
        "DEBUG": "\033[36m",
        # green:
        "INFO": "\033[32m",
        # yellow:
        "WARNING": "\033[33m",
        # red:
        "ERROR": "\033[31m",
        # bold red:
        "CRITICAL": "\033[1;31m",
    }

    def format(self, log_record):
        log_color = self.color_set.get(log_record.levelname, self.color_reset)
        log_msg = super().format(log_record)
        return f"{log_color}{log_msg}{self.color_reset}"


def configure_logger() -> None:
    custom_logger = logging.getLogger()
    custom_logger.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.INFO)
    log_formatter = CustomFormatter()
    stderr_handler.setFormatter(log_formatter)
    custom_logger.addHandler(stderr_handler)

    # Make all warnings be captured by the logging subsystem:
    logging.captureWarnings(True)


if __name__ == "__main__":
    main()
