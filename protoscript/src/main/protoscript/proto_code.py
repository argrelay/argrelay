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
import datetime
import enum
import json
import logging
import os
import pathlib
import sys
import venv

# Implements this (using the single script directly without a separate `_version.py` file):
# https://stackoverflow.com/a/7071358/441652
__version__ = "0.0.0.dev0"

from typing import (
    Any,
    Generic,
    TypeVar,
)

logger = logging.getLogger()

StateValueType = TypeVar("StateValueType")


def main(configure_env_context=None):

    ensure_min_python_version()

    if configure_env_context is None:
        env_ctx = EnvContext()
    else:
        env_ctx = configure_env_context()

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
        ArgConst.arg_recursion_flag,
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
        "--state_name",
        type=str,
        default=None,
        # TODO: Compute universal sink:
        help="Select state name to start with (default = universal sink).",
    )
    arg_parser.add_argument(
        ArgConst.arg_proj_dir_path,
        nargs="?",
        default=None,
        help="Path to project root dir (relative to current directory or absolute).",
    )
    arg_parser.add_argument(
        ArgConst.arg_py_exec,
        type=str,
        choices=[py_exec.name for py_exec in PythonExecutable],
        default=PythonExecutable.py_exec_initial.name,
        help="Used internally: category of `python` executable detected by recursive invocation.",
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
        pathlib.PurePath(abs_sub_path).relative_to(pathlib.PurePath(abs_base_base))
        return True
    except ValueError:
        return False


def get_path_to_curr_python():
    return sys.executable


def get_script_command_line():
    return " ".join(sys.argv)


def read_json_file(
    file_path: str,
) -> dict:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def write_json_file(
    file_path: str,
    file_data: dict,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        json.dump(file_data, file_obj, indent=4)


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
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        raise NotImplementedError()


class SinkPrinterVisitor(AbstractBootstrapperVisitor):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx
        self.bootstrapper_usage_count: dict[str, int] = {}

    def visit_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ) -> None:
        self.count_usage(
            state_bootstrapper,
        )
        self.print_bootstrapper_parents(
            state_bootstrapper,
            level=0,
        )

    def count_usage(
        self,
        state_bootstrapper,
    ) -> None:
        self.bootstrapper_usage_count.setdefault(
            state_bootstrapper.get_env_state().name,
            0,
        )
        self.bootstrapper_usage_count[state_bootstrapper.get_env_state().name] += 1
        for state_parent in state_bootstrapper.get_state_parents():
            self.count_usage(
                self.env_ctx.state_bootstrappers[state_parent],
            )

    def print_bootstrapper_parents(
        self,
        state_bootstrapper,
        level: int,
    ) -> None:
        print(
            f"{' ' * level}{state_bootstrapper.get_env_state().name} x {self.bootstrapper_usage_count[state_bootstrapper.get_env_state().name]}"
        )
        for state_parent in state_bootstrapper.get_state_parents():
            self.print_bootstrapper_parents(
                self.env_ctx.state_bootstrappers[state_parent],
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


class AbstractStateBootstrapper(Generic[StateValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        env_state: EnvState,
        state_parents: list[EnvState],
    ):
        self.env_ctx = env_ctx
        self.env_state = env_state

        # TODO: Actually bootstrap the additional states
        #       (beyond what is bootstrapped by code):
        # The states which will be bootstrapped:
        # `state_parents` >= `state_parents`
        self.state_parents: list[EnvState] = state_parents

        # Embed `EnvState` name into the class name:
        assert self.env_state.name in self.__class__.__name__

        for state_parent in self.state_parents:
            self.env_ctx.add_dependency_edge(
                state_parent,
                env_state,
            )

    def accept_visitor(
        self,
        bootstrapper_visitor: AbstractBootstrapperVisitor,
    ) -> None:
        bootstrapper_visitor.visit_bootstrapper(self)

    def get_env_state(
        self,
    ) -> EnvState:
        return self.env_state

    def set_state_parents(
        self,
        state_parents: list[EnvState],
    ):
        self.state_parents = state_parents

    def get_state_parents(
        self,
    ) -> list[EnvState]:
        return self.state_parents

    def bootstrap_state(
        self,
    ) -> StateValueType:
        self._ensure_pre_condition()
        return self._bootstrap_state()

    def _ensure_pre_condition(
        self,
    ) -> None:
        pass

    def _bootstrap_state(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


class AbstractCachingStateBootstrapper(AbstractStateBootstrapper[StateValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        env_state: EnvState,
        state_parents: list[EnvState],
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=env_state,
            state_parents=state_parents,
        )
        self.is_bootstrapped: bool = False
        self.cached_value: StateValueType | None = None

    def _bootstrap_state(
        self,
    ) -> StateValueType:
        if not self.is_bootstrapped:
            self.cached_value = self._bootstrap_once()
            self.is_bootstrapped = True

        return self.cached_value

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_state_default_log_level(AbstractCachingStateBootstrapper[int]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_default_log_level,
            state_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return logging.INFO


# noinspection PyPep8Naming
class Bootstrapper_state_parsed_args(
    AbstractCachingStateBootstrapper[argparse.Namespace]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_parsed_args,
            state_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        parsed_args: argparse.Namespace = init_arg_parser().parse_args()
        return parsed_args


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_specified(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_py_exec_specified,
            state_parents=[
                EnvState.state_parsed_args,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return self.env_ctx.bootstrap_state(EnvState.state_parsed_args).py_exec


# noinspection PyPep8Naming
class Bootstrapper_state_script_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_script_dir_path,
            state_parents=[],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        return os.path.dirname(os.path.abspath(__file__))


# noinspection PyPep8Naming
class Bootstrapper_state_script_config_file_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_script_config_file_path,
            state_parents=[
                EnvState.state_script_dir_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_script_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_script_dir_path
        )
        return os.path.join(
            state_script_dir_path,
            ConfConstInput.default_file_basename_conf_primer,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_proj_dir_path_specified(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_proj_dir_path_specified,
            state_parents=[
                EnvState.state_parsed_args,
                EnvState.state_script_config_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        # TODO: access by declared name (string constant):
        state_proj_dir_path_specified = self.env_ctx.bootstrap_state(
            EnvState.state_parsed_args
        ).proj_dir_path

        state_script_config_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_script_config_file_path
        )

        if not os.path.exists(state_script_config_file_path):
            if state_proj_dir_path_specified is None:
                raise AssertionError(
                    f"Unable to bootstrap [{EnvState.state_proj_dir_path_specified.name}]: file [{state_script_config_file_path}] does not exists and [{ArgConst.arg_proj_dir_path}] is not specified."
                )
        return state_proj_dir_path_specified


# noinspection PyPep8Naming
class Bootstrapper_state_script_config_file_data(
    AbstractCachingStateBootstrapper[dict]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_script_config_file_data,
            state_parents=[
                EnvState.state_script_config_file_path,
                EnvState.state_script_dir_path,
                EnvState.state_proj_dir_path_specified,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_script_config_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_script_config_file_path
        )

        file_data: dict
        if os.path.exists(state_script_config_file_path):
            file_data = read_json_file(state_script_config_file_path)
        else:
            state_script_dir_path = self.env_ctx.bootstrap_state(
                EnvState.state_script_dir_path
            )
            state_proj_dir_path_specified = self.env_ctx.bootstrap_state(
                EnvState.state_proj_dir_path_specified
            )
            assert state_proj_dir_path_specified is not None

            # Generate file data when missing (first time):
            file_data = {
                ConfConstPrimer.field_dir_rel_path_root_proj: os.path.relpath(
                    state_proj_dir_path_specified,
                    state_script_dir_path,
                ),
                ConfConstPrimer.field_file_rel_path_conf_proj: ConfConstPrimer.default_file_basename_conf_proj,
            }
            write_json_file(state_script_config_file_path, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_proj_dir_path_configured(
    AbstractCachingStateBootstrapper[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_proj_dir_path_configured,
            state_parents=[
                EnvState.state_script_config_file_data,
                EnvState.state_script_dir_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_script_config_file_data = self.env_ctx.bootstrap_state(
            EnvState.state_script_config_file_data
        )

        field_proj_dir_rel_path = state_script_config_file_data[
            ConfConstPrimer.field_dir_rel_path_root_proj
        ]

        state_script_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_script_dir_path
        )

        state_proj_dir_path_configured = os.path.join(
            state_script_dir_path,
            field_proj_dir_rel_path,
        )

        return os.path.normpath(state_proj_dir_path_configured)


# noinspection PyPep8Naming
class Bootstrapper_state_target_dst_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_target_dst_dir_path,
            state_parents=[
                EnvState.state_parsed_args,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        # TODO: access via declared string constant for arg field:
        return self.env_ctx.bootstrap_state(
            EnvState.state_parsed_args
        ).target_dst_dir_path


# noinspection PyPep8Naming
class Bootstrapper_state_proj_conf_man_file_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_proj_conf_man_file_path,
            state_parents=[
                EnvState.state_proj_dir_path_configured,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_proj_dir_path_configured = self.env_ctx.bootstrap_state(
            EnvState.state_proj_dir_path_configured
        )

        state_script_config_file_data = self.env_ctx.bootstrap_state(
            EnvState.state_script_config_file_data
        )

        field_proj_config_rel_path = state_script_config_file_data[
            ConfConstPrimer.field_file_rel_path_conf_proj
        ]

        return os.path.join(
            state_proj_dir_path_configured,
            field_proj_config_rel_path,
        )


# noinspection PyPep8Naming
class Bootstrapper_state_proj_conf_man_file_data(
    AbstractCachingStateBootstrapper[dict]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_proj_conf_man_file_data,
            state_parents=[
                EnvState.state_proj_conf_man_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:

        state_proj_conf_man_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_proj_conf_man_file_path
        )
        if os.path.exists(state_proj_conf_man_file_path):
            return read_json_file(state_proj_conf_man_file_path)
        else:
            # Generate file data when missing (first time):
            file_data = {
                # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
                #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
                #       Using default when value is missing in data does not work here.
                ConfConstProj.field_dir_rel_path_conf_env_link_name: ConfConstProj.default_dir_rel_path_conf_env_link_name,
            }
            write_json_file(state_proj_conf_man_file_path, file_data)
            return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_dir_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_conf_dir_path,
            state_parents=[
                EnvState.state_proj_dir_path_configured,
                EnvState.state_proj_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.env_ctx.bootstrap_state(EnvState.state_proj_conf_man_file_data)

        env_conf_dir_rel_path = file_data.get(
            ConfConstProj.field_dir_rel_path_conf_env_link_name,
            # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
            #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
            #       Using default when value is missing in data does not work here.
            ConfConstProj.default_dir_rel_path_conf_env_link_name,
        )

        assert not os.path.isabs(env_conf_dir_rel_path)

        # Convert to absolute:
        state_env_conf_dir_path = os.path.join(
            self.env_ctx.bootstrap_state(EnvState.state_proj_dir_path_configured),
            env_conf_dir_rel_path,
        )

        return state_env_conf_dir_path


# noinspection PyPep8Naming
class Bootstrapper_state_target_dst_dir_path_verified(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_target_dst_dir_path_verified,
            state_parents=[
                EnvState.state_target_dst_dir_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        """
        Raises exception if the target path of the `@/conf/` symlink is not allowed.

        NOTE:
        At the moment, only target paths under `project_dir` (under `@/`) are allowed.
        This is not a strict requirement and can be relaxed in the future.
        """

        state_target_dst_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_target_dst_dir_path
        )
        if os.path.isabs(state_target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must not be absolute path."
            )
        elif ".." in pathlib.Path(state_target_dst_dir_path).parts:
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must not contain `..` path segments."
            )
        elif not os.path.isdir(state_target_dst_dir_path):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_target_dst_dir_path}] must lead to a directory."
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_dir_path_verified(
    AbstractCachingStateBootstrapper[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_conf_dir_path_verified,
            state_parents=[
                EnvState.state_target_dst_dir_path,
                EnvState.state_target_dst_dir_path_verified,
                EnvState.state_env_conf_dir_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_dir_path
        )
        state_target_dst_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_target_dst_dir_path
        )
        if os.path.exists(state_env_conf_dir_path):
            if os.path.islink(state_env_conf_dir_path):
                if os.path.isdir(state_env_conf_dir_path):
                    if state_target_dst_dir_path is None:
                        pass
                    else:
                        conf_dir_path = os.readlink(state_env_conf_dir_path)
                        if state_target_dst_dir_path == conf_dir_path:
                            pass
                        else:
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{state_target_dst_dir_path}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{state_env_conf_dir_path}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{state_env_conf_dir_path}] is not a symlink.",
                )
        else:
            if state_target_dst_dir_path is None:
                raise AssertionError(
                    f"The `@/conf/` dir does not exists and `target_dst_dir_path` is not provided - see `--help`.",
                )
            else:
                state_target_dst_dir_path_verified = self.env_ctx.bootstrap_state(
                    EnvState.state_target_dst_dir_path_verified
                )
                assert state_target_dst_dir_path_verified

                os.symlink(
                    state_target_dst_dir_path,
                    state_env_conf_dir_path,
                )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_man_file_path(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_conf_man_file_path,
            state_parents=[
                EnvState.state_proj_dir_path_configured,
                EnvState.state_env_conf_dir_path,
                EnvState.state_env_conf_dir_path_verified,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_dir_path_verified = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_dir_path_verified
        )
        assert state_env_conf_dir_path_verified

        state_proj_dir_path_configured = self.env_ctx.bootstrap_state(
            EnvState.state_proj_dir_path_configured
        )
        state_env_conf_man_file_path = os.path.join(
            state_proj_dir_path_configured,
            ConfConstProj.default_dir_rel_path_conf_env_link_name,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstProj.default_file_basename_conf_env,
        )
        state_env_conf_dir_path = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_dir_path
        )
        # TODO: Ensure the path is under with proper error message:
        assert is_sub_path(
            state_env_conf_man_file_path,
            state_env_conf_dir_path,
        )
        return state_env_conf_man_file_path


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_man_file_data(AbstractCachingStateBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_conf_man_file_data,
            state_parents=[
                EnvState.state_env_conf_man_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_man_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_man_file_path
        )
        # TODO: If does not exists, do not fail.
        if not os.path.isfile(state_env_conf_man_file_path):
            raise AssertionError(f"file [{state_env_conf_man_file_path}] is not a file")

        return read_json_file(state_env_conf_man_file_path)


# noinspection PyPep8Naming
class Bootstrapper_state_env_path_to_python(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_path_to_python,
            state_parents=[
                EnvState.state_env_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.env_ctx.bootstrap_state(EnvState.state_env_conf_man_file_data)

        state_env_path_to_python = file_data.get(
            ConfConstEnv.field_file_abs_path_python,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,
        )

        if not os.path.isabs(state_env_path_to_python):
            state_env_path_to_python = os.path.join(
                self.env_ctx.bootstrap_state(EnvState.state_proj_dir_path_configured),
                state_env_path_to_python,
            )

        return state_env_path_to_python


# noinspection PyPep8Naming
class Bootstrapper_state_env_path_to_venv(AbstractCachingStateBootstrapper[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_path_to_venv,
            state_parents=[
                EnvState.state_env_conf_man_file_data,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        file_data = self.env_ctx.bootstrap_state(EnvState.state_env_conf_man_file_data)

        state_env_path_to_venv = file_data.get(
            ConfConstEnv.field_dir_rel_path_venv,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_env_path_to_venv):
            state_env_path_to_venv = os.path.join(
                self.env_ctx.bootstrap_state(EnvState.state_proj_dir_path_configured),
                state_env_path_to_venv,
            )

        return state_env_path_to_venv


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_gen_file_data(AbstractCachingStateBootstrapper[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_env_conf_gen_file_data,
            state_parents=[
                EnvState.state_env_conf_man_file_path,
                EnvState.state_env_path_to_python,
                EnvState.state_env_path_to_venv,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        state_env_conf_man_file_path = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_man_file_path
        )
        state_env_path_to_python = self.env_ctx.bootstrap_state(
            EnvState.state_env_path_to_python
        )
        state_env_path_to_venv = self.env_ctx.bootstrap_state(
            EnvState.state_env_path_to_venv
        )
        file_data: dict
        if os.path.exists(state_env_conf_man_file_path):
            file_data = read_json_file(state_env_conf_man_file_path)
        else:
            file_data = {
                ConfConstEnv.field_file_abs_path_python: state_env_path_to_python,
                ConfConstEnv.field_dir_rel_path_venv: state_env_path_to_venv,
            }
            # TODO: This creates a directory with `ConfConstProj.default_dir_rel_path_conf_env_link_name` instead of symlink:
            write_json_file(state_env_conf_man_file_path, file_data)
        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_selected(
    AbstractCachingStateBootstrapper[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            env_state=EnvState.state_py_exec_selected,
            state_parents=[
                EnvState.state_py_exec_specified,
                EnvState.state_env_conf_gen_file_data,
                EnvState.state_env_conf_man_file_path,
            ],
        )

    def _bootstrap_once(
        self,
    ) -> StateValueType:
        """
        Recursively runs this script inside the `python` interpreter required by the user.

        The `python` interpreter required by the user is saved into `field_file_abs_path_python`.
        Otherwise, it matches the interpreter the bootstrap script is executed with at the moment.
        """

        state_py_exec_specified: PythonExecutable = self.env_ctx.bootstrap_state(
            EnvState.state_py_exec_specified
        )

        value_file_abs_path_python = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_gen_file_data
        )[ConfConstEnv.field_file_abs_path_python]
        value_dir_rel_path_venv = self.env_ctx.bootstrap_state(
            EnvState.state_env_conf_gen_file_data
        )[ConfConstEnv.field_dir_rel_path_venv]

        if is_sub_path(value_file_abs_path_python, value_dir_rel_path_venv):
            state_env_conf_man_file_path = self.env_ctx.bootstrap_state(
                EnvState.state_env_conf_man_file_path
            )
            raise AssertionError(
                f"The `path_to_python` [{value_file_abs_path_python}] is a sub-path of the `path_to_venv` [{value_dir_rel_path_venv}]. "
                f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
                f"Specify different `path_to_python` (e.g. `/usr/bin/python3`). "
                f"Alternatively, remove [{state_env_conf_man_file_path}] and re-run `@/exe/proto_code.py` "
                f"to re-create it automatically. "
            )

        venv_path_to_python = os.path.join(
            value_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        if is_sub_path(path_to_curr_python, value_dir_rel_path_venv):
            assert state_py_exec_specified == PythonExecutable.py_exec_venv
            # If already under `venv`, nothing to do - just ensure `python` is from the correct `venv` path.
            if path_to_curr_python != venv_path_to_python:
                raise AssertionError(
                    f"Current `python` interpreter [{path_to_curr_python}] points under `venv` [{value_dir_rel_path_venv}], "
                    f"but it does not match expected interpreter there [{venv_path_to_python}]."
                )
            else:
                # Successfully reached end goal:
                self.env_ctx.py_exec = state_py_exec_specified
        else:
            if path_to_curr_python != value_file_abs_path_python:
                assert state_py_exec_specified == PythonExecutable.py_exec_initial
                logger.info(
                    f"switching from current `python` interpreter [{path_to_curr_python}] to required one [{value_file_abs_path_python}]"
                )
                os.execv(
                    value_file_abs_path_python,
                    [
                        value_file_abs_path_python,
                        *sys.argv,
                        ArgConst.arg_py_exec,
                        PythonExecutable.py_exec_required.name,
                    ],
                )
            else:
                assert state_py_exec_specified == PythonExecutable.py_exec_required
                if not os.path.exists(value_dir_rel_path_venv):
                    logger.info(f"creating `venv` [{value_dir_rel_path_venv}]")
                    venv.create(
                        value_dir_rel_path_venv,
                        with_pip=True,
                    )
                else:
                    logger.info(f"reusing existing `venv` [{value_dir_rel_path_venv}]")
                logger.info(
                    f"switching from current `python` interpreter [{value_file_abs_path_python}] to `venv` interpreter [{venv_path_to_python}]"
                )
                os.execv(
                    venv_path_to_python,
                    [
                        venv_path_to_python,
                        *sys.argv,
                        ArgConst.arg_py_exec,
                        PythonExecutable.py_exec_venv.name,
                    ],
                )

        return self.env_ctx.py_exec


class EnvState(enum.Enum):
    """
    Configuration states to be bootstrapped during the bootstrap process.

    NOTE: Only names of the enum items are supposed to be used (any value is ignored).
    """

    state_default_log_level = Bootstrapper_state_default_log_level

    state_parsed_args = Bootstrapper_state_parsed_args

    state_py_exec_specified = Bootstrapper_state_py_exec_specified

    state_script_dir_path = Bootstrapper_state_script_dir_path

    state_script_config_file_path = Bootstrapper_state_script_config_file_path

    state_proj_dir_path_specified = Bootstrapper_state_proj_dir_path_specified

    state_script_config_file_data = Bootstrapper_state_script_config_file_data

    state_proj_dir_path_configured = Bootstrapper_state_proj_dir_path_configured

    # TODO:
    # state_cli_log_level = enum.auto()

    state_proj_conf_man_file_path = Bootstrapper_state_proj_conf_man_file_path

    state_proj_conf_man_file_data = Bootstrapper_state_proj_conf_man_file_data

    # TODO:
    # state_proj_conf_gen_file_path = enum.auto()

    # TODO:
    # state_proj_log_level = enum.auto()

    # TODO:
    # state_proj_path_to_python = enum.auto()

    # TODO:
    # state_proj_path_to_venv = enum.auto()

    state_env_conf_dir_path = Bootstrapper_state_env_conf_dir_path

    state_target_dst_dir_path = Bootstrapper_state_target_dst_dir_path

    state_target_dst_dir_path_verified = Bootstrapper_state_target_dst_dir_path_verified

    state_env_conf_dir_path_verified = Bootstrapper_state_env_conf_dir_path_verified

    state_env_conf_man_file_path = Bootstrapper_state_env_conf_man_file_path

    state_env_conf_man_file_data = Bootstrapper_state_env_conf_man_file_data

    # TODO:
    # state_env_conf_gen_file_path = enum.auto()

    # TODO:
    # state_env_log_level = enum.auto()

    state_env_path_to_python = Bootstrapper_state_env_path_to_python

    state_env_path_to_venv = Bootstrapper_state_env_path_to_venv

    state_env_conf_gen_file_data = Bootstrapper_state_env_conf_gen_file_data

    state_py_exec_selected = Bootstrapper_state_py_exec_selected

    # TODO: Use string for id, and do not define it here:
    state_custom = None


class ArgConst:

    # TODO: decide on convention for pure `arg_name` and `--arg_name`:
    name_recursion_flag = "recursion_flag"
    name_proj_dir_path = "proj_dir_path"
    name_py_exec = "py_exec"

    arg_recursion_flag = f"--{name_recursion_flag}"
    arg_proj_dir_path = f"--{name_proj_dir_path}"
    arg_py_exec = f"--{name_py_exec}"


class ConfConstGeneral:

    # This is a value declared for completeness,
    # but unused (evaluated dynamically via the bootstrap process):
    input_based = None

    file_rel_path_venv_python = os.path.join(
        "bin",
        "python",
    )


class ConfConstInput:
    """
    Constants input config phase.
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

    default_file_basename_conf_primer = "conf_primer.proto_code.json"


class ConfConstPrimer:
    """
    Constants primer config phase.
    """

    field_dir_rel_path_root_proj = "dir_rel_path_root_proj"

    field_file_rel_path_conf_proj = "file_rel_path_conf_proj"

    default_dir_rel_path_root_proj = ConfConstGeneral.input_based

    default_file_basename_conf_proj = "conf_proj.proto_code.json"


class ConfConstProj:
    """
    Constants proj config phase.
    """

    field_dir_rel_path_conf_env_link_name = "dir_rel_path_conf_env_link_name"

    default_dir_rel_path_conf_env_link_name = os.path.join(
        "conf_env",
    )

    default_file_basename_conf_env = "conf_env.proto_code.json"


class ConfConstEnv:
    """
    Constants env config phase.
    """

    field_file_abs_path_python = "file_abs_path_python"
    field_dir_rel_path_venv = "path_to_venv"

    default_file_abs_path_python = "/usr/bin/python"
    default_dir_rel_path_venv = "venv"


class EnvContext:

    def __init__(
        self,
    ):
        self.state_bootstrappers: dict[EnvState, AbstractStateBootstrapper] = {}
        self.dependency_edges: list[tuple[EnvState, EnvState]] = []

        self.py_exec: PythonExecutable = PythonExecutable.py_exec_initial

        self.recursion_flag: bool = False
        self.activate_venv_only_flag: bool = False

        self.custom_logger: logging.Logger = logging.getLogger()
        # TODO: generate file:
        # self.env_gen_conf_json_abs_path: str | None = None
        # TODO: Standardize naming `path_to`  or `_path`:

        self.register_bootstrapper(Bootstrapper_state_default_log_level(self))
        self.register_bootstrapper(Bootstrapper_state_parsed_args(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_specified(self))
        self.register_bootstrapper(Bootstrapper_state_script_dir_path(self))
        self.register_bootstrapper(Bootstrapper_state_script_config_file_path(self))
        self.register_bootstrapper(Bootstrapper_state_proj_dir_path_specified(self))
        self.register_bootstrapper(Bootstrapper_state_script_config_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_proj_dir_path_configured(self))
        self.register_bootstrapper(Bootstrapper_state_target_dst_dir_path(self))
        self.register_bootstrapper(Bootstrapper_state_proj_conf_man_file_path(self))
        self.register_bootstrapper(Bootstrapper_state_proj_conf_man_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_path(self))
        self.register_bootstrapper(
            Bootstrapper_state_target_dst_dir_path_verified(self)
        )
        self.register_bootstrapper(Bootstrapper_state_env_conf_dir_path_verified(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_man_file_path(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_man_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_env_path_to_python(self))
        self.register_bootstrapper(Bootstrapper_state_env_path_to_venv(self))
        self.register_bootstrapper(Bootstrapper_state_env_conf_gen_file_data(self))
        self.register_bootstrapper(Bootstrapper_state_py_exec_selected(self))

        self.populate_dependencies()

        # TODO: Find "Universal Sink":
        self.universal_sink: EnvState = EnvState.state_py_exec_selected

    def register_bootstrapper(
        self,
        state_bootstrapper: AbstractStateBootstrapper,
    ):
        env_state: EnvState = state_bootstrapper.get_env_state()
        if env_state in self.state_bootstrappers:
            raise AssertionError(
                f"[{AbstractStateBootstrapper.__name__}] for [{env_state}] is already registered."
            )
        else:
            self.state_bootstrappers[env_state] = state_bootstrapper

    def add_dependency_edge(
        self,
        parent_state: EnvState,
        child_state: EnvState,
    ):
        self.dependency_edges.append((parent_state, child_state))

    def populate_dependencies(
        self,
    ):
        # Populate a temporary collection of all children per parent:
        child_parents: dict[EnvState, list[EnvState]] = {}
        for dependency_edge in self.dependency_edges:
            parent_dependency = dependency_edge[0]
            child_dependency = dependency_edge[1]
            child_parents.setdefault(child_dependency, []).append(parent_dependency)

        # Set children per parent:
        for child_id in child_parents.keys():
            state_bootstrapper: AbstractStateBootstrapper = self.state_bootstrappers[
                child_id
            ]
            state_parents = child_parents[child_id]
            state_bootstrapper.set_state_parents(state_parents)

    def bootstrap_state(
        self,
        env_state: EnvState,
    ) -> Any:
        state_bootstrapper = self.state_bootstrappers[env_state]
        return state_bootstrapper.bootstrap_state()

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

        self.set_log_level(self.bootstrap_state(EnvState.state_default_log_level))

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
                f"{color_status}{status_name}{color_reset}: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )

    def load_cli_args(
        self,
    ):
        parsed_args: argparse.Namespace = self.bootstrap_state(
            EnvState.state_parsed_args
        )

        self.select_log_level_from_cli_args(parsed_args)

        # TODO: Define states for these values instead:
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
            self.set_log_level(self.bootstrap_state(EnvState.state_default_log_level))

    def run_stages(
        self,
    ):
        # TODO: hide this procedure inside `EnvContext`:
        self.configure_logger()

        self.load_cli_args()

        run_mode: RunMode = RunMode[
            self.bootstrap_state(EnvState.state_parsed_args).run_mode
        ]
        state_name: str = self.bootstrap_state(EnvState.state_parsed_args).state_name

        if state_name is None:
            env_state = self.universal_sink
        else:
            env_state: EnvState = EnvState[state_name]

        if run_mode is None:
            pass
        elif run_mode == RunMode.print_dag:
            self.do_print_dag(env_state)
        elif run_mode == RunMode.bootstrap_env:
            self.do_bootstrap_env(env_state)
        else:
            raise ValueError(f"cannot handle run mode [{run_mode}]")

    def do_print_dag(
        self,
        env_state: EnvState,
    ):
        state_bootstrapper: AbstractBootstrapperVisitor = self.state_bootstrappers[
            env_state
        ]
        SinkPrinterVisitor(self).visit_bootstrapper(state_bootstrapper)

    def do_bootstrap_env(
        self,
        # TODO: use this:
        env_state: EnvState,
    ):
        # FS_28_84_41_40: flexible bootstrap
        # `init_venv`
        self.bootstrap_state(env_state)

        # FS_28_84_41_40: flexible bootstrap
        # `install_deps`
        # TODO: TODO_11_66_62_70: python_bootstrap:

        # FS_28_84_41_40: flexible bootstrap
        # `generate_files`
        # TODO: TODO_11_66_62_70: python_bootstrap:


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
        formatted_timestamp = datetime.datetime.fromtimestamp(
            log_record.created
        ).strftime("%Y-%m-%d %H:%M:%S")

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
