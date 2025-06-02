#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 uvsmtid@gmail.com
"""

NOTE: The script must be run with Python 3.
      Ensure that `python3` is in `PATH` for shebang to work.
      Alternatively, run under specific `python` interpreter.

TODO: TODO_11_66_62_70: python_bootstrap: this is an experimental alternative to `bootstrap_env.bash`.

See more:
*   FS_28_84_41_40: flexible bootstrap

Typical usage:
    ./exe/bootstrap_env.py

To initialize the env with specific Python version:
    /path/to/pythonX ./exe/bootstrap_env.py

"""
from __future__ import annotations

import argparse
import atexit
import enum
import json
import logging
import os
import sys
import venv
from datetime import datetime
from pathlib import (
    Path,
    PurePath,
)

# Implements this (using the single script directly without a separate `_version.py` file):
# https://stackoverflow.com/a/7071358/441652
__version__ = "0.0.0.dev0"

from typing import (
    Any,
    Generic,
    TypeVar,
)

logger = logging.getLogger()

ValueType = TypeVar("ValueType")


def main():

    ensure_min_python_version()

    env_ctx = EnvContext()

    try:

        env_ctx.run_stages()
        atexit.register(lambda: env_ctx.report_success_status(True))
    except:
        atexit.register(lambda: env_ctx.report_success_status(False))
        raise


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
        description="Bootstraps the environment in current directory as `project_dir` `@/`."
    )
    arg_parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        dest="log_level_silent",
        # In the case of exceptions, stack traces are still printed:
        help="Do not log, use non-zero exit code on error.",
    )
    arg_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="log_level_quiet",
        help="Log errors messages only.",
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="log_level_verbose",
        default=0,
        help="Log debug messages.",
    )
    arg_parser.add_argument(
        "--proj_conf",
        type=str,
        required=True,
        help=f"path to initial config file.",
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
        "--run_mode",
        type=str,
        choices=[run_mode.name for run_mode in RunMode],
        default=RunMode.bootstrap_env.name,
        help="Select run mode.",
    )
    arg_parser.add_argument(
        "target_dst_dir_path",
        nargs="?",
        default=None,
        help="Path to one of the dirs (normally under `@/dst/`) to be used as target for `@/conf/` symlink.",
    )
    return arg_parser


def is_sub_path(
    abs_sub_path,
    abs_base_base,
):
    try:
        PurePath(abs_sub_path).relative_to(PurePath(abs_base_base))
        return True
    except ValueError:
        return False


def get_path_to_curr_python():
    return sys.executable


def get_path_to_curr_script():
    return sys.argv[0]


class RunMode(enum.Enum):
    """
    Various modes the script can be run in.
    """

    print_dag = enum.auto()

    bootstrap_env = enum.auto()


class AbstractBootstrapperVisitor:
    """
    Visitor pattern to work with bootstrappers.
    """

    def visit_bootstrapper(
        self,
        value_bootstrapper: AbstractValueBootstrapper,
    ) -> None:
        raise NotImplementedError()


class SinkPrinterVisitor(AbstractBootstrapperVisitor):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx

    def visit_bootstrapper(
        self,
        value_bootstrapper: AbstractValueBootstrapper,
    ) -> None:
        self.print_bootstrapper_parents(
            value_bootstrapper,
            level=0,
        )

    def print_bootstrapper_parents(
        self,
        value_bootstrapper,
        level: int = 0,
    ) -> None:
        print(f"{' ' * level}{value_bootstrapper.get_env_value().name}")
        for value_parent in value_bootstrapper.get_value_parents():
            self.print_bootstrapper_parents(
                self.env_ctx.value_bootstrappers[value_parent],
                level=level + 1,
            )


class BootstrapStage(enum.Enum):
    """
    States of the bootstrap process.
    """

    stage_init = enum.auto()


class PythonExecutable(enum.Enum):
    """
    Python executables which are dealt with during the bootstrap process.
    """

    py_exec_initial = enum.auto()

    py_exec_required = enum.auto()

    py_exec_venv = enum.auto()


class EnvValue(enum.Enum):
    """
    Configuration values to be bootstrapped during the bootstrap process.

    TODO: Implement chain of bootstrappers for each value.
    """

    value_default_log_level = enum.auto()

    value_script_dir_path = enum.auto()

    value_proj_dir_path = enum.auto()

    value_parsed_args = enum.auto()

    value_cli_log_level = enum.auto()

    value_proj_conf_man_file_path = enum.auto()

    value_proj_conf_man_file_data = enum.auto()

    value_proj_conf_gen_file_path = enum.auto()

    value_proj_log_level = enum.auto()

    value_proj_path_to_python = enum.auto()

    value_proj_path_to_venv = enum.auto()

    value_env_conf_dir_path = enum.auto()

    value_env_conf_man_file_path = enum.auto()

    value_env_conf_man_file_data = enum.auto()

    value_env_conf_gen_file_path = enum.auto()

    value_env_log_level = enum.auto()

    value_env_path_to_python = enum.auto()

    value_env_path_to_venv = enum.auto()


class AbstractValueBootstrapper(Generic[ValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        env_value: EnvValue,
        value_parents: list[EnvValue],
    ):
        self.env_ctx = env_ctx
        self.env_value = env_value
        self.value_parents = value_parents

        # Embed `EnvValue` name into the class name:
        assert self.env_value.name in self.__class__.__name__

    def accept_visitor(
        self,
        bootstrapper_visitor: AbstractBootstrapperVisitor,
    ) -> None:
        bootstrapper_visitor.visit_bootstrapper(self)

    def get_env_value(
        self,
    ) -> EnvValue:
        return self.env_value

    def get_value_parents(
        self,
    ) -> list[EnvValue]:
        return self.value_parents

    def bootstrap_value(
        self,
    ) -> ValueType:
        self._ensure_pre_condition()
        return self._bootstrap_value()

    def _ensure_pre_condition(
        self,
    ) -> None:
        pass

    def _bootstrap_value(
        self,
    ) -> ValueType:
        raise NotImplementedError()


class AbstractCachingValueBootstrapper(AbstractValueBootstrapper[ValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        env_value: EnvValue,
        value_parents: list[EnvValue],
    ):
        super().__init__(
            env_ctx,
            env_value,
            value_parents,
        )
        self.is_bootstrapped: bool = False
        self.cached_value: ValueType | None = None

    def _bootstrap_value(
        self,
    ) -> ValueType:
        if not self.is_bootstrapped:
            self.cached_value = self._bootstrap_once()
            self.is_bootstrapped = True

        return self.cached_value

    def _bootstrap_once(
        self,
    ) -> ValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_value_default_log_level(AbstractCachingValueBootstrapper[int]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_default_log_level,
            value_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        return logging.INFO


# noinspection PyPep8Naming
class Bootstrapper_value_script_dir_path(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_script_dir_path,
            value_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        return os.path.dirname(os.path.abspath(__file__))


# noinspection PyPep8Naming
class Bootstrapper_value_proj_dir_path(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_proj_dir_path,
            value_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        return os.getcwd()


# noinspection PyPep8Naming
class Bootstrapper_value_parsed_args(
    AbstractCachingValueBootstrapper[argparse.Namespace]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_parsed_args,
            value_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        parsed_args: argparse.Namespace = init_arg_parser().parse_args()
        return parsed_args


# noinspection PyPep8Naming
class Bootstrapper_value_proj_conf_man_file_path(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_proj_conf_man_file_path,
            value_parents=[
                EnvValue.value_proj_dir_path,
                EnvValue.value_parsed_args,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        return os.path.join(
            self.env_ctx.bootstrap_value(EnvValue.value_proj_dir_path),
            self.env_ctx.bootstrap_value(EnvValue.value_parsed_args).proj_conf,
        )


# noinspection PyPep8Naming
class Bootstrapper_value_proj_conf_man_file_data(
    AbstractCachingValueBootstrapper[dict]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_proj_conf_man_file_data,
            value_parents=[
                EnvValue.value_proj_conf_man_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        value_proj_conf_man_file_path = self.env_ctx.bootstrap_value(
            EnvValue.value_proj_conf_man_file_path
        )
        if not os.path.isfile(value_proj_conf_man_file_path):
            raise AssertionError(
                f"file [{value_proj_conf_man_file_path}] is not a file"
            )

        with open(value_proj_conf_man_file_path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)


# noinspection PyPep8Naming
class Bootstrapper_value_env_conf_dir_path(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_env_conf_dir_path,
            value_parents=[
                EnvValue.value_proj_dir_path,
                EnvValue.value_proj_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        file_data = self.env_ctx.bootstrap_value(EnvValue.value_proj_conf_man_file_data)

        value_env_conf_dir_rel_path = file_data.get(
            self.env_ctx.field_env_conf_dir_rel_path,
            # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
            #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
            #       Using default when value is missing in data does not work here.
            self.env_ctx.default_env_conf_dir_rel_path,
        )

        value_env_conf_dir_path = os.path.join(
            self.env_ctx.bootstrap_value(EnvValue.value_proj_dir_path),
            value_env_conf_dir_rel_path,
        )

        return value_env_conf_dir_path


# noinspection PyPep8Naming
class Bootstrapper_value_env_conf_man_file_path(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_env_conf_man_file_path,
            value_parents=[
                EnvValue.value_proj_dir_path,
                EnvValue.value_env_conf_dir_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        value_env_conf_man_file_path = os.path.join(
            self.env_ctx.bootstrap_value(EnvValue.value_proj_dir_path),
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            self.env_ctx.default_env_config_rel_path,
        )
        # TODO: Ensure the path is under with proper error message:
        assert is_sub_path(
            value_env_conf_man_file_path,
            self.env_ctx.bootstrap_value(EnvValue.value_env_conf_dir_path),
        )


# noinspection PyPep8Naming
class Bootstrapper_value_env_conf_man_file_data(AbstractCachingValueBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_env_conf_man_file_data,
            value_parents=[
                EnvValue.value_env_conf_man_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        value_env_conf_man_file_path = self.env_ctx.bootstrap_value(
            EnvValue.value_env_conf_man_file_path
        )
        if not os.path.isfile(value_env_conf_man_file_path):
            raise AssertionError(f"file [{value_env_conf_man_file_path}] is not a file")

        with open(value_env_conf_man_file_path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)


# noinspection PyPep8Naming
class Bootstrapper_value_env_path_to_python(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_env_path_to_python,
            value_parents=[
                EnvValue.value_env_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        file_data = self.env_ctx.bootstrap_value(EnvValue.value_env_conf_man_file_data)

        value_path_to_python = file_data.get(
            self.env_ctx.field_path_to_python,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            self.env_ctx.default_path_to_python,
        )

        if not os.path.isabs(value_path_to_python):
            value_path_to_python = os.path.join(
                self.env_ctx.bootstrap_value(EnvValue.value_proj_dir_path),
                value_path_to_python,
            )

        return value_path_to_python


# noinspection PyPep8Naming
class Bootstrapper_value_env_path_to_venv(AbstractCachingValueBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_value=EnvValue.value_env_path_to_venv,
            value_parents=[
                EnvValue.value_env_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> ValueType:
        file_data = self.env_ctx.bootstrap_value(EnvValue.value_env_conf_man_file_data)

        value_path_to_venv = file_data.get(
            self.env_ctx.field_path_to_venv,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            self.env_ctx.default_path_to_venv,
        )

        if not os.path.isabs(value_path_to_venv):
            self.abs_path_to_venv = os.path.join(
                self.env_ctx.bootstrap_value(EnvValue.value_proj_dir_path),
                value_path_to_venv,
            )

        return value_path_to_venv


class EnvContext:

    # TODO: Call it `proto_boot`?
    # TODO: Add generated one?     "boot_env.gen.proj.json"
    default_proj_config_rel_path = "boot_env.man.proj.json"
    default_env_config_rel_path = "boot_env.man.env.json"

    # TODO: Should value under project_dir or free to be anywhere?
    field_env_conf_dir_rel_path = "env_conf_dir_rel_path"
    default_env_conf_dir_rel_path = "env_conf"

    field_path_to_python = "path_to_python"
    default_path_to_python = "/usr/bin/python"

    field_path_to_venv = "path_to_venv"
    default_path_to_venv = "venv"

    def __init__(
        self,
    ):
        self.value_bootstrappers: dict[EnvValue, AbstractValueBootstrapper] = {}

        self.py_exec: PythonExecutable = PythonExecutable.py_exec_initial

        self.recursion_flag: bool = False
        self.activate_venv_only_flag: bool = False
        self.target_dst_dir_path: str | None = None

        self.custom_logger: logging.Logger = logging.getLogger()
        # TODO: generate file:
        # self.env_gen_conf_json_abs_path: str | None = None
        # TODO: Standardize naming `path_to`  or `_path`:

        self.register_bootstrapper(Bootstrapper_value_default_log_level(self))
        self.register_bootstrapper(Bootstrapper_value_script_dir_path(self))
        self.register_bootstrapper(Bootstrapper_value_proj_dir_path(self))
        self.register_bootstrapper(Bootstrapper_value_parsed_args(self))
        self.register_bootstrapper(Bootstrapper_value_proj_conf_man_file_path(self))
        self.register_bootstrapper(Bootstrapper_value_proj_conf_man_file_data(self))
        self.register_bootstrapper(Bootstrapper_value_env_conf_dir_path(self))
        self.register_bootstrapper(Bootstrapper_value_env_conf_man_file_path(self))
        self.register_bootstrapper(Bootstrapper_value_env_conf_man_file_data(self))
        self.register_bootstrapper(Bootstrapper_value_env_path_to_python(self))
        self.register_bootstrapper(Bootstrapper_value_env_path_to_venv(self))

    def register_bootstrapper(
        self,
        value_bootstrapper: AbstractValueBootstrapper,
    ):
        env_value: EnvValue = value_bootstrapper.get_env_value()
        if env_value in self.value_bootstrappers:
            raise AssertionError(
                f"[{AbstractValueBootstrapper.__name__}] for [{env_value}] is already registered."
            )
        else:
            self.value_bootstrappers[env_value] = value_bootstrapper

    def bootstrap_value(
        self,
        env_value: EnvValue,
    ) -> Any:
        value_bootstrapper = self.value_bootstrappers[env_value]
        return value_bootstrapper.bootstrap_value()

    def configure_logger(
        self,
    ) -> None:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        log_formatter = CustomFormatter()

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.NOTSET)
        stderr_handler.setFormatter(log_formatter)

        self.custom_logger.addHandler(stderr_handler)

        self.set_log_level(self.bootstrap_value(EnvValue.value_default_log_level))

    def set_log_level(
        self,
        log_level: int,
    ):
        self.log_level = log_level
        self.custom_logger.setLevel(self.log_level)

    def report_success_status(
        self,
        is_successful: bool,
    ):
        """
        Print a color-coded status message to stderr.
        """

        color_success = "\033[42m\033[30m"
        color_failure = "\033[41m\033[97m"
        color_reset = "\033[0m"

        is_reportable: bool
        if is_successful:
            color_status = color_success
            status_name = "SUCCESS"
            is_reportable = self.log_level <= logging.INFO
        else:
            color_status = color_failure
            status_name = "FAILURE"
            is_reportable = self.log_level <= logging.CRITICAL

        if is_reportable:
            print(
                f"{color_status}{status_name}{color_reset}: {get_path_to_curr_python()} {get_path_to_curr_script()}",
                file=sys.stderr,
                flush=True,
            )

    def load_cli_args(
        self,
    ):
        parsed_args: argparse.Namespace = self.bootstrap_value(
            EnvValue.value_parsed_args
        )

        self.select_log_level_from_cli_args(parsed_args)

        self.target_dst_dir_path = parsed_args.target_dst_dir_path
        self.recursion_flag = parsed_args.recursion_flag
        self.activate_venv_only_flag = parsed_args.activate_venv_only_flag

    def select_log_level_from_cli_args(
        self,
        parsed_args,
    ):
        if parsed_args.log_level_silent:
            # disable logs = no output:
            self.set_log_level(logging.CRITICAL + 1)
        elif parsed_args.log_level_quiet:
            self.set_log_level(logging.ERROR)
        elif parsed_args.log_level_verbose >= 2:
            self.set_log_level(logging.NOTSET)
        elif parsed_args.log_level_verbose == 1:
            self.set_log_level(logging.DEBUG)
        else:
            self.set_log_level(self.bootstrap_value(EnvValue.value_default_log_level))

    def load_proj_man_conf(
        self,
    ):
        # TODO: Do we need this function body?
        self.bootstrap_value(EnvValue.value_env_conf_dir_path)

    def bootstrap_env_man_conf_json_abs_path(
        self,
    ):
        # TODO: Do we need this function body?
        self.bootstrap_value(EnvValue.value_env_conf_man_file_path)

    def load_env_man_config(
        self,
    ):

        # TODO: Do we need this function body?
        file_data = self.bootstrap_value(EnvValue.value_env_conf_man_file_data)

        # ---

        # TODO: Do we need this function body?
        self.bootstrap_value(EnvValue.value_env_path_to_python)

        # ---

        # TODO: Do we need this function body?
        self.bootstrap_value(EnvValue.value_env_path_to_venv)

    def run_stages(
        self,
    ):
        # TODO: hide this procedure inside `EnvContext`:
        self.configure_logger()

        self.load_cli_args()

        run_mode: RunMode = RunMode[
            self.bootstrap_value(EnvValue.value_parsed_args).run_mode
        ]
        if run_mode is None:
            pass
        elif run_mode == RunMode.print_dag:
            self.do_print_dag()
        elif run_mode == RunMode.bootstrap_env:
            self.do_bootstrap_env()
        else:
            raise ValueError(f"cannot handle run mode [{run_mode}]")

    def do_print_dag(
        self,
    ):
        # TODO: Find "Universal Sink":
        universal_sink: AbstractBootstrapperVisitor = self.value_bootstrappers[
            EnvValue.value_proj_conf_man_file_path
        ]
        SinkPrinterVisitor(self).visit_bootstrapper(universal_sink)

    def do_bootstrap_env(
        self,
    ):
        # FS_28_84_41_40: flexible bootstrap
        # `init_venv`
        self.ensure_proj_dir()
        self.load_proj_man_conf()
        self.ensure_conf_dir()
        self.bootstrap_env_man_conf_json_abs_path()
        self.load_env_man_config()
        self.recurse_with_required_python_interpreter()

        # FS_28_84_41_40: flexible bootstrap
        # `install_deps`
        # TODO: TODO_11_66_62_70: python_bootstrap:

        # FS_28_84_41_40: flexible bootstrap
        # `generate_files`
        # TODO: TODO_11_66_62_70: python_bootstrap:

    def ensure_proj_dir(
        self,
    ):
        value_proj_dir_path = self.bootstrap_value(EnvValue.value_proj_dir_path)
        value_proj_conf_man_file_path = self.bootstrap_value(
            EnvValue.value_proj_conf_man_file_path
        )
        if not os.path.isfile(value_proj_conf_man_file_path):
            raise AssertionError(
                f"The `project_dir` `@/` [{value_proj_dir_path}] does not contain the required signature file [{value_proj_conf_man_file_path}]"
            )

    def ensure_conf_dir(
        self,
    ):
        value_env_conf_dir_path = self.bootstrap_value(EnvValue.value_env_conf_dir_path)
        if os.path.exists(value_env_conf_dir_path):
            if os.path.islink(value_env_conf_dir_path):
                if os.path.isdir(value_env_conf_dir_path):
                    if self.target_dst_dir_path is None:
                        pass
                    else:
                        conf_dir_path = os.readlink(value_env_conf_dir_path)
                        if self.target_dst_dir_path == conf_dir_path:
                            pass
                        else:
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{self.target_dst_dir_path}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{value_env_conf_dir_path}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{value_env_conf_dir_path}] is not a symlink.",
                )
        else:
            if self.target_dst_dir_path is None:
                raise AssertionError(
                    f"The `@/conf/` dir does not exists and `target_dst_dir_path` is not provided - see `--help`.",
                )
            else:
                self.ensure_allowed_conf_symlink_target()
                os.symlink(
                    self.target_dst_dir_path,
                    value_env_conf_dir_path,
                )

    def ensure_allowed_conf_symlink_target(
        self,
    ):
        """
        Raises exception if the target of the `@/conf/` symlink is not allowed.

        NOTE:
        At the moment, only targets under `project_dir` (under `@/`) are allowed.
        This is not a strict requirement and can be relaxed in the future.
        """
        if os.path.isabs(self.target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{self.target_dst_dir_path}] must not be absolute path."
            )
        elif ".." in Path(self.target_dst_dir_path).parts:
            raise AssertionError(
                f"Target for `@/conf/` symlink [{self.target_dst_dir_path}] must not contain `..` path segments."
            )
        elif not os.path.isdir(self.target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{self.target_dst_dir_path}] must lead to a directory."
            )
        return True

    def recurse_with_required_python_interpreter(
        self,
    ):
        """
        Recursively runs this script inside the `python` interpreter required by the user.

        The `python` interpreter required by the user is saved into `field_path_to_python`.
        Otherwise, it matches the interpreter the bootstrap script is executed with at the moment.
        """

        assert self.py_exec == PythonExecutable.py_exec_initial

        value_path_to_python = self.bootstrap_value(EnvValue.value_env_path_to_python)
        value_env_path_to_venv = self.bootstrap_value(EnvValue.value_env_path_to_venv)

        if is_sub_path(value_path_to_python, value_env_path_to_venv):
            value_env_conf_man_file_path = self.bootstrap_value(
                EnvValue.value_env_conf_man_file_path
            )
            raise AssertionError(
                f"The `path_to_python` [{value_path_to_python}] is a sub-path of the `path_to_venv` [{value_env_path_to_venv}]. "
                f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
                f"Specify different `path_to_python` (e.g. `/usr/bin/python3`). "
                f"Alternatively, remove [{value_env_conf_man_file_path}] and re-run `@/exe/boot_env.py` "
                f"to re-create it automatically. "
            )

        venv_path_to_python = os.path.join(
            value_env_path_to_venv,
            "bin",
            "python",
        )
        path_to_curr_python = get_path_to_curr_python()
        if is_sub_path(path_to_curr_python, value_env_path_to_venv):
            self.py_exec = PythonExecutable.py_exec_venv
            # If already under `venv`, nothing to do - just ensure `python` is from the correct `venv` path.
            if path_to_curr_python != venv_path_to_python:
                raise AssertionError(
                    f"Current `python` interpreter [{path_to_curr_python}] points under `venv` [{value_env_path_to_venv}], "
                    f"but it does not match expected interpreter there [{venv_path_to_python}]."
                )
        else:
            if path_to_curr_python != value_path_to_python:
                logger.info(
                    f"switching from current `python` interpreter [{path_to_curr_python}] to required one [{value_path_to_python}]"
                )
                os.execv(
                    value_path_to_python,
                    [
                        value_path_to_python,
                        *sys.argv,
                    ],
                )
            else:
                self.py_exec = PythonExecutable.py_exec_required
                if not os.path.exists(value_env_path_to_venv):
                    logger.info(f"creating `venv` [{value_env_path_to_venv}]")
                    venv.create(
                        value_env_path_to_venv,
                        with_pip=True,
                    )
                else:
                    logger.info(f"reusing existing `venv` [{value_env_path_to_venv}]")
                logger.info(
                    f"switching from current `python` interpreter [{value_path_to_python}] to `venv` interpreter [{venv_path_to_python}]"
                )
                os.execv(
                    venv_path_to_python,
                    [
                        venv_path_to_python,
                        *sys.argv,
                    ],
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
            fmt="%(asctime)s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s",
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


if __name__ == "__main__":
    main()
