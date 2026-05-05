#!/usr/bin/env python3
################################################################################
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
################################################################################
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned
# (to be available in the target client repo on clone),
# but it should not be linted
# (as its content/style is governed by the source repo).
################################################################################
#
# A bootstrap script that starts with a **wild** `python` version
# to invoke code from a configured `venv` using the **required** `python` version.
# FT_84_11_73_28.supported_python_versions.md: tested for `python` 3.7 min and above.
# Documentation: https://protoprimer.readthedocs.io/
# Source: https://github.com/uvsmtid/protoprimer
# SPDX-License-Identifier: MIT
# Copyright (C) 2025 Alexey Pakseykin
#
# TODO: TODO_91_75_37_57.implement_shebang_update.md / FT_02_89_37_65.shebang_line.md
#       Be able to generate any shebang for `proto_code`.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

from __future__ import annotations

import argparse
import ast
import atexit
import contextvars
import datetime
import enum
import importlib
import importlib.util
import json
import logging
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import types
import typing
from typing import (
    Any,
    Callable,
    Generic,
    MutableMapping,
    TypeVar,
)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
# The release process ensures that content in this file matches the version below while tagging the release commit
# (otherwise, if the file comes from a different commit, the version is irrelevant):
__version__ = "0.11.1"

logger: logging.Logger = logging.getLogger()

log_stride = contextvars.ContextVar("state_stride")

ValueType = TypeVar("ValueType")
DataValueType = TypeVar("DataValueType")


def proto_main(configure_env_context: typing.Callable[[], EnvContext] | None = None):
    # Avoid `NameError` (not associated with a value in enclosing scope) for the last `except`:
    env_ctx = EnvContext()
    try:
        ensure_min_python_version()

        if configure_env_context is not None:
            # See UC_10_80_27_57.extend_DAG.md:
            env_ctx = configure_env_context()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
        #       Do not call `state_graph.eval_state` directly.
        #       Evaluate state via child state (to check that this is eligible).
        #       But... What is the child state here?
        state_exec_mode_executed: bool = env_ctx.state_graph.eval_state(TargetState.target_exec_mode_executed.value.name)
        assert state_exec_mode_executed
        atexit.register(lambda: env_ctx.print_exit_line(0))

    except subprocess.CalledProcessError as subproc_error:
        # Convert the list of arguments into a single shell-escaped string:
        if isinstance(subproc_error.cmd, list):
            executable_str = " ".join(shlex.quote(arg) for arg in subproc_error.cmd)
        else:
            executable_str = subproc_error.cmd
        exit_code = subproc_error.returncode
        # NOTE: orig `exit_code` is only part of the message, but `RuntimError` will exit with 1:
        atexit.register(lambda: env_ctx.print_exit_line(1))
        raise RuntimeError(f"command failed with `exit_code` [{exit_code}]:\n{executable_str}") from subproc_error

    except SystemExit as sys_exit:
        if sys_exit.code is None or sys_exit.code == 0:
            atexit.register(lambda: env_ctx.print_exit_line(0))
        else:
            exit_code: int = sys_exit.code if isinstance(sys_exit.code, int) else 1
            atexit.register(lambda: env_ctx.print_exit_line(exit_code))
        # We only catch `SystemExit` to print the status line.
        # The actual exit code is already in-flight with `SystemExit`, propagate it:
        raise
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    except:
        atexit.register(lambda: env_ctx.print_exit_line(1))
        raise


def ensure_min_python_version():
    """
    Ensure the running Python interpreter is >= (major, minor, patch).
    """

    # FT_84_11_73_28.supported_python_versions.md:
    version_tuple: tuple[int, int, int] = (3, 7, 0)

    if sys.version_info < version_tuple:
        raise AssertionError(f"The version of Python used [{sys.version_info}] is below the min required [{version_tuple}]")


class StateStride(enum.IntEnum):
    """
    Monotonically increasing "stride"-s (a milestone within the DAG of `EnvState`-s).
    Several `EnvState`-s are normally required to transition between each `StateStride`-s.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    If the current `python` executable has to be (re-)started during the bootstrap process,
    the `StateStride` enum item name is communicated via `EnvVar.var_PROTOPRIMER_PY_EXEC`.

    See FT_72_45_12_06.python_executable.md
    """

    # No value for `EnvVar.var_PROTOPRIMER_PY_EXEC` -> `python` executable has not been categorized yet:
    stride_py_unknown = -1

    # To run `proto_code` by `python` outside any `venv` (to identify `proto_code` abs path):
    stride_py_arbitrary = 1

    # To run `python` of specific version (to create `venv` using that `python`):
    stride_py_required = 2

    # To use dedicated `venv` (to install packages):
    stride_py_venv = 3

    # To use the latest `protoprimer` package:
    stride_deps_updated = 4
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # To use the latest `proto_code` sources:
    stride_src_updated = 5

    def __str__(self):
        return f"{self.name}[{self.value}]"


class TermColor(enum.Enum):
    """
    ANSI escape codes for terminal text colors:

    Reference:
    *   https://pkg.go.dev/github.com/whitedevops/colors
    *   https://gist.github.com/vratiu/9780109
    """

    # Direct colors:
    # do not use them directly, use semantic colors instead (below).

    back_dark_red = "\033[41m"
    back_dark_green = "\033[42m"
    back_dark_yellow = "\033[43m"
    back_dark_blue = "\033[44m"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    fore_dark_black = "\033[30m"
    fore_dark_red = "\033[31m"
    fore_dark_green = "\033[32m"
    fore_dark_yellow = "\033[33m"
    fore_dark_cyan = "\033[36m"

    fore_bright_green = "\033[92m"
    fore_bright_yellow = "\033[93m"
    fore_bright_blue = "\033[94m"
    fore_bright_white = "\033[97m"

    fore_bold_dark_red = "\033[1;31m"

    # Semantic colors:

    config_comment = f"{fore_bright_green}"
    config_missing = f"{fore_bright_blue}"
    config_unused = f"{fore_bright_yellow}"

    reset_style = "\033[0m"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class KeyWord(enum.Enum):
    """
    Reused words for semantic linking via these definitions.
    """

    key_input = "input"
    key_primer = "primer"
    key_client = "client"
    key_global = "global"
    key_env = "env"
    key_local = "local"
    key_derived = "derived"

    key_help = "help"

    key_var = "var"
    key_tmp = "tmp"
    key_log = "log"
    key_venv = "venv"
    key_cache = "cache"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    key_do = "do"
    key_run = "run"
    key_start = "start"
    key_install = "install"
    key_restart = "restart"

    key_id = "id"
    key_state = "state"
    key_args = "args"
    key_mode = "mode"
    key_stderr = "stderr"
    key_handler = "handler"
    key_data = "data"
    key_package = "package"
    key_constraints = "constraints"
    key_main = "main"
    key_func = "func"
    key_level = "level"
    key_basename = "basename"

    key_mocked = "mocked"
    key_default = "default"
    key_conf = "conf"
    key_effective = "effective"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    key_configured = "configured"
    key_parsed = "parsed"
    key_executed = "executed"
    key_reached = "reached"
    key_printed = "printed"
    key_triggered = "triggered"
    key_installed = "installed"
    key_updated = "updated"
    key_generated = "generated"
    key_prepared = "prepared"


class TopDir(enum.Enum):
    """
    Top-level directories (or dirs under `TopDir.dir_var`).
    """

    dir_var = f"{KeyWord.key_var.value}"
    dir_tmp = f"{KeyWord.key_tmp.value}"
    dir_log = f"{KeyWord.key_log.value}"
    dir_venv = f"{KeyWord.key_venv.value}"
    dir_cache = f"{KeyWord.key_cache.value}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class ConfLeap(enum.Enum):
    """
    See FT_89_41_35_82.conf_leap.md
    """

    # surrogate: no associated config file:
    leap_input = f"{KeyWord.key_input.value}"

    leap_primer = f"{KeyWord.key_primer.value}"

    # TODO: Rename, use `global` instead:
    #       FT_23_37_64_44.global_vs_local.md
    #       FT_89_41_35_82.conf_leap.md
    leap_client = f"{KeyWord.key_client.value}"

    # TODO: Remove, use `local` instead:
    #       FT_23_37_64_44.global_vs_local.md
    #       FT_89_41_35_82.conf_leap.md
    leap_env = f"{KeyWord.key_env.value}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # surrogate: no associated config file:
    leap_derived = f"{KeyWord.key_derived.value}"

    # TODO: Consolidate `leap_global` and `leap_local` are not really `ConfLeap`-s.
    #       Instead, see `leap_client` and `leap_env`.
    leap_global = f"{KeyWord.key_global.value}"
    leap_local = f"{KeyWord.key_local.value}"


class PrimerRuntime(enum.Enum):
    """
    See FT_14_52_73_23.primer_runtime.md
    """

    runtime_proto = "proto"

    runtime_neo = "neo"


class EntryFunc(enum.Enum):
    """
    Specifies how `proto_kernel` was started (which API was the entry point).
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    See FT_25_62_13_55.entry_func.md

    TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
          make use of this enum.
    """

    # Start via `boot_env` call:
    func_boot_env = "boot_env"

    # Start via `start_app` call:
    func_start_app = "start_app"

    # A lib function call (e.g. `get_derived_config`):
    func_lib = "lib"

    # Direct CLI execution via (e.g.) `./proto_kernel.py` executing `__main__` section:
    func_main = "main"


class ExecMode(enum.Enum):
    """
    Various modes the script can be run in.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    See FT_11_27_29_83.exec_mode.md
    """

    # FT_85_17_35_21.boot_env.md
    mode_boot = "boot"

    # FT_05_08_64_67.start_app.md
    mode_start = "start"

    # FT_42_03_79_73.reboot_env.md
    # UC_61_12_90_59.upgrade_venv.md
    mode_reboot = "reboot"

    # FT_00_22_19_59.derived_config.md
    mode_eval = "eval"

    # TODO: TODO_73_71_31_84.exec_mode_check_or_info.md: maybe merge `info` and `check` use cases?
    #       If we specify which `StateStride` or which `EnvState` to check things for, it might be useful.
    # TODO: implement? It must find its application to check things before `venv`.
    mode_check = "check"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class GraphCoordinates:
    """
    This class defines fields which specify coordinates for `NodeFactory`-ies during DAG constructions.

    Each class of `StateNode` defines applicable coordinates for its creation via its `NodeFactory`.

    See TODO_60_63_68_81.refactor_DAG_builder.md
    """

    def __init__(self):
        self.entry_func: EntryFunc | None = None
        self.exec_mode: ExecMode | None = None


# TODO: TODO_31_76_38_60.exec_mode_for_shell.md: remove "command" (when replaced by `shell_mode` or `run_mode`):
class CommandAction(enum.Enum):

    action_command = "command"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
class FilesystemObject(enum.Enum):

    fs_object_file = "file"

    fs_object_dir = "dir"

    fs_object_symlink = "symlink"


class PathType(enum.Enum):

    # If both paths are possible (absolute or relative):
    path_any = "any_path"

    # Relative path:
    path_rel = "rel_path"

    # Absolute path:
    path_abs = "abs_path"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
class EnvVar(enum.Enum):
    """
    See FT_08_92_69_92.env_var.md
    """

    # FT_11_27_29_83.exec_mode.md
    var_PROTOPRIMER_EXEC_MODE = "PROTOPRIMER_EXEC_MODE"

    # FT_58_74_37_70.boot_vs_start.md
    # Selects the main function to run, for example, "sup_module.sub_module:some_main".
    var_PROTOPRIMER_MAIN_FUNC = "PROTOPRIMER_MAIN_FUNC"

    var_PROTOPRIMER_STDERR_LOG_LEVEL = "PROTOPRIMER_STDERR_LOG_LEVEL"

    var_PROTOPRIMER_PY_EXEC = "PROTOPRIMER_PY_EXEC"

    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       This is to be removed - it is only used by
    #       `conf_eval` and `venv_shell` which can be switched to `start_app`
    #       as soon as config can be accessed via API.
    var_PROTOPRIMER_DO_INSTALL = "PROTOPRIMER_DO_INSTALL"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    var_PROTOPRIMER_PROTO_CODE = "PROTOPRIMER_PROTO_CODE"

    var_PROTOPRIMER_CONF_BASENAME = "PROTOPRIMER_CONF_BASENAME"

    var_PROTOPRIMER_START_ID = "PROTOPRIMER_START_ID"

    var_PROTOPRIMER_VENV_DRIVER = "PROTOPRIMER_VENV_DRIVER"

    # TODO: Consider splitting `is_test_run()` and `PROTOPRIMER_MOCKED_RESTART` into different `feature_story`-ies.
    var_PROTOPRIMER_MOCKED_RESTART = "PROTOPRIMER_MOCKED_RESTART"
    """
    See: FT_83_60_72_19.test_perimeter.md / test_fast_fat_min_mocked
    """


class ConfDst(enum.Enum):
    """
    See FT_23_37_64_44.global_vs_local.md

    TODO: Is this supposed to be called conf src (instead of `conf dst`)?
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    dst_shebang = "shebang"

    dst_global = "gconf"

    dst_local = "lconf"


class ValueName(enum.Enum):

    value_stderr_log_level = "stderr_log_level"

    value_do_install = "do_install"

    value_exec_mode = "exec_mode"

    value_final_state = "final_state"

    value_py_exec = "py_exec"

    value_primer_runtime = "primer_runtime"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    value_start_id = "start_id"

    value_project_descriptors = "project_descriptors"

    value_install_specs = "install_specs"

    value_install_group = "install_group"

    value_install_extras = "install_extras"

    value_extra_command_args = "extra_command_args"

    value_venv_driver = "venv_driver"

    value_python = "python"

    value_version = "version"


class PathName(enum.Enum):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    path_proto_code = "proto_code"

    # TODO: use another suffix (not `dir`) as `dir` is specified by `FilesystemObject.fs_object_dir`
    # TODO: make use of it in naming states (instead of using only `path_proto_code`):
    path_proto_dir = "proto_dir"

    # TODO: Add a `feature_topic` for `ref root` (explaining how everything is relative to it):
    path_ref_root = "ref_root"

    # See FT_89_41_35_82.conf_leap.md / primer
    path_primer_conf = f"{ConfLeap.leap_primer.value}_conf"

    # TODO: Instead of `path_conf_client`, use `path_global_conf`:
    # See FT_89_41_35_82.conf_leap.md / client
    path_conf_client = f"conf_{ConfLeap.leap_client.value}"
    path_global_conf = f"{ConfLeap.leap_global.value}_conf"

    # TODO: Instead of `path_conf_env`, use `path_local_conf`:
    # See FT_89_41_35_82.conf_leap.md / env
    path_conf_env = f"conf_{ConfLeap.leap_env.value}"
    path_local_conf = f"{ConfLeap.leap_local.value}_conf"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # TODO: Rename to "lconf_link" (otherwise, `local_conf_symlink_rel_path` does not reflect anything about `lconf` or `leap_env`):
    path_link_name = "link_name"

    path_default_env = "default_env"

    path_selected_env = f"selected_env"

    path_required_python = "required_python"

    # TODO: TODO_41_10_50_01.implement_env_selector.md: What is the FT (feature_topic)?
    path_python_selector = "python_selector"

    path_selected_python = "selected_python"

    path_local_venv = "local_venv"

    path_local_log = "local_log"

    path_local_tmp = "local_tmp"

    path_local_cache = "local_cache"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    path_build_root = "build_root"


class ParsedArg(enum.Enum):

    name_selected_env_dir = f"{PathName.path_selected_env.value}_{FilesystemObject.fs_object_dir.value}"

    name_command = f"{KeyWord.key_run.value}_{CommandAction.action_command.value}"

    name_exec_mode = str(ValueName.value_exec_mode.value)

    name_final_state = str(ValueName.value_final_state.value)


class LogLevel(enum.Enum):
    name_quiet = "quiet"
    name_verbose = "verbose"


class SyntaxArg:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    arg_h = f"-{KeyWord.key_help.value[0]}"
    arg_help = f"--{KeyWord.key_help.value}"

    arg_final_state = f"--{ParsedArg.name_final_state.value}"

    arg_c = f"-{CommandAction.action_command.value[0]}"
    arg_command = f"--{CommandAction.action_command.value}"

    arg_q = f"-{LogLevel.name_quiet.value[0]}"
    arg_quiet = f"--{LogLevel.name_quiet.value}"
    dest_quiet = f"{ValueName.value_stderr_log_level.value}_{LogLevel.name_quiet.value}"

    arg_v = f"-{LogLevel.name_verbose.value[0]}"
    arg_verbose = f"--{LogLevel.name_verbose.value}"
    dest_verbose = f"{ValueName.value_stderr_log_level.value}_{LogLevel.name_verbose.value}"

    arg_e = f"-{KeyWord.key_env.value[0]}"
    arg_env = f"--{KeyWord.key_env.value}"


class SelectorFunc(enum.Enum):
    """
    Lists selector functions (called from standalone `python` scripts).
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # TODO: TODO_41_10_50_01.implement_env_selector.md: What is the FT (feature_topic)?
    # A function of this signature:
    # def select_python_file_abs_path(required_version: tuple[int, int, int]) -> str | None:
    select_python_file_abs_path = "select_python_file_abs_path"


class ConfField(enum.Enum):
    """
    Lists all conf fields from persisted files for every `ConfLeap.*`.
    """

    ####################################################################################################################
    # `ConfLeap.leap_primer`-specific

    # state_ref_root_dir_abs_path_inited:
    field_ref_root_dir_rel_path = f"{PathName.path_ref_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # state_global_conf_dir_abs_path_inited
    field_global_conf_dir_rel_path = f"{PathName.path_global_conf.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    ####################################################################################################################
    # `ConfLeap.leap_client`-specific
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # FT_92_51_35_07.local_env_link.md: symlink name:
    # state_local_conf_symlink_abs_path_inited:
    field_local_conf_symlink_rel_path = f"{PathName.path_local_conf.value}_{FilesystemObject.fs_object_symlink.value}_{PathType.path_rel.value}"

    # FT_92_51_35_07.local_env_link.md: default symlink target:
    # state_selected_env_dir_rel_path_inited:
    field_default_env_dir_rel_path = f"{PathName.path_default_env.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    ####################################################################################################################
    # `ConfLeap.leap_env`-specific

    # None at the moment.

    ####################################################################################################################
    # Common overridable `global` and `local` fields: FT_23_37_64_44.global_vs_local.md

    # state_required_python_version_inited:
    field_required_python_version = f"{PathName.path_required_python.value}_{ValueName.value_version.value}"

    # TODO: TODO_41_10_50_01.implement_env_selector.md: What is the FT (feature_topic)?
    # state_python_selector_file_abs_path_inited:
    field_python_selector_file_rel_path = f"{PathName.path_python_selector.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_rel.value}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # state_local_venv_dir_abs_path_inited:
    field_local_venv_dir_rel_path = f"{PathName.path_local_venv.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_log_dir_abs_path_inited:
    field_local_log_dir_rel_path = f"{PathName.path_local_log.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_tmp_dir_abs_path_inited:
    field_local_tmp_dir_rel_path = f"{PathName.path_local_tmp.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_cache_dir_abs_path_inited:
    field_local_cache_dir_rel_path = f"{PathName.path_local_cache.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # state_venv_driver_inited:
    field_venv_driver = f"{ValueName.value_venv_driver.value}"

    # parent of `field_build_root_dir_rel_path` & `field_install_extras`:
    # state_project_descriptors_inited:
    field_project_descriptors = f"{ValueName.value_project_descriptors.value}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    field_install_specs = f"{ValueName.value_install_specs.value}"

    ####################################################################################################################

    # child of `field_project_descriptors`:
    field_build_root_dir_rel_path = f"{PathName.path_build_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # child of `field_project_descriptors`:
    field_install_extras = f"{ValueName.value_install_extras.value}"

    # child of `field_project_descriptors`:
    field_install_group = f"{ValueName.value_install_group.value}"

    ####################################################################################################################

    # child of `field_install_specs`:
    field_extra_command_args = f"{ValueName.value_extra_command_args.value}"


########################################################################################################################
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class VenvDriverBase:

    def get_type(self) -> VenvDriverType:
        raise NotImplementedError()

    def is_mine_venv(
        self,
        local_venv_dir_abs_path: str,
    ) -> bool:
        return self.get_type() == get_venv_type(local_venv_dir_abs_path)

    def create_venv(
        self,
        local_venv_dir_abs_path: str,
    ) -> None:
        logger.info(f"creating `venv` [{local_venv_dir_abs_path}]")
        self._create_venv_impl(local_venv_dir_abs_path)

    def _create_venv_impl(
        self,
        local_venv_dir_abs_path: str,
    ) -> None:
        raise NotImplementedError()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def install_packages(
        self,
        selected_python_file_abs_path: str,
        given_packages: list[str],
    ):
        """
        Install packages (which are not necessarily listed in any of the `pyproject.toml` files).

        This is against UC_78_58_06_54.no_stray_packages.md (in relation to the main `venv`),
        but it is required for separate non-main `venv`-s created for tools (like `uv`).
        """
        sub_proc_args: list[str] = self.get_install_dependencies_cmd(selected_python_file_abs_path)
        sub_proc_args.extend(given_packages)

        logger.info(f"installing packages: {' '.join(sub_proc_args)}")

        subprocess.check_call(sub_proc_args)

    def install_dependencies(
        self,
        ref_root_dir_abs_path: str,
        venv_python_file_abs_path: str,
        constraints_file_abs_path: str,
        project_descriptors: list[dict],
        extra_command_args: list[str],
    ) -> None:
        """
        Install each project from the `project_descriptors`.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        The assumption is that they use `pyproject.toml`.

        See also:
        *   UC_78_58_06_54.no_stray_packages.md
        *   FT_46_37_27_11.editable_install.md
        """

        editable_project_install_args = []
        for project_descriptor in project_descriptors:
            project_build_root_dir_rel_path = project_descriptor[ConfField.field_build_root_dir_rel_path.value]
            project_build_root_dir_abs_path = os.path.join(
                ref_root_dir_abs_path,
                project_build_root_dir_rel_path,
            )

            install_extras: list[str]
            if ConfField.field_install_extras.value in project_descriptor:
                install_extras = project_descriptor[ConfField.field_install_extras.value]
            else:
                install_extras = []
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            editable_project_install_args.append("--editable")
            if len(install_extras) > 0:
                editable_project_install_args.append(f"{project_build_root_dir_abs_path}[{','.join(install_extras)}]")
            else:
                editable_project_install_args.append(f"{project_build_root_dir_abs_path}")

        sub_proc_args = self.get_install_dependencies_cmd(venv_python_file_abs_path)
        sub_proc_args.extend(
            [
                "--constraint",
                constraints_file_abs_path,
            ]
        )
        sub_proc_args.extend(extra_command_args)

        sub_proc_args.extend(editable_project_install_args)

        logger.info(f"installing projects: {' '.join(sub_proc_args)}")

        env_vars = os.environ.copy()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # Adding `venv/bin` is required for `uv` to access `keyring`.
        # See: FT_17_41_51_83.private_artifact_repo.md
        env_vars[ConfConstInput.ext_env_var_PATH] = f"{os.path.dirname(venv_python_file_abs_path)}:{env_vars[ConfConstInput.ext_env_var_PATH]}"

        subprocess.check_call(
            sub_proc_args,
            env=env_vars,
        )

    def get_install_dependencies_cmd(
        self,
        venv_python_file_abs_path: str,
    ) -> list[str]:
        raise NotImplementedError()

    def pin_versions(
        self,
        venv_python_file_abs_path: str,
        constraints_file_abs_path: str,
    ) -> None:
        logger.info(f"generating version constraints file [{constraints_file_abs_path}]")
        with open(constraints_file_abs_path, "w") as f:
            subprocess.check_call(
                self._get_pin_versions_cmd(venv_python_file_abs_path),
                stdout=f,
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _get_pin_versions_cmd(
        self,
        venv_python_file_abs_path: str,
    ) -> list[str]:
        raise NotImplementedError()


class VenvDriverPip(VenvDriverBase):

    def __init__(
        self,
        required_python_version: str,
        selected_python_file_abs_path: str,
        state_local_venv_dir_abs_path_inited: str,
    ):
        self.required_python_version: str = required_python_version
        self.selected_python_file_abs_path: str = selected_python_file_abs_path
        self.state_local_venv_dir_abs_path_inited: str = state_local_venv_dir_abs_path_inited

    def get_type(self) -> VenvDriverType:
        return VenvDriverType.venv_pip
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _create_venv_impl(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        local_venv_dir_abs_path: str,
    ) -> None:
        subprocess.check_call(
            [
                self.selected_python_file_abs_path,
                "-m",
                "venv",
                local_venv_dir_abs_path,
            ]
        )
        # Use the python executable within the created `venv`:
        venv_python_executable = os.path.join(
            local_venv_dir_abs_path,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        subprocess.check_call(
            [
                venv_python_executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ]
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_install_dependencies_cmd(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        venv_python_file_abs_path: str,
    ) -> list[str]:
        return [
            venv_python_file_abs_path,
            "-m",
            "pip",
            "install",
        ]

    def _get_pin_versions_cmd(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        venv_python_file_abs_path: str,
    ) -> list[str]:
        return [
            venv_python_file_abs_path,
            "-m",
            "pip",
            "freeze",
            "--exclude-editable",
        ]
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class VenvDriverUv(VenvDriverBase):

    def __init__(
        self,
        required_python_version: str,
        selected_python_file_abs_path: str,
        state_local_venv_dir_abs_path_inited: str,
        state_local_cache_dir_abs_path_inited: str,
    ):
        self.required_python_version: str = required_python_version
        self.selected_python_file_abs_path: str = selected_python_file_abs_path
        self.state_local_venv_dir_abs_path_inited: str = state_local_venv_dir_abs_path_inited
        self.uv_venv_abs_path: str = os.path.join(
            # TODO: make it relative to "cache/venv" specifically (instead of directly to "cache"):
            state_local_cache_dir_abs_path_inited,
            ConfConstEnv.default_dir_rel_path_venv,
            # TODO: take from config (or default constant):
            "uv.venv",
        )
        self.uv_exec_abs_path: str = os.path.join(
            self.uv_venv_abs_path,
            ConfConstGeneral.file_rel_path_venv_uv,
        )
        self.venv_python_file_abs_path: str = os.path.join(
            self.state_local_venv_dir_abs_path_inited,
            ConfConstGeneral.file_rel_path_venv_python,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_type(self) -> VenvDriverType:
        return VenvDriverType.venv_uv

    def _ensure_uv_is_available(self):
        if not os.path.exists(self.uv_exec_abs_path):
            # To use `VenvDriverType.venv_uv`, use `VenvDriverType.venv_pip` to install `uv` first:
            pip_driver = VenvDriverPip(
                required_python_version=self.required_python_version,
                # TODO: assert python version suitable for `uv` (because this `venv` will be used to install `uv`).
                # NOTE: Create this `venv` (to install `uv`) with whatever `python` runs now:
                selected_python_file_abs_path=self.selected_python_file_abs_path,
                # Instead of `self.state_local_venv_dir_abs_path_inited`,
                # this intermediate driver uses ` self.uv_venv_abs_path`:
                state_local_venv_dir_abs_path_inited=self.uv_venv_abs_path,
            )
            pip_driver.create_venv(self.uv_venv_abs_path)
            uv_exec_venv_python_abs_path = os.path.join(
                self.uv_venv_abs_path,
                ConfConstGeneral.file_rel_path_venv_python,
            )
            pip_driver.install_packages(
                uv_exec_venv_python_abs_path,
                [
                    ConfConstGeneral.name_uv_package,
                ],
            )
        else:
            # Verify `self.uv_exec_abs_path` is functional:
            subprocess.check_call(
                [
                    self.uv_exec_abs_path,
                    "python",
                    "dir",
                ]
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert os.path.isfile(self.uv_exec_abs_path)

    def _create_venv_impl(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        local_venv_dir_abs_path: str,
    ) -> None:

        self._ensure_uv_is_available()

        subprocess.check_call(
            [
                self.uv_exec_abs_path,
                "python",
                "install",
                self.required_python_version,
            ]
        )

        subprocess.check_call(
            [
                self.uv_exec_abs_path,
                "venv",
                # Creates `venv` with the standard `pip`:
                "--seed",
                "--python",
                self.required_python_version,
                local_venv_dir_abs_path,
            ]
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_install_dependencies_cmd(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        venv_python_file_abs_path: str,
    ) -> list[str]:

        self._ensure_uv_is_available()

        return [
            self.uv_exec_abs_path,
            "pip",
            "install",
            "--python",
            # TODO: Clean up `venv_python_file_abs_path` arg:
            # NOTE: Use simple relative path like `${venv_abs_path}/bin/python`.
            #       The `venv_python_file_abs_path` arg passed to this function might be
            #       a `python` exec path internal to `uv` which fails if used directly.
            self.venv_python_file_abs_path,
        ]

    def _get_pin_versions_cmd(
        self,
        # TODO: Do we need this arg if we have `state_local_venv_dir_abs_path_inited`?
        venv_python_file_abs_path: str,
    ) -> list[str]:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        self._ensure_uv_is_available()

        return [
            self.uv_exec_abs_path,
            "pip",
            "freeze",
            "--exclude-editable",
            "--python",
            # TODO: Clean up `venv_python_file_abs_path` arg:
            # NOTE: Use simple relative path like `${venv_abs_path}/bin/python`.
            #       The `venv_python_file_abs_path` arg passed to this function might be
            #       a `python` exec path internal to `uv` which fails if used directly.
            self.venv_python_file_abs_path,
        ]


class VenvDriverType(enum.Enum):
    """
    See UC_09_61_98_94.installer_pip_vs_uv.md
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    venv_pip = VenvDriverPip

    venv_uv = VenvDriverUv


########################################################################################################################


class ShellType(enum.Enum):

    shell_bash = "bash"

    shell_zsh = "zsh"


def remove_protoprimer_env_vars(env_vars: MutableMapping[str, str]) -> MutableMapping[str, str]:
    """
    FT_66_02_54_56.context_isolation.md
    """
    for env_var in EnvVar:
        env_vars.pop(env_var.value, None)
    return env_vars
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class ShellDriverBase:

    def __init__(
        self,
        shell_abs_path: str,
        shell_env_vars: dict[str, str],
        cache_dir_abs_path: str,
        activate_venv: bool = True,
    ):
        self.shell_abs_path: str = shell_abs_path
        self.shell_args: list[str] = [
            self.shell_abs_path,
        ]
        self.shell_env_vars: dict[str, str] = shell_env_vars
        self.cache_dir_abs_path: str = cache_dir_abs_path
        self.activate_venv: bool = activate_venv

    def get_type(self) -> ShellType:
        raise NotImplementedError()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_init_file_basename(self):
        raise NotImplementedError()

    def get_init_file_abs_path(self):
        return os.path.join(
            os.path.join(
                self.cache_dir_abs_path,
                self.get_type().value,
            ),
            self.get_init_file_basename(),
        )

    @staticmethod
    def get_venv_activate_script_abs_path(venv_abs_path: str) -> str:
        return os.path.join(
            venv_abs_path,
            ConfConstGeneral.file_rel_path_venv_activate,
        )

    def write_init_file(
        self,
        venv_abs_path: str,
    ):
        pathlib.Path(os.path.dirname(self.get_init_file_abs_path())).mkdir(
            parents=True,
            exist_ok=True,
        )
        write_text_file(
            self.get_init_file_abs_path(),
            f"""
# Load user settings if available:
test -f ~/{self.get_init_file_basename()} && source ~/{self.get_init_file_basename()} || true
# Activate `venv`:
if [ "{str(self.activate_venv).lower()}" = "true" ]
then
    source {self.get_venv_activate_script_abs_path(venv_abs_path)}
fi
""",
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def configure_interactive_shell(
        self,
        has_command: bool,
    ) -> None:
        """
        Implements: UC_36_72_11_12.pipe_to_execute_with_activated_venv.md
        """
        raise NotImplementedError()

    def run_shell(
        self,
        start_interactive_shell: bool,
        command_line: str | None,
        stderr_log_handler: logging.Handler,
        venv_abs_path: str,
    ) -> int:

        if command_line is None and not start_interactive_shell:
            return 0

        self.write_init_file(venv_abs_path)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        self.configure_interactive_shell(command_line is not None)

        self.shell_args.extend(
            [
                # Always start interactive `shell` (even if it exits immediately in case of `-c`)
                # because we need to override `*rc`-files which activate `venv`:
                "-i",
            ]
        )

        if command_line is not None:
            self.shell_args.extend(
                [
                    "-c",
                    command_line,
                ]
            )

        print_delegate_line(
            self.shell_args,
            stderr_log_handler,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        os.execve(
            self.shell_abs_path,
            self.shell_args,
            self.shell_env_vars,
        )

        # When `os.execve` is mocked:
        # noinspection PyUnreachableCode
        return 0


class ShellDriverBash(ShellDriverBase):

    def get_type(self) -> ShellType:
        return ShellType.shell_bash

    def get_init_file_basename(self):
        return ".bashrc"

    def configure_interactive_shell(
        self,
        has_command: bool,
    ) -> None:
        self.shell_args.extend(
            [
                # `bash` uses explicit override for `.bashrc`:
                "--init-file",
                self.get_init_file_abs_path(),
            ]
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class ShellDriverZsh(ShellDriverBase):

    def get_type(self) -> ShellType:
        return ShellType.shell_zsh

    def get_init_file_basename(self):
        return ".zshrc"

    def configure_interactive_shell(
        self,
        has_command: bool,
    ) -> None:
        if not sys.stdin.closed and not sys.stdin.isatty() and not has_command:
            # Unlike `bash`, `zsh` reads `tty` instead of `stdin` (for UI control) unless `-s` is specified:
            self.shell_args.extend(
                [
                    "-s",
                ]
            )
        # `zsh` takes "dot dir" path to find overridden `.zshrc`:
        self.shell_env_vars["ZDOTDIR"] = os.path.dirname(self.get_init_file_abs_path())
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def _get_shell_driver(
    cache_dir_abs_path: str,
    activate_venv: bool = True,
) -> ShellDriverBase:

    var_shell = "SHELL"
    shell_abs_path: str | None = os.environ.get(var_shell, None)
    shell_driver_type: type[ShellDriverBase]

    if shell_abs_path is None:
        # TODO: Implement `ShellDriverSh` using `/bin/sh` instead:
        logger.warning(f"env var `{var_shell}` is not set - assuming `bash` as default")

        # TODO: How will work on Windows without `shutil`? And without POSIX shell?
        # noinspection PyDeprecation
        shell_abs_path = shutil.which("bash")
        # TODO: If `bash` is not in the `PATH`, fall back to `/bin/sh` instead:
        assert shell_abs_path is not None

        shell_driver_type = ShellDriverBash
    elif os.path.basename(shell_abs_path) == ShellType.shell_bash.value:
        shell_driver_type = ShellDriverBash
    elif os.path.basename(shell_abs_path) == ShellType.shell_zsh.value:
        shell_driver_type = ShellDriverZsh
    else:
        raise ValueError(f"env var `{var_shell}` has unknown value [{shell_abs_path}]")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    return shell_driver_type(
        shell_abs_path=shell_abs_path,
        shell_env_vars=remove_protoprimer_env_vars(os.environ.copy()),
        cache_dir_abs_path=cache_dir_abs_path,
        activate_venv=activate_venv,
    )


########################################################################################################################


class ConfConstGeneral:

    # The project name = package name:
    name_protoprimer_package = "protoprimer"

    name_protoprimer_site_link = "https://protoprimer.readthedocs.io/"

    # Concept name of the FT_90_65_67_62.proto_code.md:
    name_proto_code = "proto_code"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # The main module of the `protoprimer` package (this file):
    name_primer_kernel_module = "primer_kernel"

    # The default name of for the module of the client own copy of `proto_code` (this file).
    # It is a different name from `name_primer_kernel_module` purely to avoid confusion.
    default_proto_code_module = "proto_kernel"

    # File name of the FT_90_65_67_62.proto_code.md:
    default_proto_code_basename = f"{default_proto_code_module}.py"

    python_version_file_basename = ".python-version"

    venv_config_file_basename = "pyvenv.cfg"

    pytest_module = "pytest"

    name_pip_package = "pip"

    name_uv_package = "uv"

    curr_dir_rel_path = "."
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    module_func_separator = ":"

    # TODO: use lambdas to generate based on input (instead of None):
    # This is a value declared for completeness,
    # but unused (evaluated dynamically via the bootstrap process):
    input_based = None

    file_rel_path_venv_bin = os.path.join("bin")

    file_rel_path_venv_python = os.path.join(
        file_rel_path_venv_bin,
        "python",
    )

    file_rel_path_venv_activate = os.path.join(
        file_rel_path_venv_bin,
        "activate",
    )

    file_rel_path_venv_uv = os.path.join(
        file_rel_path_venv_bin,
        name_uv_package,
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    log_section_delimiter = "=" * 5

    min_lines_between_generated_boilerplate = 20

    # FT_56_85_65_41.generated_boilerplate.md
    func_get_proto_code_generated_boilerplate_single_header = lambda module_obj: (
        f"""
################################################################################
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
################################################################################
# This is a (proto) copy of `{module_obj.__name__}` updated automatically.
# It is supposed to be versioned
# (to be available in the target client repo on clone),
# but it should not be linted
# (as its content/style is governed by the source repo).
################################################################################
"""
    )

    # FT_56_85_65_41.generated_boilerplate.md
    func_get_proto_code_generated_boilerplate_multiple_body = lambda module_obj: (
        f"""
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
"""
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    relative_path_field_note: str = f"The path is relative to the `{PathName.path_ref_root.value}` dir specified in the `{ConfField.field_ref_root_dir_rel_path.value}` field."
    common_field_global_note: str = f"This field can be specified in global config (see `{ConfLeap.leap_client.name}`) but it is override-able by local environment-specific config (see `{ConfLeap.leap_env.name}`)."
    common_field_local_note: str = f"This local environment-specific field overrides the global one (see description in `{ConfLeap.leap_client.name}`)."
    func_note_derived_based_on_common = lambda field_name: (f"This value is derived from `{field_name}` in `{ConfLeap.leap_client.name}` (override-able in `{ConfLeap.leap_env.name}`) - see description there.")
    func_note_derived_based_on_conf_leap_field = lambda field_name, conf_leap: (f"This value is derived from `{field_name}` - see description in `{conf_leap.name}`.")


class ConfConstInput:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_input
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

    default_proto_conf_dir_rel_path: str = f"{ConfConstGeneral.name_proto_code}"

    conf_file_ext = "json"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_primer`:
    default_file_basename_conf_primer = f"{ConfConstGeneral.name_protoprimer_package}.{conf_file_ext}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    ext_env_var_VIRTUAL_ENV: str = "VIRTUAL_ENV"
    ext_env_var_PATH: str = "PATH"
    ext_env_var_PYTHONPATH: str = "PYTHONPATH"

    default_PROTOPRIMER_STDERR_LOG_LEVEL: str = "WARNING"

    default_PROTOPRIMER_PY_EXEC: str = StateStride.stride_py_unknown.name

    default_PROTOPRIMER_DO_INSTALL: str = str(True)


class ConfConstPrimer:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_primer
    """

    default_client_conf_dir_rel_path: str = f"{ConfDst.dst_global.value}"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_client`:
    default_file_basename_leap_client: str = ConfConstInput.default_file_basename_conf_primer
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # TODO: Is this still needed if we propagate conf file base name primer -> client -> env?
    default_client_conf_file_rel_path: str = os.path.join(
        default_client_conf_dir_rel_path,
        default_file_basename_leap_client,
    )


class ConfConstClient:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_client
    """

    common_env_name = "common_env"

    # TODO: Is this used? If link_name is not specified, the env conf dir becomes ref root dir:
    default_dir_rel_path_leap_env_link_name: str = os.path.join(ConfDst.dst_local.value)

    # FT_59_95_81_63.env_layout.md / max layout
    default_default_env_dir_rel_path: str = os.path.join(
        # TODO: Use constant:
        "dst",
        common_env_name,
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_env`:
    default_file_basename_leap_env: str = ConfConstInput.default_file_basename_conf_primer

    default_env_conf_file_rel_path: str = os.path.join(
        default_default_env_dir_rel_path,
        default_file_basename_leap_env,
    )

    default_pyproject_toml_basename = "pyproject.toml"


class ConfConstEnv:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_env
    """

    default_dir_rel_path_venv = "venv"

    default_dir_rel_path_log = "log"

    default_dir_rel_path_tmp = "tmp"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    default_dir_rel_path_cache = "cache"

    # NOTE: FT_84_11_73_28.supported_python_versions.md:
    #       The default is `uv` only if it is supported by the selected `python` version:
    default_venv_driver = VenvDriverType.venv_uv.name

    default_project_descriptors = [
        {
            ConfField.field_build_root_dir_rel_path.value: ".",
            ConfField.field_install_extras.value: [],
            ConfField.field_install_group.value: None,
        },
    ]

    default_install_specs = []

    constraints_txt_basename = "constraints.txt"

    # FT_84_11_73_28.supported_python_versions.md:
    latest_known_python_version = "3.14"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        for action in self._actions:
            if isinstance(action, argparse._HelpAction):
                action.help = "Show this help message and exit."

    def error(
        self,
        message,
    ):
        raise ValueError(message)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def _create_parent_argparser():
    parent_argparser = CustomArgumentParser(add_help=False)
    parent_argparser.add_argument(
        # See: FT_38_73_38_52.log_verbosity.md
        SyntaxArg.arg_q,
        SyntaxArg.arg_quiet,
        action="count",
        dest=SyntaxArg.dest_quiet,
        default=0,
        help="Decrease log verbosity level.",
    )
    parent_argparser.add_argument(
        # See: FT_38_73_38_52.log_verbosity.md
        SyntaxArg.arg_v,
        SyntaxArg.arg_verbose,
        action="count",
        dest=SyntaxArg.dest_verbose,
        default=0,
        help="Increase log verbosity level.",
    )
    return parent_argparser
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def _create_child_argparser(parent_argparsers):
    def _create_boot_parser(sub_command_parsers):
        sub_command_desc = "Bootstrap whatever is missing in the environment."
        parser_boot = sub_command_parsers.add_parser(
            ExecMode.mode_boot.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_boot.set_defaults(exec_mode=ExecMode.mode_boot.value)
        parser_boot.add_argument(
            SyntaxArg.arg_e,
            SyntaxArg.arg_env,
            type=str,
            default=None,
            dest=ParsedArg.name_selected_env_dir.value,
            metavar=ParsedArg.name_selected_env_dir.value,
            help=(
                f"Path to the env-specific config dir. "
                f"If specified, `{ExecMode.mode_boot.value}` exec mode creates the symlink to that dir. "
                f"If not specified, the existing symlink is reused. "
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            ),
        )

        parser_boot.add_argument(
            SyntaxArg.arg_c,
            SyntaxArg.arg_command,
            type=str,
            dest=ParsedArg.name_command.value,
            metavar=ParsedArg.name_command.value,
            help="Command to execute after the bootstrap.",
        )
        parser_boot.add_argument(
            # TODO: Remove this arg - it does not support any strong use case:
            # TODO: Use "env_state" as `dest` and `metavar`, but `--state` as option name:
            SyntaxArg.arg_final_state,
            type=str,
            # TODO: Decide to print choices or not (they look too excessive). Maybe print those in `TargetState` only?
            # choices=[state_name.name for state_name in EnvState],
            # Keep the default `None` to indicate there was no user override
            # (and select the actual default in code):
            default=None,
            # TODO: Use "env_state" as `dest` and `metavar`, but `--state` as option name:
            dest=ParsedArg.name_final_state.value,
            metavar=ParsedArg.name_final_state.value,
            help=f"Select final `{EnvState.__name__}` name.",
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _create_reset_parser(sub_command_parsers):
        sub_command_desc = "Bootstrap from scratch: re-create `venv`, re-install dependencies, re-pin versions, ..."
        parser_reset = sub_command_parsers.add_parser(
            ExecMode.mode_reboot.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_reset.set_defaults(exec_mode=ExecMode.mode_reboot.value)

    def _create_eval_parser(sub_command_parsers):
        sub_command_desc = "Evaluate effective config (print it on `stdout`)."
        parser_eval = sub_command_parsers.add_parser(
            ExecMode.mode_eval.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_eval.set_defaults(exec_mode=ExecMode.mode_eval.value)

    def _create_check_parser(sub_command_parsers):
        sub_command_desc = "Check the environment configuration."
        parser_check = sub_command_parsers.add_parser(
            ExecMode.mode_check.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_check.set_defaults(exec_mode=ExecMode.mode_check.value)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    child_argparser = CustomArgumentParser(
        description=(f"The early [{PrimerRuntime.runtime_proto.value}] environment bootstrapper [{KeyWord.key_primer.value}]."),
        parents=parent_argparsers,
        epilog=f"Version: {__version__} | {ConfConstGeneral.name_protoprimer_site_link} | {pathlib.Path(__file__).resolve()}",
    )

    child_argparsers = child_argparser.add_subparsers(
        dest=ParsedArg.name_exec_mode.value,
        title="Exec modes",
        description=f"Select one of the following sub-commands (default: `{ExecMode.mode_boot.value}`):",
        metavar="exec_mode",
    )
    child_argparsers.required = False

    _create_boot_parser(child_argparsers)
    _create_reset_parser(child_argparsers)
    _create_eval_parser(child_argparsers)

    # TODO: TODO_73_71_31_84.exec_mode_check_or_info.md: implement
    # noinspection PyUnreachableCode
    if False:
        _create_check_parser(child_argparsers)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    return child_argparser


def parse_args(remaining_argv=None) -> argparse.Namespace:
    """
    Parse CLI args by creating parent and child (sub-command) parsers.

    This function uses a two-phase parsing to allow common options
    which can be placed anywhere:
    * ... -q boot (option before sub-command `ExecMode.mode_boot`)
    * ... boot -q (option after sub-command `ExecMode.mode_boot`)

    See also: FT_62_88_55_10.CLI_compatibility.md
    """

    if remaining_argv is None:
        remaining_argv = sys.argv[1:]

    # Phase 1: parse common args:
    parent_argparser = _create_parent_argparser()
    (
        parsed_args,
        remaining_argv,
    ) = parent_argparser.parse_known_args(remaining_argv)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # Phase 2: parse sub-command args:
    child_argparser = _create_child_argparser(
        parent_argparsers=[
            parent_argparser,
        ],
    )
    if (
        SyntaxArg.arg_h not in remaining_argv
        and SyntaxArg.arg_help not in remaining_argv
        #
    ):
        try:
            # Try to parse with `ExecMode.mode_boot` as the default sub-command:
            parsed_args = child_argparser.parse_args(
                [ExecMode.mode_boot.value] + remaining_argv,
                namespace=argparse.Namespace(**vars(parsed_args)),
            )
        except ValueError:
            # If that fails, it might be because another sub-command was specified.
            # In that case, parse without any default sub-command.
            try:
                parsed_args = child_argparser.parse_args(
                    remaining_argv,
                    namespace=parsed_args,
                )
            except ValueError as e:
                # It is the real error now:
                logger.error(e)
                # Use code 2 for a syntax error (as `argparse` does):
                exit(2)
    else:
        parsed_args = child_argparser.parse_args(
            remaining_argv,
            namespace=parsed_args,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    return parsed_args


def str_to_bool(v: str) -> bool:
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError(f"[{bool.__name__}]-like value expected.")


########################################################################################################################


class RunStrategy:
    """
    See related:
    *   `ExecMode`
    *   FT_11_27_29_83.exec_mode.md

    TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
          Currently, `RunStrategy` is degenerated into single implementation `ExitCodeReporter`.
          Is it even needed (unless make it useful beyond that)?
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        raise NotImplementedError()


class ExitCodeReporter(RunStrategy):
    """
    This strategy requires the state to return an `int` value (as exit code).
    """

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        """
        This is a trivial implementation.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        No special DAG traversal because nodes traverse their own dependencies.
        But it may not reach all nodes because
        dependencies will be conditionally evaluated by the implementation of those nodes.
        """
        # NOTE: The `EnvContext.final_state` must return `int` with this strategy:
        exit_code: int = state_node.eval_own_state()
        if type(exit_code) is not int:
            raise AssertionError("`exit_code` must be an `int`")
        sys.exit(exit_code)


########################################################################################################################


class StateNode(Generic[ValueType]):
    """
    All nodes form a `StateGraph`, which must be a DAG.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
    ):
        self.env_ctx: EnvContext = env_ctx
        self.state_name: str = state_name
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # Ensure no duplicates:
        assert len(parent_states) == len(set(parent_states))

        self.parent_states: list[str] = parent_states

        assert type(state_name) is str

        for state_parent in parent_states:
            assert type(state_parent) is str

    def get_state_name(self) -> str:
        return self.state_name

    def get_parent_states(self) -> list[str]:
        return self.parent_states

    def eval_parent_state(
        self,
        parent_state: str,
    ) -> typing.Any:
        if parent_state not in self.parent_states:
            raise AssertionError(f"parent_state [{parent_state}] is not parent of [{self.state_name}]")
        return self.env_ctx.state_graph.eval_state(parent_state)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def eval_own_state(self) -> ValueType:
        return self._eval_own_state()

    def _eval_own_state(self) -> ValueType:
        raise NotImplementedError()


########################################################################################################################


# FT_84_11_73_28.supported_python_versions.md:
# With min `python` switched to 3.8, `NodeFactory` can be turned into `typing.Protocol`:
class NodeFactory(Generic[ValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        self.env_ctx: EnvContext = env_ctx

    def create_state_node(self) -> StateNode[ValueType]:
        raise NotImplementedError()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def trivial_factory(state_node_class: type[StateNode]) -> type[StateNode]:
    """
    Class decorator that makes a `StateNode` class act like a factory for itself.

    In other words, the creation of this DAG node does not depend on `GraphCoordinates`.
    """

    def create_state_node(self) -> StateNode:
        return self

    state_node_class.create_state_node = create_state_node
    return state_node_class


########################################################################################################################


class AbstractCachingStateNode(StateNode[ValueType]):
    _parent_states: Callable[[], list[str]] = staticmethod(lambda: [])
    _state_name: Callable[[], str]
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=self._parent_states(),
            state_name=self._state_name(),
        )
        self.is_cached: bool = False
        self.cached_value: ValueType | None = None

    def _eval_own_state(self) -> ValueType:
        if not self.is_cached:

            # Bootstrap all dependencies:
            for state_name in self.parent_states:
                self.eval_parent_state(state_name)

            # See FT_30_24_95_65.state_idempotency.md
            self.cached_value = self._eval_state_once()
            logger.debug(f"state [{self.state_name}] evaluated value [{self.cached_value}]")
            self.is_cached = True
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return self.cached_value

    def _eval_state_once(self) -> ValueType:
        raise NotImplementedError()


class AbstractOverriddenFieldCachingStateNode(AbstractCachingStateNode[ValueType]):
    """
    Base class that overrides field values from `ConfLeap.leap_client` and `ConfLeap.leap_env`.

    See: FT_00_22_19_59.derived_config.md
    """

    def _get_overridden_value_or_default(
        self,
        field_name: str,
        default_field_value: DataValueType,
    ) -> DataValueType:
        """
        Implements config overrides: FT_23_37_64_44.global_vs_local.md
        """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_client_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_client_conf_file_data_loaded.name)
        state_env_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_env_conf_file_data_loaded.name)
        field_value: DataValueType
        if field_name in state_env_conf_file_data_loaded:
            field_value = state_env_conf_file_data_loaded[field_name]
        else:
            field_value = state_client_conf_file_data_loaded.get(field_name, default_field_value)
        return field_value


########################################################################################################################


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_py_exec_var_loaded(AbstractCachingStateNode[StateStride]):

    _state_name = staticmethod(lambda: EnvState.state_input_py_exec_var_loaded.name)

    def _eval_state_once(self) -> ValueType:
        py_exec = StateStride[
            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return self.env_ctx.set_max_stride(py_exec)


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_stderr_log_level_var_loaded(AbstractCachingStateNode[int]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_py_exec_var_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_input_stderr_log_level_var_loaded.name)

    def _eval_state_once(self) -> ValueType:

        loaded_stderr_level: str = os.getenv(
            EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        default_stderr_log_level = getattr(
            logging,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_input_stderr_log_level_var_loaded: int
        try:
            state_input_stderr_log_level_var_loaded = int(loaded_stderr_level)
            if state_input_stderr_log_level_var_loaded < 0:
                logger.warning(f"Unsupported log level value [{loaded_stderr_level}] for `{EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value}`")
                state_input_stderr_log_level_var_loaded = default_stderr_log_level
        except ValueError:
            loaded_stderr_level = loaded_stderr_level.upper()
            defined_value: int | None = getattr(
                logging,
                loaded_stderr_level,
                None,
            )
            if defined_value is None:
                logger.warning(f"Unrecognized log level value [{loaded_stderr_level}] for `{EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value}`")
                defined_value = default_stderr_log_level
            assert isinstance(defined_value, int)

            state_input_stderr_log_level_var_loaded = defined_value

        return state_input_stderr_log_level_var_loaded
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_do_install_var_loaded(AbstractCachingStateNode[bool]):

    _state_name = staticmethod(lambda: EnvState.state_input_do_install_var_loaded.name)

    def _eval_state_once(self) -> ValueType:
        state_input_do_install_var_loaded: bool = str_to_bool(
            os.getenv(
                EnvVar.var_PROTOPRIMER_DO_INSTALL.value,
                ConfConstInput.default_PROTOPRIMER_DO_INSTALL,
            )
        )
        return state_input_do_install_var_loaded


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_default_stderr_log_handler_configured(AbstractCachingStateNode[logging.Handler]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_var_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_default_stderr_log_handler_configured.name)

    def _eval_state_once(self) -> ValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_var_loaded.name)
        assert state_input_stderr_log_level_var_loaded >= 0

        stderr_handler: logging.Handler = _configure_primer_stderr_log_handler(state_input_stderr_log_level_var_loaded)

        return stderr_handler


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_args_parsed(AbstractCachingStateNode[argparse.Namespace]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _state_name = staticmethod(lambda: EnvState.state_args_parsed.name)

    def _eval_state_once(self) -> ValueType:
        """
        Parse the args. In case of `EnvVar.var_PROTOPRIMER_EXEC_MODE` == `ExecMode.mode_start`, skip parsing.
        """
        state_args_parsed: argparse.Namespace
        if os.environ.get(EnvVar.var_PROTOPRIMER_EXEC_MODE.value, None) == ExecMode.mode_start.value:
            # Pretend there is no args except `ExecMode.mode_start`:
            state_args_parsed = parse_args([])
            setattr(
                state_args_parsed,
                ParsedArg.name_exec_mode.value,
                ExecMode.mode_start.value,
            )
        else:
            state_args_parsed = parse_args()
        return state_args_parsed


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_stderr_log_level_eval_finalized(AbstractCachingStateNode[int]):
    """
    There is a narrow window between the default log level is set and this state is evaluated.
    To control the default log level, see `EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL`.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_var_loaded.name,
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_input_stderr_log_level_eval_finalized.name)

    def _eval_state_once(self) -> ValueType:

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_var_loaded.name)

        state_default_stderr_logger_configured: logging.Handler = self.eval_parent_state(EnvState.state_default_stderr_log_handler_configured.name)

        parsed_args = self.eval_parent_state(EnvState.state_args_parsed.name)
        stderr_log_level_quiet_count: int = getattr(
            parsed_args,
            SyntaxArg.dest_quiet,
        )
        stderr_log_level_verbose_count: int = getattr(
            parsed_args,
            SyntaxArg.dest_verbose,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        stderr_log_level_eval_finalized: int
        if stderr_log_level_quiet_count == 0 and stderr_log_level_verbose_count == 0:
            stderr_log_level_eval_finalized = state_input_stderr_log_level_var_loaded
        else:
            # FT_38_73_38_52.log_verbosity.md
            # The base is the numeric value of `ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL`.
            base_log_level: int = getattr(
                logging,
                ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
            )

            relative_log_level = 10 * (stderr_log_level_quiet_count - stderr_log_level_verbose_count)

            stderr_log_level_eval_finalized = base_log_level + relative_log_level

            if stderr_log_level_eval_finalized < logging.NOTSET:
                stderr_log_level_eval_finalized = logging.NOTSET

        state_default_stderr_logger_configured.setLevel(stderr_log_level_eval_finalized)
        assert isinstance(
            state_default_stderr_logger_configured.formatter,
            _PrimerStderrLogFormatter,
        )
        state_default_stderr_logger_configured.formatter.set_verbosity_level(stderr_log_level_eval_finalized)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # Set default log level for subsequent invocations:
        level_var_value: str = logging.getLevelName(stderr_log_level_eval_finalized)
        assert isinstance(level_var_value, str)
        if " " in level_var_value:
            # Due to some hacks in the `python` `logging` library,
            # it may return non-existing level names - use number instead:
            level_var_value = str(stderr_log_level_eval_finalized)

        # Remove stack trace for levels >= WARNING (it will only print the exception itself):
        if stderr_log_level_eval_finalized >= logging.WARNING:
            # Avoid changing that in tests - it changes the global state and causes many tests to fail unexpectedly:
            if not is_test_run():
                sys.tracebacklimit = 0

        return stderr_log_level_eval_finalized


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_exec_mode_arg_loaded(AbstractCachingStateNode[ExecMode]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_input_exec_mode_arg_loaded.name)

    def _eval_state_once(self) -> ValueType:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)
        state_input_exec_mode_arg_loaded: ExecMode = ExecMode(
            getattr(
                state_args_parsed,
                ParsedArg.name_exec_mode.value,
            )
        )
        self.env_ctx.graph_coordinates.exec_mode = state_input_exec_mode_arg_loaded
        return state_input_exec_mode_arg_loaded


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_final_state_eval_finalized(AbstractCachingStateNode[str]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_input_final_state_eval_finalized.name)

    def _eval_state_once(self) -> ValueType:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        state_input_final_state_eval_finalized: str | None
        state_input_final_state_eval_finalized = getattr(
            state_args_parsed,
            ParsedArg.name_final_state.value,
            # NOTE: The value is only set for `ExecMode.mode_boot`, otherwise, this default is used:
            None,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if state_input_final_state_eval_finalized is None:
            # TODO: Fix duplicated logs: try default bootstrap - this line is printed repeatedly.
            #       Pass the arg after the start to subsequent `switch_python` calls.
            logger.info(f"selecting `final_state`[{self.env_ctx.final_state}] as no `{SyntaxArg.arg_final_state}` specified")
            state_input_final_state_eval_finalized = self.env_ctx.final_state

        return state_input_final_state_eval_finalized


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_exec_mode_executed(AbstractCachingStateNode[bool]):
    """
    This is a special node - it traverses ALL nodes.

    BUT: It does not depend on ALL nodes - instead, it uses an exec mode strategy implementation.
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_final_state_eval_finalized.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_exec_mode_executed.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_input_stderr_log_level_eval_finalized = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)
        assert state_input_stderr_log_level_eval_finalized >= 0

        state_input_final_state_eval_finalized: str = self.eval_parent_state(EnvState.state_input_final_state_eval_finalized.name)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        state_node: StateNode = self.env_ctx.state_graph.get_state_node(state_input_final_state_eval_finalized)

        selected_strategy: RunStrategy
        if state_input_exec_mode_arg_loaded is None:
            raise ValueError(f"exec mode is not defined")
        elif state_input_exec_mode_arg_loaded == ExecMode.mode_boot:
            selected_strategy = ExitCodeReporter(self.env_ctx)
        elif state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            selected_strategy = ExitCodeReporter(self.env_ctx)
        elif state_input_exec_mode_arg_loaded == ExecMode.mode_reboot:
            selected_strategy = ExitCodeReporter(self.env_ctx)
        elif state_input_exec_mode_arg_loaded == ExecMode.mode_eval:
            selected_strategy = ExitCodeReporter(self.env_ctx)
            state_node = self.env_ctx.state_graph.get_state_node(EnvState.state_effective_conf_data_printed.name)
        else:
            raise ValueError(f"cannot handle exec mode [{state_input_exec_mode_arg_loaded}]")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        selected_strategy.execute_strategy(state_node)

        return True


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_start_id_var_loaded(AbstractCachingStateNode[str]):

    _state_name = staticmethod(lambda: EnvState.state_input_start_id_var_loaded.name)

    def _eval_state_once(self) -> ValueType:
        return os.getenv(
            EnvVar.var_PROTOPRIMER_START_ID.value,
            get_default_start_id(),
        )


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_input_proto_code_file_abs_path_var_loaded(AbstractCachingStateNode[str]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _state_name = staticmethod(lambda: EnvState.state_input_proto_code_file_abs_path_var_loaded.name)

    def _eval_state_once(self) -> ValueType:
        state_input_proto_code_file_abs_path_var_loaded: str | None = os.getenv(
            EnvVar.var_PROTOPRIMER_PROTO_CODE.value,
            None,
        )
        if state_input_proto_code_file_abs_path_var_loaded is not None:
            if not os.path.isabs(state_input_proto_code_file_abs_path_var_loaded):
                raise AssertionError(f"`{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}` must specify absolute path")
            if not os.path.isfile(state_input_proto_code_file_abs_path_var_loaded):
                raise AssertionError(f"file {state_input_proto_code_file_abs_path_var_loaded} is not available")
        return state_input_proto_code_file_abs_path_var_loaded


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_stride_py_arbitrary_reached(AbstractCachingStateNode[StateStride]):
    """
    Implements UC_90_98_17_93.run_under_venv.md.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_py_arbitrary_reached.name)

    def _eval_state_once(self) -> ValueType:

        state_stride_py_arbitrary_reached: StateStride = StateStride.stride_py_arbitrary

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if self.env_ctx.has_stride_reached(next_stride=state_stride_py_arbitrary_reached):
            return self.env_ctx.set_max_stride(state_stride_py_arbitrary_reached)

        if (
            (os.environ.get(EnvVar.var_PROTOPRIMER_PROTO_CODE.value, None) is not None)
            and state_input_exec_mode_arg_loaded == ExecMode.mode_start
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        ):
            # The only reason for `EnvState.state_stride_py_arbitrary_reached`
            # is to obtain `proto_code` abs path in `EnvState.state_proto_code_file_abs_path_inited`.
            # Skip `python` switching for `ExecMode.mode_start` as the env var already set:
            return self.env_ctx.set_max_stride(state_stride_py_arbitrary_reached)

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        log_python_context(logging.DEBUG)

        # UC_90_98_17_93.run_under_venv.md
        # Switch out of the current `venv` -
        # it might be a wrong one,
        # and even if it is the right one,
        # child states require out of `venv` execution.

        cleaned_env = os.environ.copy()

        orig_venv_abs_path = cleaned_env.pop(ConfConstInput.ext_env_var_VIRTUAL_ENV, None)
        orig_PYTHONPATH_value = cleaned_env.pop(ConfConstInput.ext_env_var_PYTHONPATH, None)
        orig_PATH_value: str = cleaned_env.get(ConfConstInput.ext_env_var_PATH, "")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # TODO: Is this (above and below) manual clean-up necessary after we switched to isolated `-I` `python` mode?
        if orig_venv_abs_path is not None:
            # Remove `venv/bin` dir from the `PATH` env var:
            venv_bin_abs_path: str = os.path.join(
                orig_venv_abs_path,
                "bin",
            )
            PATH_parts: list[str] = orig_PATH_value.split(os.pathsep)
            cleaned_path_parts = [p for p in PATH_parts if p != venv_bin_abs_path]
            cleaned_env[ConfConstInput.ext_env_var_PATH] = os.pathsep.join(cleaned_path_parts)

        path_to_curr_python = get_path_to_curr_python()
        path_to_next_python = get_path_to_base_python()
        return switch_python(
            curr_python_path=path_to_curr_python,
            next_py_exec=self.env_ctx.set_max_stride(state_stride_py_arbitrary_reached),
            next_python_path=path_to_next_python,
            start_id=state_input_start_id_var_loaded,
            proto_code_abs_file_path=None,
            required_environ=cleaned_env,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_proto_code_file_abs_path_inited(AbstractCachingStateNode[str]):
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
            EnvState.state_stride_py_arbitrary_reached.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_proto_code_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_stride_py_arbitrary_reached: StateStride = self.eval_parent_state(EnvState.state_stride_py_arbitrary_reached.name)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        state_input_proto_code_file_abs_path_var_loaded: str | None = self.eval_parent_state(EnvState.state_input_proto_code_file_abs_path_var_loaded.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert self.env_ctx.get_stride().value >= StateStride.stride_py_arbitrary.value

        state_proto_code_file_abs_path_inited: str
        if self.env_ctx.get_stride().value >= StateStride.stride_py_venv.value:
            if state_input_proto_code_file_abs_path_var_loaded is None:
                raise AssertionError(f"`{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}` is not specified at `{self.env_ctx.get_stride().name}` [{self.env_ctx.get_stride()}]")
            # rely on the path given in the `EnvVar.var_PROTOPRIMER_PROTO_CODE` env var:
            state_proto_code_file_abs_path_inited = state_input_proto_code_file_abs_path_var_loaded
        else:
            log_python_context()
            if os.environ.get(EnvVar.var_PROTOPRIMER_MOCKED_RESTART.value, None) is None:
                if state_input_exec_mode_arg_loaded != ExecMode.mode_start:
                    if self.env_ctx.get_stride().value == StateStride.stride_py_arbitrary.value:
                        state_proto_code_file_abs_path_inited = os.path.abspath(__file__)
                    else:
                        # Anything except `StateStride.stride_py_arbitrary`
                        # relies on `EnvVar.var_PROTOPRIMER_PROTO_CODE`:
                        assert state_input_proto_code_file_abs_path_var_loaded is not None
                        state_proto_code_file_abs_path_inited = state_input_proto_code_file_abs_path_var_loaded
                        assert self.env_ctx.get_stride().value < StateStride.stride_py_venv.value
                        if self.env_ctx.get_stride().value > StateStride.stride_py_unknown.value:
                            # NOTE: Even `StateStride.stride_py_required` may
                            #       have `py_exec` in `venv` (not the dedicated, just current):
                            if self.env_ctx.get_stride().value != StateStride.stride_py_required.value:
                                assert not is_venv()
                            else:
                                if is_venv():
                                    logger.warning(f"`sys.executable` [{sys.executable}] for [{StateStride.stride_py_required.name}] evaluated from config should ideally be outside `venv`")
                else:
                    # `ExecMode.mode_start` relies only on the `EnvVar.var_PROTOPRIMER_PROTO_CODE` env var:
                    assert state_input_proto_code_file_abs_path_var_loaded is not None
                    state_proto_code_file_abs_path_inited = state_input_proto_code_file_abs_path_var_loaded
            else:
                # `EnvVar.var_PROTOPRIMER_MOCKED_RESTART`: rely on the path
                # given in the `EnvVar.var_PROTOPRIMER_PROTO_CODE` env var:
                assert state_input_proto_code_file_abs_path_var_loaded is not None
                state_proto_code_file_abs_path_inited = state_input_proto_code_file_abs_path_var_loaded
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert os.path.isabs(state_proto_code_file_abs_path_inited)
        return state_proto_code_file_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_primer_conf_file_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_proto_code_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_primer_conf_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:
        """
        Select the conf file name from a list of candidate basenames (whichever is found first).
        """
        state_proto_code_file_abs_path_inited = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        proto_code_dir_abs_path: str = os.path.dirname(state_proto_code_file_abs_path_inited)

        candidate_basenames = []
        conf_basename_from_env = os.environ.get(EnvVar.var_PROTOPRIMER_CONF_BASENAME.value, None)
        if conf_basename_from_env is not None:
            candidate_basenames.append(conf_basename_from_env)

        candidate_basenames.extend(
            [
                f"{pathlib.Path(sys.argv[0]).stem}.{ConfConstInput.conf_file_ext}",
                f"{pathlib.Path(state_proto_code_file_abs_path_inited).stem}.{ConfConstInput.conf_file_ext}",
                ConfConstInput.default_file_basename_conf_primer,
            ]
        )

        for candidate_basename in candidate_basenames:
            candidate_conf_file_abs_path = os.path.join(
                proto_code_dir_abs_path,
                candidate_basename,
            )
            logger.debug(f"candidate conf file name: {candidate_conf_file_abs_path}")
            if os.path.exists(candidate_conf_file_abs_path):
                return candidate_conf_file_abs_path
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # Use `ConfConstInput.default_file_basename_conf_primer` even if not found
        # because it names conf files for other `ConfLeap.*`:
        return os.path.join(
            proto_code_dir_abs_path,
            ConfConstInput.default_file_basename_conf_primer,
        )


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_primer_conf_file_data_loaded(AbstractCachingStateNode[dict]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_primer_conf_file_data_loaded.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:
        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)
        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_primer_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_primer_conf_file_abs_path_inited):
            file_data = read_json_file(state_primer_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            warn_once_at_state_stride(
                missing_conf_file_message(state_primer_conf_file_abs_path_inited),
                self.env_ctx.get_stride(),
            )
            file_data = {}

        if can_print_effective_config(self):

            # Print `ConfLeap.leap_input` data together:
            # ===
            # `ConfLeap.leap_input`:
            print(
                json.dumps(
                    {
                        ConfLeap.leap_input.name: {
                            EnvState.state_proto_code_file_abs_path_inited.name: state_proto_code_file_abs_path_inited,
                            EnvState.state_primer_conf_file_abs_path_inited.name: state_primer_conf_file_abs_path_inited,
                        }
                    },
                    indent=4,
                )
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            # ===
            # `ConfLeap.leap_primer`:
            print(
                json.dumps(
                    {
                        ConfLeap.leap_primer.name: file_data,
                    },
                    indent=4,
                )
            )

        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_ref_root_dir_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_ref_root_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:
        state_proto_code_file_abs_path_inited = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)

        proto_code_dir_abs_path: str = os.path.dirname(state_proto_code_file_abs_path_inited)

        state_primer_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_primer_conf_file_data_loaded.name)

        field_client_dir_rel_path: str | None = state_primer_conf_file_data_loaded.get(ConfField.field_ref_root_dir_rel_path.value, None)

        state_ref_root_dir_abs_path_inited: str
        if field_client_dir_rel_path is None:
            warn_once_at_state_stride(
                f"Field `{ConfField.field_ref_root_dir_rel_path.value}` is [{field_client_dir_rel_path}] - use [{ExecMode.mode_eval.value}] sub-command for description.",
                self.env_ctx.get_stride(),
            )
            state_ref_root_dir_abs_path_inited = proto_code_dir_abs_path
        else:
            state_ref_root_dir_abs_path_inited = os.path.join(
                proto_code_dir_abs_path,
                field_client_dir_rel_path,
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_ref_root_dir_abs_path_inited = os.path.normpath(state_ref_root_dir_abs_path_inited)

        assert os.path.isabs(state_ref_root_dir_abs_path_inited)
        return state_ref_root_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_global_conf_dir_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_primer_conf_file_data_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_global_conf_dir_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_primer_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_primer_conf_file_data_loaded.name)

        field_client_config_dir_rel_path: str | None = state_primer_conf_file_data_loaded.get(ConfField.field_global_conf_dir_rel_path.value, None)

        state_global_conf_dir_abs_path_inited: str | None
        if field_client_config_dir_rel_path is None:
            state_global_conf_dir_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                ConfConstPrimer.default_client_conf_dir_rel_path,
            )
        else:
            state_global_conf_dir_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                field_client_config_dir_rel_path,
            )

        return state_global_conf_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_global_conf_file_abs_path_inited(AbstractCachingStateNode[str]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_primer_conf_file_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_global_conf_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_primer_conf_file_abs_path_inited.name)
        conf_file_base_name = os.path.basename(state_primer_conf_file_abs_path_inited)

        state_global_conf_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_global_conf_dir_abs_path_inited.name)

        state_global_conf_file_abs_path_inited: str = os.path.join(
            state_global_conf_dir_abs_path_inited,
            conf_file_base_name,
        )

        return state_global_conf_file_abs_path_inited
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_client_conf_file_data_loaded(AbstractCachingStateNode[dict]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_client_conf_file_data_loaded.name)

    def _eval_state_once(self) -> ValueType:

        state_global_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_global_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_global_conf_file_abs_path_inited):
            file_data = read_json_file(state_global_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            warn_once_at_state_stride(
                missing_conf_file_message(state_global_conf_file_abs_path_inited),
                self.env_ctx.get_stride(),
            )
            file_data = {}
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if can_print_effective_config(self):
            print(
                json.dumps(
                    {
                        ConfLeap.leap_client.name: file_data,
                    },
                    indent=4,
                )
            )

        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_selected_env_dir_rel_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_selected_env_dir_rel_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        client_local_env_dir_any_path: str | None = self._select_client_local_env_dir_any_path()
        if client_local_env_dir_any_path is None:
            return None

        client_local_env_dir_abs_path: str = self._select_client_local_env_dir_abs_path(client_local_env_dir_any_path)

        if not os.path.isdir(client_local_env_dir_abs_path):
            raise AssertionError(f"`{PathName.path_selected_env.value}` [{client_local_env_dir_abs_path}] must be a dir.")

        state_ref_root_dir_abs_path_inited = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
        if not is_sub_path(
            client_local_env_dir_abs_path,
            state_ref_root_dir_abs_path_inited,
        ):
            raise AssertionError(f"`{PathName.path_selected_env.value}` [{client_local_env_dir_abs_path}] is not under `{EnvState.state_ref_root_dir_abs_path_inited.name}` [{state_ref_root_dir_abs_path_inited}].")

        state_selected_env_dir_rel_path_inited: str = os.path.normpath(
            rel_path(
                client_local_env_dir_abs_path,
                state_ref_root_dir_abs_path_inited,
            )
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert ".." not in pathlib.Path(state_selected_env_dir_rel_path_inited).parts

        return state_selected_env_dir_rel_path_inited

    def _select_client_local_env_dir_any_path(self) -> str | None:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)
        env_conf_dir_any_path: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_selected_env_dir.value,
            # NOTE: The value is only set for `ExecMode.mode_boot`, otherwise, this default is used:
            None,
        )
        if env_conf_dir_any_path is None:
            # Use the default env configured:
            state_client_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_client_conf_file_data_loaded.name)
            field_default_env_dir_rel_path: str | None = state_client_conf_file_data_loaded.get(ConfField.field_default_env_dir_rel_path.value, None)
            if field_default_env_dir_rel_path is None:
                warn_once_at_state_stride(
                    f"Field `{ConfField.field_default_env_dir_rel_path.value}` is [{field_default_env_dir_rel_path}] - use [{ExecMode.mode_eval.value}] sub-command for description.",
                    self.env_ctx.get_stride(),
                )
                return None
            if os.path.isabs(field_default_env_dir_rel_path):
                # Disable wrong complain about `.value`:
                # noinspection PyUnresolvedReferences
                raise AssertionError(f"Field `{ConfField.field_default_env_dir_rel_path.value}` must be a relative path.")
            return field_default_env_dir_rel_path
        else:
            return env_conf_dir_any_path
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _select_client_local_env_dir_abs_path(
        self,
        client_local_env_dir_any_path: str,
    ) -> str:
        """
        Determine the target dir abs path by trying the path it is relative to.

        *   If the input path is already absolute, return as is.
        *   Use ref root as the base first.
        *   Use curr dir as the base last.
        """

        if os.path.isabs(client_local_env_dir_any_path):
            return client_local_env_dir_any_path
        else:
            state_ref_root_dir_abs_path_inited = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
            for base_dir_abs_path in [
                state_ref_root_dir_abs_path_inited,
                os.getcwd(),
            ]:
                abs_path = os.path.join(
                    base_dir_abs_path,
                    client_local_env_dir_any_path,
                )
                if os.path.isdir(abs_path):
                    return abs_path
            raise AssertionError(f"`{PathName.path_selected_env.value}` [{client_local_env_dir_any_path}] is relative to neither `{PathName.path_ref_root.value}` [{state_ref_root_dir_abs_path_inited}] nor curr dir [{os.getcwd()}].")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_conf_symlink_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_selected_env_dir_rel_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_conf_symlink_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_selected_env_dir_rel_path_inited: str | None = self.eval_parent_state(EnvState.state_selected_env_dir_rel_path_inited.name)

        # TODO: TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md
        #       This is `None` when (A) config is missing (B) no CLI arg.
        #       But do we want to use `gconf` as target for `lconf`?
        if state_selected_env_dir_rel_path_inited is None:
            # No symlink target => no `conf_leap` => use `client_conf` instead of `env_conf`:
            return state_ref_root_dir_abs_path_inited

        state_client_conf_file_data_loaded: dict = self.eval_parent_state(EnvState.state_client_conf_file_data_loaded.name)
        client_env_conf_link_name_dir_rel_path: str | None = state_client_conf_file_data_loaded.get(ConfField.field_local_conf_symlink_rel_path.value, None)

        # Convert to absolute:
        state_local_conf_symlink_abs_path_inited: str
        if client_env_conf_link_name_dir_rel_path is None:
            state_local_conf_symlink_abs_path_inited = state_ref_root_dir_abs_path_inited
        else:
            if os.path.isabs(client_env_conf_link_name_dir_rel_path):
                raise AssertionError(f"Field `{ConfField.field_local_conf_symlink_rel_path.value}` cannot be absolute [{client_env_conf_link_name_dir_rel_path}]")
            state_local_conf_symlink_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                client_env_conf_link_name_dir_rel_path,
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if os.path.exists(state_local_conf_symlink_abs_path_inited):
            if os.path.islink(state_local_conf_symlink_abs_path_inited):
                if os.path.isdir(state_local_conf_symlink_abs_path_inited):
                    if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
                        # Nothing to do:
                        pass
                    else:
                        # Compare the existing link target and the configured one:
                        conf_dir_path = os.path.normpath(os.readlink(state_local_conf_symlink_abs_path_inited))
                        if state_selected_env_dir_rel_path_inited != conf_dir_path:
                            # TODO: TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md
                            #       If symlink target does not match default env, why not reset instead of raising?
                            #       If we do not reset automatically, user has to do it manually.
                            #       More over, symlink matching default env may actually be normal...
                            #       What if user wants to keep "decision" of what env he uses in that symlink?
                            #       The automatic reset must only be done when --env arg is specified.
                            raise AssertionError(f"The symlink [{state_local_conf_symlink_abs_path_inited}] target [{conf_dir_path}] is not the same as the provided target [{state_selected_env_dir_rel_path_inited}].")
                else:
                    raise AssertionError(f"The symlink [{state_local_conf_symlink_abs_path_inited}] target [{state_local_conf_symlink_abs_path_inited}] is not a directory.")
            else:
                raise AssertionError(f"The entry [{state_local_conf_symlink_abs_path_inited}] is not a symlink.")
        else:
            os.symlink(
                os.path.normpath(state_selected_env_dir_rel_path_inited),
                state_local_conf_symlink_abs_path_inited,
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return state_local_conf_symlink_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_conf_file_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_primer_conf_file_abs_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_conf_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_primer_conf_file_abs_path_inited.name)
        conf_file_base_name = os.path.basename(state_primer_conf_file_abs_path_inited)

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_conf_symlink_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_local_conf_file_abs_path_inited = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            conf_file_base_name,
        )

        return state_local_conf_file_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_env_conf_file_data_loaded(AbstractCachingStateNode[dict]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_env_conf_file_data_loaded.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:
        state_local_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_local_conf_file_abs_path_inited):
            file_data = read_json_file(state_local_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            # TODO: Still warn when required for some fields:
            # noinspection PyUnreachableCode
            if False:
                warn_once_at_state_stride(
                    missing_conf_file_message(state_local_conf_file_abs_path_inited),
                    self.env_ctx.get_stride(),
                )
            file_data = {}

        if can_print_effective_config(self):
            print(
                json.dumps(
                    {
                        ConfLeap.leap_env.name: file_data,
                    },
                    indent=4,
                )
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_required_python_version_inited(AbstractOverriddenFieldCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_required_python_version_inited.name)

    def _eval_state_once(self) -> ValueType:
        state_required_python_version_inited: str | None = self._get_overridden_value_or_default(
            ConfField.field_required_python_version.value,
            None,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)

        if state_required_python_version_inited is None:
            python_version_file_abs_path: str | None = find_python_version_file(state_ref_root_dir_abs_path_inited)
            if python_version_file_abs_path is None:
                raise AssertionError(f"Both field [{ConfField.field_required_python_version.name}] value is [{state_required_python_version_inited}] and no file [{ConfConstGeneral.python_version_file_basename}] found walking up from [{state_ref_root_dir_abs_path_inited}] dir.")
            logger.info(f"Using file [{python_version_file_abs_path}] as field [{ConfField.field_required_python_version.name}] value is [{state_required_python_version_inited}].")
            state_required_python_version_inited = read_text_file(python_version_file_abs_path).strip()

        assert state_required_python_version_inited is not None
        logger.debug(f"raw `state_required_python_version_inited` [{state_required_python_version_inited}]")

        # normalize:
        python_version: tuple[int, int, int] = parse_python_version(state_required_python_version_inited)
        state_required_python_version_inited = f"{python_version[0]}.{python_version[1]}.{python_version[2]}"

        return state_required_python_version_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_python_selector_file_abs_path_inited(AbstractOverriddenFieldCachingStateNode[str]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_python_selector_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        python_selector_file_rel_path: str | None = self._get_overridden_value_or_default(
            ConfField.field_python_selector_file_rel_path.value,
            None,
        )

        state_python_selector_file_abs_path_inited: str | None
        if python_selector_file_rel_path is not None:
            state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
            state_python_selector_file_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                python_selector_file_rel_path,
            )
        else:
            state_python_selector_file_abs_path_inited = None
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return state_python_selector_file_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_selected_python_file_abs_path_inited(AbstractCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_required_python_version_inited.name,
            EnvState.state_python_selector_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_selected_python_file_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_python_selector_file_abs_path_inited: str | None = self.eval_parent_state(EnvState.state_python_selector_file_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_required_python_version_inited: str = self.eval_parent_state(EnvState.state_required_python_version_inited.name)

        required_python_version: tuple[int, int, int] = parse_python_version(state_required_python_version_inited)

        state_selected_python_file_abs_path_inited: str | None = probe_python_file_abs_path(
            state_python_selector_file_abs_path_inited,
            required_python_version,
        )

        return state_selected_python_file_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_venv_dir_abs_path_inited(AbstractOverriddenFieldCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_venv_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_local_venv_dir_abs_path_inited: str = self._get_overridden_value_or_default(
            ConfField.field_local_venv_dir_rel_path.value,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_local_venv_dir_abs_path_inited):
            state_ref_root_dir_abs_path_inited = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)
            state_local_venv_dir_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                state_local_venv_dir_abs_path_inited,
            )

        assert os.path.isabs(state_local_venv_dir_abs_path_inited)
        return state_local_venv_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_log_dir_abs_path_inited(AbstractOverriddenFieldCachingStateNode[str]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_log_dir_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        field_local_log_dir_rel_path: str = self._get_overridden_value_or_default(
            ConfField.field_local_log_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_log,
        )

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)

        state_local_log_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_log_dir_rel_path,
        )
        state_local_log_dir_abs_path_inited = os.path.normpath(state_local_log_dir_abs_path_inited)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert os.path.isabs(state_local_log_dir_abs_path_inited)
        return state_local_log_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_tmp_dir_abs_path_inited(AbstractOverriddenFieldCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_tmp_dir_abs_path_inited.name)

    def _eval_state_once(self) -> ValueType:

        field_local_tmp_dir_rel_path: str = self._get_overridden_value_or_default(
            ConfField.field_local_tmp_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_tmp,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)

        state_local_tmp_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_tmp_dir_rel_path,
        )
        state_local_tmp_dir_abs_path_inited = os.path.normpath(state_local_tmp_dir_abs_path_inited)

        assert os.path.isabs(state_local_tmp_dir_abs_path_inited)
        return state_local_tmp_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_local_cache_dir_abs_path_inited(AbstractOverriddenFieldCachingStateNode[str]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_local_cache_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        field_local_cache_dir_rel_path: str = self._get_overridden_value_or_default(
            ConfField.field_local_cache_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_cache,
        )

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)

        state_local_cache_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_cache_dir_rel_path,
        )
        state_local_cache_dir_abs_path_inited = os.path.normpath(state_local_cache_dir_abs_path_inited)

        assert os.path.isabs(state_local_cache_dir_abs_path_inited)
        return state_local_cache_dir_abs_path_inited


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_venv_driver_inited(AbstractOverriddenFieldCachingStateNode[VenvDriverType]):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_venv_driver_inited.name)

    def _eval_state_once(self) -> ValueType:

        state_selected_python_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_selected_python_file_abs_path_inited.name)

        # FT_84_11_73_28.supported_python_versions.md:
        uv_min_version: tuple[int, int, int] = (3, 8, 0)
        selected_version: tuple[int, int, int] = get_python_version(state_selected_python_file_abs_path_inited)

        default_venv_driver: str
        if selected_version < uv_min_version:
            default_venv_driver = VenvDriverType.venv_pip.name
        else:
            default_venv_driver = ConfConstEnv.default_venv_driver
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_venv_driver_inited: VenvDriverType
        venv_driver_name: str | None = os.environ.get(EnvVar.var_PROTOPRIMER_VENV_DRIVER.value, None)
        if venv_driver_name is None:
            state_venv_driver_inited = VenvDriverType[
                self._get_overridden_value_or_default(
                    ConfField.field_venv_driver.value,
                    default_venv_driver,
                )
            ]
        else:
            state_venv_driver_inited = VenvDriverType[venv_driver_name]

        if (
            selected_version < uv_min_version
            and state_venv_driver_inited == VenvDriverType.venv_uv
            #
        ):
            logger.warning(f"Overriding package driver [{state_venv_driver_inited}] to [{VenvDriverType.venv_pip}] because selected `python` version [{selected_version}] is below minimum required [{uv_min_version}] for [{VenvDriverType.venv_uv}]")
            state_venv_driver_inited = VenvDriverType.venv_pip

        return state_venv_driver_inited
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_project_descriptors_inited(AbstractOverriddenFieldCachingStateNode[list]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_project_descriptors_inited.name)

    def _eval_state_once(self) -> ValueType:

        project_descriptors: list = self._get_overridden_value_or_default(
            ConfField.field_project_descriptors.value,
            ConfConstEnv.default_project_descriptors,
        )

        return project_descriptors
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_install_specs_inited(AbstractOverriddenFieldCachingStateNode[list]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_install_specs_inited.name)

    def _eval_state_once(self) -> ValueType:

        install_specs: list = self._get_overridden_value_or_default(
            ConfField.field_install_specs.value,
            ConfConstEnv.default_install_specs,
        )

        return install_specs
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_derived_conf_data_loaded(AbstractCachingStateNode[dict]):
    """
    Implements: FT_00_22_19_59.derived_config.md
    """

    _state_name = staticmethod(lambda: EnvState.state_derived_conf_data_loaded.name)

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        self.derived_data_env_states: list[str] = [
            # ===
            # `ConfLeap.leap_input`
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_primer`
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_client`
            EnvState.state_selected_env_dir_rel_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_env`
            # nothing specific
            # ===
            # `ConfLeap.leap_derived`
            EnvState.state_required_python_version_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_project_descriptors_inited.name,
        ]
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # TODO: Is this needed given the list of dependencies in `derived_data_env_states`?
        parent_states = [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_primer_conf_file_data_loaded.name,
            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            *self.derived_data_env_states,
        ]

        # The list parent states sorted by their definition order in `EnvState`:
        parent_states.sort(key=lambda parent_state: [enum_item.name for enum_item in EnvState].index(parent_state))

        self._parent_states = lambda: parent_states
        super().__init__(env_ctx=env_ctx)

    def _eval_state_once(self) -> ValueType:

        config_data_derived = {}
        for derived_data_env_state in self.derived_data_env_states:
            evaluated_value = self.eval_parent_state(derived_data_env_state)
            if isinstance(evaluated_value, enum.Enum):
                config_data_derived[derived_data_env_state] = evaluated_value.name
            else:
                config_data_derived[derived_data_env_state] = evaluated_value
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if can_print_effective_config(self):
            print(
                json.dumps(
                    {
                        ConfLeap.leap_derived.name: config_data_derived,
                    },
                    indent=4,
                )
            )

        return config_data_derived


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_effective_conf_data_printed(AbstractCachingStateNode[int]):
    """
    Implements: FT_19_44_42_19.effective_config.md
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_derived_conf_data_loaded.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_effective_conf_data_printed.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:
        # Nothing to do:
        # If we reach this state,
        # then, transitively, effective configs for all `ConfLeap.*` has been printed.
        return 0


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_default_file_log_handler_configured(AbstractCachingStateNode[logging.Handler]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_default_file_log_handler_configured.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        state_local_log_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_log_dir_abs_path_inited.name)

        state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

        script_path = sys.argv[0]
        script_name = os.path.basename(script_path)

        file_handler = _configure_primer_file_log_handler(
            script_name,
            state_input_start_id_var_loaded,
            state_input_stderr_log_level_eval_finalized,
            state_local_log_dir_abs_path_inited,
        )

        return file_handler

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
# noinspection PyPep8Naming
class Bootstrapper_state_stride_py_required_reached_not_mode_start(AbstractCachingStateNode[StateStride]):
    """
    Recursively runs this script inside the `python` interpreter required by the client.

    The `python` interpreter required by the client is saved into `field_selected_python_file_abs_path`.
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_default_file_log_handler_configured.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_py_required_reached.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_stride_py_required_reached: StateStride = StateStride.stride_py_required

        if self.env_ctx.has_stride_reached(next_stride=state_stride_py_required_reached):
            return self.env_ctx.set_max_stride(state_stride_py_required_reached)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_default_file_log_handler_configured = self.eval_parent_state(EnvState.state_default_file_log_handler_configured.name)

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_local_tmp_dir_abs_path_inited = self.eval_parent_state(EnvState.state_local_tmp_dir_abs_path_inited.name)

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)

        state_selected_python_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_selected_python_file_abs_path_inited.name)
        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert not is_sub_path(
            state_selected_python_file_abs_path_inited,
            state_local_venv_dir_abs_path_inited,
        ), f"Configured `python` [{state_selected_python_file_abs_path_inited}] must be outside of configured `venv` [{state_local_venv_dir_abs_path_inited}]"

        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        assert not is_sub_path(
            path_to_curr_python,
            state_local_venv_dir_abs_path_inited,
        ), f"Current `python` [{path_to_curr_python}] must be outside of the `venv` [{state_local_venv_dir_abs_path_inited}]."

        if path_to_curr_python != state_selected_python_file_abs_path_inited:
            assert self.env_ctx.get_stride().value <= StateStride.stride_py_arbitrary.value
            return switch_python(
                curr_python_path=path_to_curr_python,
                next_py_exec=self.env_ctx.set_max_stride(state_stride_py_required_reached),
                next_python_path=state_selected_python_file_abs_path_inited,
                start_id=state_input_start_id_var_loaded,
                proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
            )
        else:
            assert self.env_ctx.get_stride().value <= StateStride.stride_py_required.value
            return skip_python(
                "already required `python` path",
                curr_py_exec=self.env_ctx.get_stride(),
                next_py_exec=self.env_ctx.set_max_stride(state_stride_py_required_reached),
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_stride_py_required_reached_mode_start(AbstractCachingStateNode[StateStride]):
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_default_file_log_handler_configured.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_py_required_reached.name)

    def _eval_state_once(self) -> ValueType:

        state_stride_py_required_reached: StateStride = StateStride.stride_py_required
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if self.env_ctx.has_stride_reached(next_stride=state_stride_py_required_reached):
            return self.env_ctx.set_max_stride(state_stride_py_required_reached)

        return self.env_ctx.set_max_stride(state_stride_py_required_reached)


# noinspection PyPep8Naming
class Factory_state_stride_py_required_reached(NodeFactory[StateStride]):

    def create_state_node(self) -> StateNode[ValueType]:
        assert self.env_ctx.graph_coordinates.exec_mode is not None

        # The only reason for `EnvState.state_stride_py_required_reached`
        # is to use the required `python` to create a `venv`.
        if self.env_ctx.graph_coordinates.exec_mode == ExecMode.mode_start:
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return Bootstrapper_state_stride_py_required_reached_mode_start(self.env_ctx)
        else:
            return Bootstrapper_state_stride_py_required_reached_not_mode_start(self.env_ctx)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_reboot_triggered(AbstractCachingStateNode[bool]):
    """
    Removes current `venv` dir and `constraints.txt` file (to trigger their re-creation subsequently).
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_stride_py_required_reached.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_reboot_triggered.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_reboot_triggered`
            # is to destroy `venv` to recreate it later.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return False

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        reboot_env: bool = state_args_parsed.exec_mode == ExecMode.mode_reboot.value

        state_stride_py_required_reached: StateStride = self.eval_parent_state(EnvState.state_stride_py_required_reached.name)
        assert self.env_ctx.get_stride().value >= StateStride.stride_py_required.value
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)

        # Reboot can only happen outside `venv` (to delete it):
        if not (reboot_env and state_stride_py_required_reached == StateStride.stride_py_required):
            return False

        state_local_venv_dir_abs_path_inited = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)
        if os.path.exists(state_local_venv_dir_abs_path_inited):

            # Move old `venv` to temporary directory:

            state_local_tmp_dir_abs_path_inited = self.eval_parent_state(EnvState.state_local_tmp_dir_abs_path_inited.name)

            moved_venv_dir = os.path.join(
                state_local_tmp_dir_abs_path_inited,
                f"venv.before.{state_input_start_id_var_loaded}",
            )

            logger.info(f"moving `venv` dir from [{state_local_venv_dir_abs_path_inited}] to [{moved_venv_dir}]")

            shutil.move(
                state_local_venv_dir_abs_path_inited,
                moved_venv_dir,
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_local_conf_symlink_abs_path_inited = self.eval_parent_state(EnvState.state_local_conf_symlink_abs_path_inited.name)
        constraints_txt_path = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            ConfConstEnv.constraints_txt_basename,
        )
        if os.path.exists(constraints_txt_path):
            logger.info(f"removing version constraints file [{constraints_txt_path}]")
            os.remove(constraints_txt_path)

        return True


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_venv_driver_prepared(AbstractCachingStateNode[VenvDriverBase]):
    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_required_python_version_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_reboot_triggered.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_venv_driver_prepared.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_venv_driver_prepared`
            # is to prepare `VenvDriverBase` to create `venv`.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return VenvDriverBase()

        state_required_python_version_inited: str = self.eval_parent_state(EnvState.state_required_python_version_inited.name)

        state_selected_python_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_selected_python_file_abs_path_inited.name)

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        state_venv_driver_inited: VenvDriverType = self.eval_parent_state(EnvState.state_venv_driver_inited.name)

        state_local_cache_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_cache_dir_abs_path_inited.name)

        venv_driver: VenvDriverBase
        if VenvDriverType.venv_uv == state_venv_driver_inited:
            venv_driver = VenvDriverUv(
                required_python_version=state_required_python_version_inited,
                selected_python_file_abs_path=state_selected_python_file_abs_path_inited,
                state_local_venv_dir_abs_path_inited=state_local_venv_dir_abs_path_inited,
                state_local_cache_dir_abs_path_inited=state_local_cache_dir_abs_path_inited,
            )
        elif VenvDriverType.venv_pip == state_venv_driver_inited:
            # Nothing to do:
            # `VenvDriverType.venv_pip` is available by default with the new `venv` without installation.
            venv_driver = VenvDriverPip(
                required_python_version=state_required_python_version_inited,
                selected_python_file_abs_path=state_selected_python_file_abs_path_inited,
                state_local_venv_dir_abs_path_inited=state_local_venv_dir_abs_path_inited,
            )
        else:
            raise AssertionError(f"unsupported `{VenvDriverType.__name__}` [{state_venv_driver_inited.name}]")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return venv_driver


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_stride_py_venv_reached(AbstractCachingStateNode[StateStride]):
    """
    Creates `venv` and switches to `python` from there.
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_reboot_triggered.name,
            EnvState.state_venv_driver_prepared.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_py_venv_reached.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_stride_py_venv_reached: StateStride = StateStride.stride_py_venv

        if self.env_ctx.has_stride_reached(next_stride=state_stride_py_venv_reached):
            return self.env_ctx.set_max_stride(state_stride_py_venv_reached)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_stride_py_venv_reached`
            # is to create a `venv`.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return self.env_ctx.set_max_stride(state_stride_py_venv_reached)

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        state_reboot_triggered: bool = self.eval_parent_state(EnvState.state_reboot_triggered.name)

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_selected_python_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_selected_python_file_abs_path_inited.name)
        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        state_venv_driver_prepared: VenvDriverBase = self.eval_parent_state(EnvState.state_venv_driver_prepared.name)

        venv_path_to_python: str = os.path.join(
            state_local_venv_dir_abs_path_inited,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python: str = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        if is_sub_path(
            path_to_curr_python,
            state_local_venv_dir_abs_path_inited,
        ):
            raise AssertionError(f"Current `python` [{path_to_curr_python}] must be outside of the `venv` [{state_local_venv_dir_abs_path_inited}].")

        if os.environ.get(EnvVar.var_PROTOPRIMER_MOCKED_RESTART.value, None) is None:
            if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
                # Skip required `python` validation because we do not need it to create `venv`:
                pass
            else:
                if not is_same_file(
                    path_to_curr_python,
                    state_selected_python_file_abs_path_inited,
                ):
                    raise AssertionError(f"Current `python` [{path_to_curr_python}] must point to the same file as the selected one [{state_selected_python_file_abs_path_inited}].")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert self.env_ctx.get_stride().value <= StateStride.stride_py_required.value
        if not os.path.exists(state_local_venv_dir_abs_path_inited):
            if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
                # The `venv` is supposed to be ready in `ExecMode.mode_start`:
                raise AssertionError(f"`venv` [{state_local_venv_dir_abs_path_inited}] is supposed to be ready in `ExecMode` [{state_input_exec_mode_arg_loaded.name}] execute `ExecMode` [{ExecMode.mode_boot.name}] to prepare it.")
            else:
                state_venv_driver_prepared.create_venv(state_local_venv_dir_abs_path_inited)
        else:
            logger.info(f"reusing existing `venv` [{state_local_venv_dir_abs_path_inited}]")
            if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
                # Skip `venv` type validation:
                pass
            else:
                if not state_venv_driver_prepared.is_mine_venv(state_local_venv_dir_abs_path_inited):
                    raise AssertionError(f"`venv` [{state_local_venv_dir_abs_path_inited}] was not created by this driver [{state_venv_driver_prepared.get_type().name}] retry with [{ExecMode.mode_reboot.value}] sub-command.")

        return switch_python(
            curr_python_path=state_selected_python_file_abs_path_inited,
            next_py_exec=self.env_ctx.set_max_stride(state_stride_py_venv_reached),
            next_python_path=venv_path_to_python,
            start_id=state_input_start_id_var_loaded,
            proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_protoprimer_package_installed(AbstractCachingStateNode[bool]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_do_install_var_loaded.name,
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_project_descriptors_inited.name,
            EnvState.state_install_specs_inited.name,
            EnvState.state_venv_driver_prepared.name,
            EnvState.state_stride_py_venv_reached.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_protoprimer_package_installed.name)

    def _eval_state_once(self) -> ValueType:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_protoprimer_package_installed`
            # is to install dependencies into `venv`.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return False

        state_input_do_install_var_loaded: bool = self.eval_parent_state(EnvState.state_input_do_install_var_loaded.name)

        state_stride_py_venv_reached: StateStride = self.eval_parent_state(EnvState.state_stride_py_venv_reached.name)
        assert self.env_ctx.get_stride().value >= StateStride.stride_py_venv.value

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_ref_root_dir_abs_path_inited.name)

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_conf_symlink_abs_path_inited.name)

        state_project_descriptors_inited: list[dict] = self.eval_parent_state(EnvState.state_project_descriptors_inited.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_install_specs_inited: list[dict] = self.eval_parent_state(EnvState.state_install_specs_inited.name)

        state_venv_driver_prepared: VenvDriverBase = self.eval_parent_state(EnvState.state_venv_driver_prepared.name)

        reboot_env: bool = state_args_parsed.exec_mode == ExecMode.mode_reboot.value

        do_install: bool = (
            state_stride_py_venv_reached.value == StateStride.stride_py_venv.value
            and (reboot_env or state_input_do_install_var_loaded)
            #
        )

        if not do_install:
            return False

        constraints_txt_path = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            ConfConstEnv.constraints_txt_basename,
        )
        if not os.path.exists(constraints_txt_path):
            logger.info(f"creating empty constraints file [{constraints_txt_path}]")
            write_text_file(
                constraints_txt_path,
                "",
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        if len(state_project_descriptors_inited) == 0:
            logger.warning(f"{ValueName.value_project_descriptors.value} is empty - nothing to install")
            return True

        # Group `project_descriptor`-s into `install_group`-s:
        grouped_descriptors: dict[str | None, list[dict]] = {}
        for project_descriptor in state_project_descriptors_inited:
            install_group: str | None = project_descriptor.get(ConfField.field_install_group.value, None)
            if install_group not in grouped_descriptors:
                grouped_descriptors[install_group] = []
            grouped_descriptors[install_group].append(project_descriptor)

        # Determine `install_group` order and collect extra args:
        group_to_extra_args: dict[str | None, list[str]] = {}
        ordered_install_groups: list[str | None] = []
        for install_spec_item in state_install_specs_inited:

            # The `install_specs` is a list of singleton dict-s:
            # (where each key is one of the `install_group`-s)
            if not isinstance(install_spec_item, dict) or len(install_spec_item) != 1:
                raise AssertionError(
                    f"invalid item in `{ConfField.field_install_specs.value}` "
                    f"(must be a single-item `dict`): "
                    f"[{install_spec_item}]"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
                )

            install_group_name = list(install_spec_item.keys())[0]
            install_spec_obj = install_spec_item[install_group_name]

            if not isinstance(install_spec_obj, dict):
                raise AssertionError(
                    f"invalid value of `{install_group_name}` "
                    f"in `{ConfField.field_install_specs.value}` (must be a `dict`): "
                    f"[{install_spec_obj}]"
                    #
                )

            extra_command_args: list[str] = install_spec_obj.get(ConfField.field_extra_command_args.value, [])

            if install_group_name in grouped_descriptors:
                ordered_install_groups.append(install_group_name)
                group_to_extra_args[install_group_name] = extra_command_args
            else:
                logger.warning(
                    f"`{install_group_name}` from `{ConfField.field_install_specs.value}` "
                    f"is not found in `{ConfField.field_project_descriptors.value}`"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
                )

        # Add `install_group`-s not listed in `install_specs`:
        for install_group in grouped_descriptors.keys():
            if install_group not in ordered_install_groups:
                ordered_install_groups.append(install_group)
                group_to_extra_args[install_group] = []

        # Install groups one by one:
        for install_group in ordered_install_groups:
            group_descriptors = grouped_descriptors[install_group]
            logger.info(f"installing group: [{install_group}]")

            state_venv_driver_prepared.install_dependencies(
                state_ref_root_dir_abs_path_inited,
                get_path_to_curr_python(),
                constraints_txt_path,
                group_descriptors,
                group_to_extra_args[install_group],
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return True


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_version_constraints_generated(AbstractCachingStateNode[bool]):
    """
    Implements UC_44_82_07_30.requirements_lock.md.
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_venv_driver_prepared.name,
            EnvState.state_protoprimer_package_installed.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_version_constraints_generated.name)

    def _eval_state_once(self) -> ValueType:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_version_constraints_generated`
            # is to re-generate the `constraints.txt` file based on `venv`.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return False

        state_protoprimer_package_installed: bool = self.eval_parent_state(EnvState.state_protoprimer_package_installed.name)

        if not state_protoprimer_package_installed:
            return False

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_conf_symlink_abs_path_inited.name)

        state_venv_driver_prepared: VenvDriverBase = self.eval_parent_state(EnvState.state_venv_driver_prepared.name)

        state_venv_driver_prepared.pin_versions(
            get_path_to_curr_python(),
            os.path.join(
                state_local_conf_symlink_abs_path_inited,
                ConfConstEnv.constraints_txt_basename,
            ),
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        return True


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_stride_deps_updated_reached(AbstractCachingStateNode[StateStride]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_version_constraints_generated.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_deps_updated_reached.name)

    def _eval_state_once(self) -> ValueType:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_stride_deps_updated_reached: StateStride = StateStride.stride_deps_updated

        if self.env_ctx.has_stride_reached(next_stride=state_stride_deps_updated_reached):
            return self.env_ctx.set_max_stride(state_stride_deps_updated_reached)

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_stride_deps_updated_reached`
            # is to make `venv` dependencies effective.
            # Skip it as `venv` is supposed to be ready in `ExecMode.mode_start`:
            return self.env_ctx.set_max_stride(state_stride_deps_updated_reached)

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)

        state_version_constraints_generated: bool = self.eval_parent_state(EnvState.state_version_constraints_generated.name)

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        venv_path_to_python: str = os.path.join(
            state_local_venv_dir_abs_path_inited,
            ConfConstGeneral.file_rel_path_venv_python,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        return switch_python(
            curr_python_path=venv_path_to_python,
            next_py_exec=self.env_ctx.set_max_stride(state_stride_deps_updated_reached),
            next_python_path=venv_path_to_python,
            start_id=state_input_start_id_var_loaded,
            proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
        )


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_proto_code_updated(AbstractCachingStateNode[bool]):
    """
    Return `True` if content of the `proto_kernel` has changed.

    TODO: UC_52_87_82_92.conditional_auto_update.md
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_stride_deps_updated_reached.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_proto_code_updated.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def _eval_state_once(self) -> ValueType:

        state_stride_deps_updated_reached: StateStride = self.eval_parent_state(EnvState.state_stride_deps_updated_reached.name)
        assert self.env_ctx.get_stride().value >= StateStride.stride_deps_updated.value

        if self.env_ctx.get_stride().value != StateStride.stride_deps_updated.value:
            # Update only after package installation, otherwise, nothing to do:
            return False

        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if state_input_exec_mode_arg_loaded == ExecMode.mode_start:
            # The only reason for `EnvState.state_proto_code_updated`
            # is to update sources, but that has to be done in `ExecMode.mode_boot`.
            # Skip:
            return False

        state_proto_code_file_abs_path_inited = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)
        assert os.path.isabs(state_proto_code_file_abs_path_inited)
        assert not os.path.islink(state_proto_code_file_abs_path_inited)
        assert os.path.isfile(state_proto_code_file_abs_path_inited)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        assert is_venv()
        try:
            import protoprimer
        except ImportError:
            logger.warning(
                f"Module `{ConfConstGeneral.name_protoprimer_package}` is missing in `venv`. "
                f"{get_import_error_hint(ConfConstGeneral.name_protoprimer_package)} "
                #
            )
            # These must be "instant" conditions.
            # No module => no update:
            return False

        # Use generator from an immutable (source) `primer_kernel`
        # instead of the current local (target) `proto_code` module to avoid:
        # generated code inside generated code inside generated code ...
        generated_content_single_header: str = protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(protoprimer.primer_kernel)
        generated_content_multiple_body: str = protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(protoprimer.primer_kernel)

        # Use `primer_kernel` from installed package as the source for `proto_code` update:
        primer_kernel_abs_path = os.path.abspath(str(protoprimer.primer_kernel.__file__))
        primer_kernel_text: str = read_text_file(primer_kernel_abs_path)
        proto_code_text_old: str = read_text_file(state_proto_code_file_abs_path_inited)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # Update body:
        proto_code_text_with_body = _replace_multiple_body_in_empty_lines(
            input_text=primer_kernel_text,
            boilerplate_text=generated_content_multiple_body,
            min_lines_between=ConfConstGeneral.min_lines_between_generated_boilerplate,
        )

        # Update header:
        proto_code_text_new = _replace_single_header_in_empty_lines(
            input_text=proto_code_text_with_body,
            boilerplate_text=generated_content_single_header,
        )

        logger.debug(f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_proto_code_file_abs_path_inited` [{state_proto_code_file_abs_path_inited}]")
        write_text_file(
            file_path=state_proto_code_file_abs_path_inited,
            file_data=proto_code_text_new,
        )

        is_updated: bool = proto_code_text_old != proto_code_text_new
        return is_updated
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_stride_src_updated_reached(AbstractCachingStateNode[StateStride]):

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_args_parsed.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_start_id_var_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_proto_code_updated.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_stride_src_updated_reached.name)

    def _eval_state_once(self) -> ValueType:

        state_stride_src_updated_reached: StateStride = StateStride.stride_src_updated
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_input_exec_mode_arg_loaded: ExecMode = self.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

        if self.env_ctx.has_stride_reached(next_stride=state_stride_src_updated_reached):
            return self.env_ctx.set_max_stride(state_stride_src_updated_reached)

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)

        state_proto_code_updated: bool = self.eval_parent_state(EnvState.state_proto_code_updated.name)

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        venv_path_to_python: str = os.path.join(
            state_local_venv_dir_abs_path_inited,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        state_input_start_id_var_loaded: str = self.eval_parent_state(EnvState.state_input_start_id_var_loaded.name)

        return switch_python(
            curr_python_path=venv_path_to_python,
            next_py_exec=self.env_ctx.set_max_stride(state_stride_src_updated_reached),
            next_python_path=venv_path_to_python,
            start_id=state_input_start_id_var_loaded,
            proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_command_executed(AbstractCachingStateNode[int]):
    """
    If `ParsedArg.name_command`, this state replaces the current process with a shell executing the given command.
    """

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_default_stderr_log_handler_configured.name,
            EnvState.state_args_parsed.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_stride_src_updated_reached.name,
        ]
    )
    _state_name = staticmethod(lambda: EnvState.state_command_executed.name)

    def _eval_state_once(self) -> ValueType:
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        state_default_stderr_log_handler_configured: logging.Handler = self.eval_parent_state(EnvState.state_default_stderr_log_handler_configured.name)

        assert self.env_ctx.get_stride().value >= StateStride.stride_src_updated.value

        state_args_parsed: argparse.Namespace = self.eval_parent_state(EnvState.state_args_parsed.name)

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_venv_dir_abs_path_inited.name)

        state_local_cache_dir_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_cache_dir_abs_path_inited.name)

        command_line: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_command.value,
            None,
        )

        shell_driver: ShellDriverBase = _get_shell_driver(state_local_cache_dir_abs_path_inited)

        return shell_driver.run_shell(
            False,
            command_line,
            state_default_stderr_log_handler_configured,
            state_local_venv_dir_abs_path_inited,
        )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

########################################################################################################################


class EnvState(enum.Enum):
    """
    Environment states to be reached during the bootstrap process.

    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).
    The value of `AbstractCachingStateNode` assigned is the default implementation for the state,
    and the only reason it is assigned is purely for the quick navigation across the source code in the IDE.

    FT_68_54_41_96.state_dependency.md

    TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
          Currently, this enum class maps "state name" -> "impl class" directly.
          In the future, it may change to "state name" -> "impl factory" instead.
    """

    state_input_py_exec_var_loaded = Bootstrapper_state_input_py_exec_var_loaded
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    state_input_stderr_log_level_var_loaded = Bootstrapper_state_input_stderr_log_level_var_loaded

    state_input_do_install_var_loaded = Bootstrapper_state_input_do_install_var_loaded

    state_default_stderr_log_handler_configured = Bootstrapper_state_default_stderr_log_handler_configured

    state_args_parsed = Bootstrapper_state_args_parsed

    state_input_stderr_log_level_eval_finalized = Bootstrapper_state_input_stderr_log_level_eval_finalized

    state_input_exec_mode_arg_loaded = Bootstrapper_state_input_exec_mode_arg_loaded

    state_input_final_state_eval_finalized = Bootstrapper_state_input_final_state_eval_finalized

    # Special case: triggers everything:
    state_exec_mode_executed = Bootstrapper_state_exec_mode_executed

    state_input_start_id_var_loaded = Bootstrapper_state_input_start_id_var_loaded

    state_input_proto_code_file_abs_path_var_loaded = Bootstrapper_state_input_proto_code_file_abs_path_var_loaded
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # restart: `StateStride.stride_py_unknown` -> `StateStride.stride_py_arbitrary`:
    state_stride_py_arbitrary_reached = Bootstrapper_state_stride_py_arbitrary_reached

    state_proto_code_file_abs_path_inited = Bootstrapper_state_proto_code_file_abs_path_inited

    state_primer_conf_file_abs_path_inited = Bootstrapper_state_primer_conf_file_abs_path_inited

    # `ConfLeap.leap_primer`:
    state_primer_conf_file_data_loaded = Bootstrapper_state_primer_conf_file_data_loaded

    state_ref_root_dir_abs_path_inited = Bootstrapper_state_ref_root_dir_abs_path_inited

    state_global_conf_dir_abs_path_inited = Bootstrapper_state_global_conf_dir_abs_path_inited

    state_global_conf_file_abs_path_inited = Bootstrapper_state_global_conf_file_abs_path_inited

    # `ConfLeap.leap_client`:
    state_client_conf_file_data_loaded = Bootstrapper_state_client_conf_file_data_loaded

    state_selected_env_dir_rel_path_inited = Bootstrapper_state_selected_env_dir_rel_path_inited
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    state_local_conf_symlink_abs_path_inited = Bootstrapper_state_local_conf_symlink_abs_path_inited

    state_local_conf_file_abs_path_inited = Bootstrapper_state_local_conf_file_abs_path_inited

    # `ConfLeap.leap_env`:
    state_env_conf_file_data_loaded = Bootstrapper_state_env_conf_file_data_loaded

    state_required_python_version_inited = Bootstrapper_required_python_version_inited

    # TODO: TODO_41_10_50_01.implement_env_selector.md: What is the FT (feature_topic)?
    state_python_selector_file_abs_path_inited = Bootstrapper_state_python_selector_file_abs_path_inited

    state_selected_python_file_abs_path_inited = Bootstrapper_state_selected_python_file_abs_path_inited

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_venv_dir_abs_path_inited = Bootstrapper_state_local_venv_dir_abs_path_inited

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_log_dir_abs_path_inited = Bootstrapper_state_local_log_dir_abs_path_inited

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_tmp_dir_abs_path_inited = Bootstrapper_state_local_tmp_dir_abs_path_inited
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_cache_dir_abs_path_inited = Bootstrapper_state_local_cache_dir_abs_path_inited

    state_venv_driver_inited = Bootstrapper_state_venv_driver_inited

    state_project_descriptors_inited = Bootstrapper_state_project_descriptors_inited

    state_install_specs_inited = Bootstrapper_state_install_specs_inited

    # `ConfLeap.leap_derived`:
    state_derived_conf_data_loaded = Bootstrapper_state_derived_conf_data_loaded

    state_effective_conf_data_printed = Bootstrapper_state_effective_conf_data_printed

    state_default_file_log_handler_configured = Bootstrapper_state_default_file_log_handler_configured

    # restart: `StateStride.stride_py_arbitrary` -> `StateStride.stride_py_required`:
    state_stride_py_required_reached = Factory_state_stride_py_required_reached

    state_reboot_triggered = Bootstrapper_state_reboot_triggered
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    state_venv_driver_prepared = Bootstrapper_state_venv_driver_prepared

    # restart: `StateStride.stride_py_required` -> `StateStride.stride_py_venv`:
    state_stride_py_venv_reached = Bootstrapper_state_stride_py_venv_reached

    # TODO: rename to "client" (or "ref"?): `client_project_descriptors_installed`:
    state_protoprimer_package_installed = Bootstrapper_state_protoprimer_package_installed

    state_version_constraints_generated = Bootstrapper_state_version_constraints_generated

    # restart: `StateStride.stride_py_venv` -> `StateStride.stride_deps_updated`:
    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_stride_deps_updated_reached = Bootstrapper_state_stride_deps_updated_reached

    # TODO: rename according to the final name:
    state_proto_code_updated = Bootstrapper_state_proto_code_updated

    # restart: `StateStride.stride_deps_updated` -> `StateStride.stride_src_updated`:
    state_stride_src_updated_reached = Bootstrapper_state_stride_src_updated_reached

    state_command_executed = Bootstrapper_state_command_executed
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class TargetState(enum.Enum):
    """
    Special `EnvState`-s.
    """

    # Used for `EnvState.state_status_line_printed` to report exit code:
    target_stderr_log_handler = EnvState.state_default_stderr_log_handler_configured

    # A special state that triggers execution in the specific `ExecMode`:
    target_exec_mode_executed = EnvState.state_exec_mode_executed

    # TODO: This should be `state_derived_conf_data_loaded`:
    # When all config files loaded:
    target_config_loaded = EnvState.state_venv_driver_inited

    # The final state before switching to `PrimerRuntime.runtime_neo`:
    target_proto_bootstrap_completed = EnvState.state_command_executed


class StateGraph:
    """
    It is a graph, which must be a DAG.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def __init__(self):
        self.state_nodes: dict[str, StateNode] = {}
        self.state_factories: dict[str, NodeFactory] = {}

    def register_factory(
        self,
        state_name: str,
        state_factory: NodeFactory,
        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
        #       This use_case may become obsolete if we use "state name" -> "impl factory" naming
        #       where the factory cannot be replaced (currently, it is "state name" -> "impl class" directly).
        replace_existing: bool = False,
    ) -> NodeFactory | None:
        if state_name in self.state_factories:
            if replace_existing:
                # See: UC_27_40_17_59.replace_by_new_and_use_old.md:
                existing_factory = self.state_factories[state_name]
                self.state_factories[state_name] = state_factory
                return existing_factory
            else:
                raise AssertionError(f"[{NodeFactory.__name__}] for [{state_name}] is already registered.")
        else:
            self.state_factories[state_name] = state_factory
            return None
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_state_factory(
        self,
        state_name: str,
    ) -> NodeFactory:
        return self.state_factories[state_name]

    def get_state_node(
        self,
        state_name: str,
    ) -> StateNode:
        if state_name not in self.state_nodes:
            self.state_nodes[state_name] = self.state_factories[state_name].create_state_node()
            logger.debug(f"instantiated `state_node` class [{self.state_nodes[state_name].__class__}] for `state_name` [{state_name}]")
        return self.state_nodes[state_name]

    def eval_state(
        self,
        state_name: str,
    ) -> Any:
        try:
            state_node = self.get_state_node(state_name)
        except KeyError:
            logger.error(f"`state_name` [{state_name}] is not registered.")
            raise
        return state_node.eval_own_state()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class MutableValue(Generic[ValueType]):
    """
    A mutable value which must be evaluated (initialized) via one of the `StateNode`-s before it can be used.

    This class provides an N-to-1 mechanism where N x `StateNode`-s update 1 x named `MutableValue`.

    Immutable values produced by `StateNode`-s cannot be changed -
    once evaluated, these values stay the same.
    Unlike `StateNode` values, `MutableValue` can evolve.

    NOTE: The issue with `MutableValue`-s is that the order of reading/writing them is important.
    To avoid defects, always read them last (after evaluation of all parent `StateNode` states).
    It is not required to bootstrap to the latest `StateNode` updating the given `MutableValue`
    because some of these `StateNode`-s may not be (transitive) parents.
    But, if the current `StateNode` depends on parents updating that `MutableValue`,
    read it after evaluation of all parent states.

    TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
          Why not simply rely on `EnvContext` to maintain current mutable state.
          It already does it with `StateStride`.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def __init__(
        self,
        state_name: str,
    ):
        # TODO: It should not be called state_name and should be disassociated from states in DAG.
        #       It should be modeled as a value which is changed by multiple states
        #       and (depending on the current state in DAG) should be accessed after those states on
        #       the path to the current one have already been evaluated.
        self.state_name = state_name
        self.curr_value: ValueType | None = None

    def get_curr_value(
        self,
        state_node: StateNode,
    ) -> ValueType:

        # This ensures that the `StateNode` using that `MutableValue`
        # declares `state_name` as a dependency:
        init_value = state_node.eval_parent_state(self.state_name)

        if self.curr_value is None:
            self.curr_value = init_value
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        logger.debug(f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after get [{self.curr_value}] in [{state_node.get_state_name()}]")
        return self.curr_value

    def set_curr_value(
        self,
        state_node: StateNode | None,
        curr_value: ValueType,
    ) -> None:
        # TODO: Shell we also ensure that the `StateNode` using that `MutableValue` has necessary dependencies on write?

        if self.curr_value is None:
            raise AssertionError(f"`{MutableValue.__name__}` [{self.state_name}] cannot be set as it is not initialized yet.")
        state_name: str | None = None
        self.curr_value = curr_value
        logger.debug(f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after set [{self.curr_value}] in [{state_node.get_state_name()}]")


class EnvContext:

    def __init__(self):
        self.graph_coordinates = GraphCoordinates()
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        self.state_graph: StateGraph = StateGraph()

        self.state_stride: StateStride = StateStride.stride_py_unknown

        # TODO: TODO_60_63_68_81.refactor_DAG_builder.md: should it even be here?
        # TODO: Do not set it on `EnvContext` - use bootstrap-able values:
        self.final_state: str = TargetState.target_proto_bootstrap_completed.value.name

        self._register_graph_node_factories()

    def _register_graph_node_factories(self):
        """
        Registers all defined `EnvState`-s.
        """
        for env_state in EnvState:
            # This `self` in `env_state.value(self)` is required
            # because some `StateNode`-s use `EnvContext` in its `ctor`:
            # noinspection PyArgumentList
            self.state_graph.register_factory(
                env_state.name,
                env_state.value(self),
            )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def get_stride(self) -> StateStride:
        return self.state_stride

    def set_max_stride(
        self,
        next_stride: StateStride,
    ) -> StateStride:
        if not self.has_stride_reached(next_stride):
            self.state_stride = next_stride
        log_stride.set(self.state_stride)
        return self.state_stride

    def has_stride_reached(
        self,
        next_stride: StateStride,
    ) -> bool:
        """
        `StateStride.value` is monotonically increasing.
        At most one call to `switch_python` is required at each value.
        """
        return self.get_stride().value >= next_stride.value
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def print_exit_line(
        self,
        exit_code: int,
        test_failure: bool = False,
    ) -> None:
        """
        Print a color-coded status message to stderr.
        """
        if type(exit_code) is not int:
            raise AssertionError("`exit_code` must be an `int`")

        state_default_stderr_log_handler_configured: logging.Handler = self.state_graph.eval_state(EnvState.state_default_stderr_log_handler_configured.name)

        status_name: str
        is_reportable: bool
        if exit_code == 0:
            color_status = f"{TermColor.back_dark_green.value}{TermColor.fore_dark_black.value}"
            status_name = "SUCCESS"
            is_reportable = state_default_stderr_log_handler_configured.level <= logging.INFO
        else:
            if not test_failure and is_test_run():
                # Avoid confusing output with "FAILURE" in tests:
                status_name = "TEST_EXIT"
                color_status = f"{TermColor.back_dark_yellow.value}{TermColor.fore_dark_black.value}"
            else:
                status_name = "FAILURE"
                color_status = f"{TermColor.back_dark_red.value}{TermColor.fore_bright_white.value}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            is_reportable = state_default_stderr_log_handler_configured.level <= logging.CRITICAL

        if is_reportable:
            print(
                f"{color_status}{status_name}{TermColor.reset_style.value} [{exit_code}]: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )


class StateStrideFilter(logging.Filter):
    """
    This filter sets `StateStride` values for each log entry without filtering any record.
    """

    def filter(
        self,
        record,
    ):
        record.py_exec_name = StateStride[
            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]
        record.state_stride = log_stride.get(StateStride.stride_py_unknown)
        # Do not filter:
        return True
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class UtcTimeFormatter(logging.Formatter):
    """
    Custom formatter with the proper timestamp.
    """

    def __init__(
        self,
        print_date: bool,
        print_time: bool,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.print_date = print_date
        self.print_time = print_time

    def formatTime(
        self,
        record,
        datefmt=None,
    ):
        if not self.print_date and not self.print_time:
            return ""
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        log_timestamp = datetime.datetime.fromtimestamp(
            record.created,
            datetime.timezone.utc,
        )
        iso_str = log_timestamp.isoformat(timespec="milliseconds").replace(
            "+00:00",
            "Z",
        )

        if self.print_date and self.print_time:
            return iso_str

        date_part, time_part = iso_str.split("T")

        if self.print_date:
            return date_part
        else:
            return time_part


class DefaultFileLogFormatter(UtcTimeFormatter):
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def __init__(
        self,
        fmt: str = "%(asctime)s pid:%(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s",
    ):
        super().__init__(
            print_date=True,
            print_time=True,
            fmt=fmt,
        )


class _PrimerFileLogFormatter(DefaultFileLogFormatter):

    def __init__(self):
        # noinspection SpellCheckingInspection
        super().__init__(
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s s:%(state_stride)s %(filename)s:%(lineno)d %(message)s",
        )


class DefaultStderrLogFormatter(UtcTimeFormatter):
    """
    Custom formatter with color and format based on log level for stderr.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    color_reset = TermColor.reset_style.value
    color_set = {
        "CRITICAL": TermColor.fore_bold_dark_red.value,
        "ERROR": TermColor.fore_dark_red.value,
        # The default is "WARNING" - see: FT_38_73_38_52.log_verbosity.md
        "WARNING": TermColor.fore_dark_yellow.value,
        "INFO": TermColor.fore_dark_green.value,
        "DEBUG": TermColor.fore_dark_cyan.value,
        # TODO: Is this true?
        # NOTE: Level `logging.NOTSET` (below `logging.DEBUG`) is not printed.
        #       And numerical levels like 5 have no given names (making `logging.DEBUG` practically the lowest).
    }

    def __init__(
        self,
        verbosity_level: int,
    ):
        super().__init__(
            # Default: least verbose:
            print_date=False,
            print_time=False,
            fmt="%(levelname)s %(message)s",
        )
        info_formatter = UtcTimeFormatter(
            print_date=False,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s %(message)s",
        )
        debug_formatter = UtcTimeFormatter(
            print_date=True,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s",
        )
        self.verbose_formatters = {
            # Anything above `logging.INFO` use default (least verbose):
            logging.INFO: info_formatter,
            # Most verbose:
            logging.DEBUG: debug_formatter,
            logging.NOTSET: debug_formatter,
        }
        self.verbosity_level = verbosity_level
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    def set_verbosity_level(
        self,
        verbosity_level: int,
    ):
        self.verbosity_level = verbosity_level

    def format(
        self,
        record,
    ):
        # Format the output:
        log_formatter = self.verbose_formatters.get(self.verbosity_level, None)
        if log_formatter is None:
            log_msg = super().format(record)
        else:
            log_msg = log_formatter.format(record)

        # Color the output:
        log_color = self.color_set.get(record.levelname, self.color_reset)
        return f"{log_color}{log_msg}{self.color_reset}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class _PrimerStderrLogFormatter(DefaultStderrLogFormatter):

    def __init__(
        self,
        verbosity_level: int,
    ):
        super().__init__(verbosity_level)
        info_formatter = UtcTimeFormatter(
            print_date=False,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s s:%(state_stride)s %(message)s",
        )
        debug_formatter = UtcTimeFormatter(
            print_date=True,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s s:%(state_stride)s %(filename)s:%(lineno)d %(message)s",
        )
        self.verbose_formatters = {
            logging.INFO: info_formatter,
            logging.DEBUG: debug_formatter,
            logging.NOTSET: debug_formatter,
        }
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def reconfigure_stderr_log_handler(log_level: int = logging.WARNING) -> logging.Handler | None:
    """
    UC_81_50_97_17.reuse_logger.md
    """

    logger.setLevel(logging.NOTSET)

    # Check for existing primer handler (to replace its formatter):
    stderr_handler: logging.Handler
    for stderr_handler in logger.handlers:
        if isinstance(stderr_handler, logging.StreamHandler) and stderr_handler.stream is sys.stderr and isinstance(stderr_handler.formatter, DefaultStderrLogFormatter):
            # This covers both `_PrimerStderrLogFormatter` (subclass) and `DefaultStderrLogFormatter`.
            stderr_handler.setFormatter(DefaultStderrLogFormatter(log_level))
            stderr_handler.setLevel(log_level)

            # Remove primer-specific filter if present:
            for f in list(stderr_handler.filters):
                if isinstance(f, StateStrideFilter):
                    stderr_handler.removeFilter(f)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            return stderr_handler

    return None


def configure_default_stderr_log_handler(log_level: int = logging.WARNING) -> logging.Handler:
    logger.setLevel(logging.NOTSET)
    stderr_handler: logging.Handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(DefaultStderrLogFormatter(log_level))
    stderr_handler.setLevel(log_level)
    logger.addHandler(stderr_handler)
    return stderr_handler


def _configure_primer_stderr_log_handler(state_input_stderr_log_level_var_loaded: int) -> logging.Handler:
    """
    Implements for `stderr` log: FT_38_73_38_52.log_verbosity.md
    """

    # Log everything (the filters are supposed to be set on output handlers instead):
    logger.setLevel(logging.NOTSET)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    handler_class = logging.StreamHandler
    stderr_handler: logging.Handler | None = None
    if os.environ.get(EnvVar.var_PROTOPRIMER_MOCKED_RESTART.value, None) is not None:
        # Prevent duplicate handler (when `os.execv*` calls restart `main` again in tests).
        # Select `stderr` handler:
        for handler_instance in logger.handlers:
            if isinstance(handler_instance, handler_class):
                if handler_instance.stream is sys.stderr:
                    stderr_handler = handler_instance
                    break

    if stderr_handler is None:
        stderr_handler: logging.Handler = handler_class(sys.stderr)

        stderr_handler.addFilter(StateStrideFilter())
        stderr_handler.setFormatter(_PrimerStderrLogFormatter(state_input_stderr_log_level_var_loaded))

        logger.addHandler(stderr_handler)

    stderr_handler.setLevel(state_input_stderr_log_level_var_loaded)
    return stderr_handler
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def reconfigure_file_log_handler(log_level: int = logging.INFO) -> logging.Handler | None:
    """
    UC_81_50_97_17.reuse_logger.md
    """

    # Check for existing `_Primer*` handler (to replace its formatter):
    file_handler: logging.Handler
    for file_handler in logger.handlers:
        if isinstance(file_handler, logging.FileHandler) and isinstance(file_handler.formatter, DefaultFileLogFormatter):
            # This covers both `_PrimerFileLogFormatter` (subclass) and `DefaultFileLogFormatter`.
            file_handler.setFormatter(DefaultFileLogFormatter())
            file_handler.setLevel(log_level)

            # Remove primer-specific filter if present:
            for handler_filter in list(file_handler.filters):
                if isinstance(handler_filter, StateStrideFilter):
                    file_handler.removeFilter(handler_filter)

            return file_handler
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    return None


def configure_default_file_log_handler(
    log_file_abs_path: str,
    log_level: int = logging.INFO,
) -> logging.Handler:
    os.makedirs(os.path.dirname(log_file_abs_path), exist_ok=True)
    file_handler: logging.Handler = logging.FileHandler(log_file_abs_path)
    file_handler.setFormatter(DefaultFileLogFormatter())
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    return file_handler


def _configure_primer_file_log_handler(
    script_name: str,
    state_input_start_id_var_loaded: str,
    state_input_stderr_log_level_eval_finalized: int,
    state_local_log_dir_abs_path_inited: str,
) -> logging.Handler:
    """
    Implements for log file: FT_38_73_38_52.log_verbosity.md
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    log_file_basename = f"{script_name}.{state_input_start_id_var_loaded}.log"
    log_file_abs_path = os.path.join(
        state_local_log_dir_abs_path_inited,
        log_file_basename,
    )

    # TODO: Configure MAX file log level in the config file (NOTE: the higher the level the fewer the log entries):
    file_log_level: int = logging.INFO
    # Increase the log level at most to what is used by stderr:
    if state_input_stderr_log_level_eval_finalized < file_log_level:
        file_log_level = state_input_stderr_log_level_eval_finalized

    os.makedirs(
        state_local_log_dir_abs_path_inited,
        exist_ok=True,
    )

    if not os.path.exists(log_file_abs_path):
        # Explain missing logs to avoid confusion:
        write_text_file(
            log_file_abs_path,
            f"""
{ConfConstGeneral.log_section_delimiter} file log starts at [{StateStride.stride_py_arbitrary.name}] after its config is resolved {ConfConstGeneral.log_section_delimiter}
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
""",
        )

    file_handler: logging.Handler = logging.FileHandler(log_file_abs_path)
    file_handler.addFilter(StateStrideFilter())

    file_formatter = _PrimerFileLogFormatter()

    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    return file_handler


def rename_to_moved_state_name(state_name: str) -> str:
    """
    See UC_27_40_17_59.replace_by_new_and_use_old.md
    """
    return f"_{state_name}"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def missing_conf_file_message(file_abs_path: str) -> str:
    return f"File [{file_abs_path}] does not exist - use [{ExecMode.mode_eval.value}] sub-command for description."


def warn_once_at_state_stride(
    log_message,
    state_stride: StateStride,
) -> None:
    if state_stride == StateStride.stride_py_arbitrary:
        logger.warning(log_message)


def can_print_effective_config(state_node: StateNode) -> bool:
    """
    See: FT_19_44_42_19.effective_config.md
    """

    state_input_exec_mode_arg_loaded: ExecMode = state_node.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)

    return (
        state_node.env_ctx.get_stride().value
        # `StateStride.stride_py_arbitrary` ensures that the path to `proto_code` is outside `venv`:
        == StateStride.stride_py_arbitrary.value
        and state_input_exec_mode_arg_loaded == ExecMode.mode_eval
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def find_python_version_file(curr_dir_any_path=".") -> str | None:
    """
    Walks up the directory tree to find the path to a `.python-version` file.
    """

    # Use abs path to ensure we can reach the root:
    curr_dir_abs_path: str = os.path.abspath(curr_dir_any_path)

    while True:
        file_abs_path = os.path.join(
            curr_dir_abs_path,
            ConfConstGeneral.python_version_file_basename,
        )

        if os.path.isfile(file_abs_path):
            return file_abs_path

        # Walk up one level:
        parent_dir_abs_path = os.path.dirname(curr_dir_abs_path)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # If the walk did not work, we hit the root:
        if parent_dir_abs_path == curr_dir_abs_path:
            break

        curr_dir_abs_path = parent_dir_abs_path

    return None


def switch_python(
    curr_python_path: str,
    next_py_exec: StateStride,
    next_python_path: str,
    start_id: str,
    proto_code_abs_file_path: str | None,
    required_environ: dict | None = None,
) -> StateStride:
    """
    It always "returns" `next_py_exec` (or fails).
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    curr_py_exec: StateStride = StateStride[
        os.getenv(
            EnvVar.var_PROTOPRIMER_PY_EXEC.value,
            ConfConstInput.default_PROTOPRIMER_PY_EXEC,
        )
    ]

    # TODO: Do not add args if they have been parsed and already have the same value:
    exec_argv: list[str] = [
        next_python_path,
        # FT_28_25_63_06.isolated_python.md:
        # This CLI arg is not added to `sys.argv` of the next `python` process
        # (instead, it simply sets `sys.flags.isolated`):
        "-I",
    ]
    exec_argv.extend(sys.argv)

    if required_environ is None:
        required_environ = os.environ.copy()
    assert isinstance(required_environ, dict)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    required_environ[EnvVar.var_PROTOPRIMER_PY_EXEC.value] = next_py_exec.name
    required_environ[EnvVar.var_PROTOPRIMER_START_ID.value] = start_id
    if proto_code_abs_file_path is not None:
        required_environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = proto_code_abs_file_path

    logger.info(f"switching from current `python` executable [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}`[{proto_code_abs_file_path}] exec_argv: {exec_argv}" "\n" "\n" f"{ConfConstGeneral.log_section_delimiter} before: [{curr_py_exec.name}] <<< restart >>> after: [{next_py_exec.name}] {ConfConstGeneral.log_section_delimiter}" "\n")

    os.execve(
        path=next_python_path,
        argv=exec_argv,
        env=required_environ,
    )

    # When `os.execve` is mocked:
    # noinspection PyUnreachableCode
    return next_py_exec


def skip_python(
    log_message: str,
    curr_py_exec: StateStride,
    next_py_exec: StateStride,
) -> StateStride:
    logger.info(f"{log_message}: skip `python` executable switch from [{curr_py_exec.name}] to [{next_py_exec.name}]")
    return next_py_exec
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def print_delegate_line(
    arg_list: list[str],
    stderr_log_handler: logging.Handler,
) -> None:

    color_delegate = f"{TermColor.back_dark_blue.value}{TermColor.fore_bright_white.value}"
    color_reset = TermColor.reset_style.value

    is_reportable: bool = stderr_log_handler.level <= logging.INFO
    if is_reportable:
        command_line = get_shell_command_line(arg_list)
        print(
            f"{color_delegate}DELEGATE{color_reset}: {command_line}",
            file=sys.stderr,
            flush=True,
        )


def get_file_name_timestamp():
    """
    Generate a timestamp acceptable to be embedded into a filename.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    file_timestamp = now_utc.strftime("%Y%m%dT%H%M%S") + "Z"
    return file_timestamp


def get_default_start_id():
    return f"{get_file_name_timestamp()}.{os.getpid()}"


def is_sub_path(
    abs_sub_path: str,
    abs_base_base: str,
) -> bool:
    try:
        rel_path(
            abs_sub_path,
            abs_base_base,
        )
        return True
    except ValueError:
        return False
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def rel_path(
    target_any_path: str,
    source_any_path: str,
) -> str:
    """
    `PurePath` compares `str` paths (without looking at the filesystem or resolving symlinks).
    """
    return str(pathlib.PurePath(target_any_path).relative_to(pathlib.PurePath(source_any_path)))


def is_same_file(
    l_abs_path: str,
    r_abs_path: str,
) -> bool:
    return pathlib.Path(l_abs_path).samefile(pathlib.Path(r_abs_path))


def get_path_to_curr_python() -> str:
    return sys.executable
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def get_path_to_base_python() -> str:

    executable_basename: str = os.path.basename(sys.executable)

    # Try current `executable_basename` first.
    # In some cases (e.g. on `macOS` with `homebrew`),
    # there are no simple basenames like `python`, instead, there are versioned ones like `python3.10`:
    path_to_next_python: str = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_bin,
        executable_basename,
    )
    if os.path.exists(path_to_next_python):
        return path_to_next_python

    path_to_next_python = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_python,
    )
    return path_to_next_python
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def get_script_command_line():
    return get_shell_command_line(sys.argv)


def get_shell_command_line(arg_list: list[str]):
    command_line = " ".join(shlex.quote(arg_item) for arg_item in arg_list)
    return command_line


def read_json_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def write_json_file(
    file_path: str,
    file_data: dict,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        json.dump(
            file_data,
            file_obj,
            indent=4,
        )
        file_obj.write("\n")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def read_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        return file_obj.read()


def write_text_file(
    file_path: str,
    file_data: str,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(file_data)


def _is_blank_line(line: str) -> bool:
    stripped = line.strip()
    return stripped == "" or stripped == "#"


def _replace_single_header_in_empty_lines(
    input_text: str,
    boilerplate_text: str,
) -> str:
    """
    FT_56_85_65_41.generated_boilerplate.md
    """
    input_lines = input_text.splitlines()
    boilerplate_lines = boilerplate_text.strip("\n").splitlines()
    boilerplate_height = len(boilerplate_lines)
    output_lines = input_lines[:1] + boilerplate_lines + input_lines[1 + boilerplate_height :]
    return "\n".join(output_lines) + "\n"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def _replace_multiple_body_in_empty_lines(
    input_text: str,
    boilerplate_text: str,
    min_lines_between: int,
) -> str:
    """
    FT_56_85_65_41.generated_boilerplate.md
    """
    input_lines = input_text.splitlines()
    boilerplate_line = boilerplate_text.strip("\n").splitlines()
    output_lines = []
    lines_since_last = 0
    line_i = 0
    while line_i < len(input_lines):
        input_line = input_lines[line_i]
        if lines_since_last >= min_lines_between and _is_blank_line(input_line):
            output_lines.extend(boilerplate_line)
            lines_since_last = 0
            line_i += 1
        else:
            output_lines.append(input_line)
            lines_since_last += 1
            line_i += 1
    return "\n".join(output_lines) + "\n"
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def is_venv() -> bool:
    # NOTE: `VIRTUAL_ENV` is not asserted because it is only set for `shell` by `source`-ing `venv/bin/activate`.
    #       Most of the commands avoid using `shell` (that is the goal for `protoprimer`).
    # NOTE: Restriction on `field_selected_python_file_abs_path`: it should not lead to `venv/bin/python`.
    #       It should use `sys.base_prefix` - see `get_path_to_base_python`.
    # TODO: Maybe it is possible to convert `field_selected_python_file_abs_path` to its base version automatically?
    if sys.prefix != sys.base_prefix:
        return True
    else:
        return False


def is_uv_venv(venv_cfg_file_abs_path: str) -> bool:
    with open(venv_cfg_file_abs_path, "r") as cfg_file:
        for file_line in cfg_file:
            if file_line.strip().startswith(f"{ConfConstGeneral.name_uv_package} ="):
                return True
    return False

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
def is_pip_venv(venv_cfg_file_abs_path: str) -> bool:
    # Not sure how to check if it regular `venv` other than saying it is not by `uv`:
    return not is_uv_venv(venv_cfg_file_abs_path)


def is_test_run() -> bool:
    """
    See: FT_83_60_72_19.test_perimeter.md
    """
    return ConfConstGeneral.pytest_module in sys.modules


def get_venv_type(local_venv_dir_abs_path: str) -> VenvDriverType:
    venv_cfg_file_abs_path = os.path.join(
        local_venv_dir_abs_path,
        ConfConstGeneral.venv_config_file_basename,
    )
    if not os.path.exists(venv_cfg_file_abs_path):
        raise AssertionError(f"File [{venv_cfg_file_abs_path}] does not exist")

    if is_uv_venv(venv_cfg_file_abs_path):
        return VenvDriverType.venv_uv
    elif is_pip_venv(venv_cfg_file_abs_path):
        return VenvDriverType.venv_pip
    else:
        raise AssertionError(f"Cannot determine `venv` type by file [{venv_cfg_file_abs_path}]")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def get_python_version(path_to_python: str) -> tuple[int, int, int]:
    """
    Executes a `python` binary and retrieves its version as a numeric tuple.
    """
    cmd_args: list[str] = [
        path_to_python,
        "-c",
        "import sys; print(tuple(sys.version_info[:3]))",
    ]
    cmd_output: str = subprocess.check_output(
        cmd_args,
        universal_newlines=True,
    )
    python_version: tuple[int, int, int] = ast.literal_eval(cmd_output.strip())
    assert (
        isinstance(python_version, tuple)
        and len(python_version) == 3
        and all(isinstance(i, int) for i in python_version)
        #
    ), f"invalid `python` version format: {python_version}"
    return python_version
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyTypeChecker
def parse_python_version(python_version: str) -> tuple[int, int, int]:
    """
    Converts a version `str` version "X.Y.Z" into a `tuple` of integers (X, Y, Z) handling:
    *   "3.13.4-beta" -> (3.13.4)
    *   "3" -> (3.0.0)
    """

    def _parse_version_int(version_part: str) -> int:
        number_match = re.search(r"\d+", version_part)
        return int(number_match.group()) if number_match else 0

    version_parts: tuple[str, str, str] = tuple((python_version.split(".") + ["0", "0", "0"])[:3])
    version_tuple: tuple[int, int, int] = tuple(_parse_version_int(part) for part in version_parts)
    return version_tuple


def import_proto_module(
    proto_module_name: str,
    proto_module_abs_path: str,
) -> types.ModuleType:
    """
    Import a module from an absolute path.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    module_spec = importlib.util.spec_from_file_location(
        proto_module_name,
        proto_module_abs_path,
    )
    assert module_spec is not None
    loaded_proto_module: types.ModuleType = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(loaded_proto_module)
    return loaded_proto_module


def select_python_file_abs_path(
    required_version: tuple[int, int, int],
    state_python_selector_file_abs_path_inited: str,
) -> str | None:
    """
    Run the `python` selector script specified in `ConfField.field_python_selector_file_rel_path`.
    """

    # TODO: TODO_41_10_50_01.implement_env_selector.md: What is the FT (feature_topic)?
    # TODO: There is `ConfField.field_python_selector_file_rel_path` - why is there hardcoded `python_selector_module`?
    # TODO: Implement local repo example with `python_selector_module`:
    # TODO: use constants:
    proto_module_name: str = "python_selector_module"
    python_selector_module = import_proto_module(
        proto_module_name,
        state_python_selector_file_abs_path_inited,
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    external_select_python_file_abs_path = getattr(
        python_selector_module,
        SelectorFunc.select_python_file_abs_path.value,
    )

    logger.debug(f"running `{SelectorFunc.select_python_file_abs_path.value}` from `{proto_module_name}`")
    selected_python_abs_path: str | None = external_select_python_file_abs_path(required_version)
    logger.debug(f"returned `selected_python_abs_path` value [{selected_python_abs_path}]")

    if selected_python_abs_path is not None:
        assert isinstance(selected_python_abs_path, str)
        try:
            logger.debug(f"trying `python` version of `selected_python_abs_path` [{selected_python_abs_path}]")
            python_version: tuple[int, int, int] = get_python_version(selected_python_abs_path)
            logger.info(f"`python` version of `selected_python_abs_path` [{selected_python_abs_path}] is [{python_version}]")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"`python` in `selected_python_abs_path` [{selected_python_abs_path}] failed without returning its version")
            selected_python_abs_path = None

    return selected_python_abs_path
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def search_python_file_abs_path_by_basename(required_version: tuple[int, int, int]) -> str | None:
    """
    Use `required_version` tuple formatted as (X, Y, Z) to try each basename (in that order):
    *   `pythonX.Y.Z`
    *   `pythonX.Y`
    *   `pythonX`
    *   `python`
    Return the abs path of the first basename found in `PATH` (e.g. via `shutil.which(...)`).
    The which also succeeds when invoked with the `--version` option.
    """
    (
        ver_x,
        ver_y,
        ver_z,
    ) = required_version
    python_basenames = [
        f"python{ver_x}.{ver_y}.{ver_z}",
        f"python{ver_x}.{ver_y}",
        f"python{ver_x}",
        f"python",
    ]
    for python_basename in python_basenames:
        logger.debug(f"trying `python_basename` [{python_basename}]")
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
        # TODO: This will not work on Windows:
        # noinspection PyDeprecation
        python_abs_path = shutil.which(python_basename)

        if python_abs_path is not None:
            try:
                logger.debug(f"checking version of `python_abs_path` [{python_abs_path}]")
                python_version: tuple[int, int, int] = get_python_version(python_abs_path)
                logger.info(f"`python_abs_path` [{python_abs_path}] returned its version [{python_version}]")
                return python_abs_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning(f"`python_abs_path` [{python_abs_path}] failed without returning its version")
                continue
    return None


def probe_python_file_abs_path(
    state_python_selector_file_abs_path_inited: str | None,
    state_required_python_version_inited: tuple[int, int, int],
) -> str | None:
    """
    Tries to select python via the selector script, falls back to search by basename.
    """
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    selected_python_file_abs_path: str | None
    if state_python_selector_file_abs_path_inited is not None:
        selected_python_file_abs_path = select_python_file_abs_path(
            state_required_python_version_inited,
            state_python_selector_file_abs_path_inited,
        )
    else:
        selected_python_file_abs_path = None

    if selected_python_file_abs_path is None:
        selected_python_file_abs_path = search_python_file_abs_path_by_basename(state_required_python_version_inited)
    return selected_python_file_abs_path


def log_python_context(log_level: int = logging.INFO):
    """
    This function helps to ensure and verify:
    UC_88_09_19_74.no_installation_outside_venv.md
    """
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_VIRTUAL_ENV}`: {os.environ.get(ConfConstInput.ext_env_var_VIRTUAL_ENV, None)}",
    )
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_PATH}`: {os.environ.get(ConfConstInput.ext_env_var_PATH, None)}",
    )
    logger.log(
        log_level,
        f"`{ConfConstInput.ext_env_var_PYTHONPATH}`: {os.environ.get(ConfConstInput.ext_env_var_PYTHONPATH, None)}",
    )
    logger.log(
        log_level,
        f"`sys.path`: {sys.path}",
    )
    logger.log(
        log_level,
        f"`sys.prefix`: {sys.prefix}",
    )
    logger.log(
        log_level,
        f"`sys.base_prefix`: {sys.base_prefix}",
    )
    logger.log(
        log_level,
        f"`sys.executable`: {sys.executable}",
    )
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def get_import_error_hint(neo_main_module: str) -> str:
    # See: UC_78_58_06_54.no_stray_packages.md
    return f"Is `{neo_main_module}` a (transitive) dependency of any `{ConfConstClient.default_pyproject_toml_basename}` being installed?"


def get_derived_config(proto_kernel_abs_path: str) -> dict:

    # NOTE: Assume (no verification) the module is loaded from
    #       (outside venv, outside local packages, outside global packages):
    os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = proto_kernel_abs_path
    # TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
    #       It is set to `StateStride.stride_py_arbitrary` even though we do not really know
    #       whether this python is outside `venv` (what `StateStride.stride_py_arbitrary` is really for).
    #       But it works for now until we an build different implementation for `get_derived_config` lib call.
    os.environ[EnvVar.var_PROTOPRIMER_PY_EXEC.value] = StateStride.stride_py_arbitrary.name

    env_ctx = EnvContext()

    state_derived_conf_data_loaded: dict = env_ctx.state_graph.eval_state(EnvState.state_derived_conf_data_loaded.name)
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    return state_derived_conf_data_loaded


def boot_env(venv_main_func: str):
    """
    This is a helper function for an FT_75_87_82_46.entry_script.md
    which implements FT_85_17_35_21.boot_env.md.

    It bootstraps `venv` from nothing.
    The majority of the entry scripts are supposed to use the `start_app` function instead
    (which only starts the specified `venv_main_func` assuming `venv` has already been bootstrapped).
    """
    _start_main(
        ExecMode.mode_boot,
        venv_main_func,
    )


def start_app(venv_main_func: str):
    """
    This is a helper function for an FT_75_87_82_46.entry_script.md
    which implements FT_05_08_64_67.start_app.md.
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    The function fails if `venv` is not created.
    In that case, the user must trigger the bootstrap manually
    (via a script which calls `boot_env` function).
    """
    _start_main(
        ExecMode.mode_start,
        venv_main_func,
    )


def _start_main(
    exec_mode: ExecMode,
    # Same format as in `EnvVar.var_PROTOPRIMER_MAIN_FUNC`:
    venv_main_func: str,
) -> None:

    # NOTE: Assume (no verification) the module is loaded from
    #       (outside venv, outside local packages, outside global packages):
    os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = os.path.abspath(__file__)

    os.environ[EnvVar.var_PROTOPRIMER_EXEC_MODE.value] = exec_mode.value
    os.environ[EnvVar.var_PROTOPRIMER_MAIN_FUNC.value] = venv_main_func
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
    module_name: str
    func_name: str
    if ConfConstGeneral.module_func_separator in venv_main_func:
        (
            module_name,
            func_name,
        ) = venv_main_func.split(
            ConfConstGeneral.module_func_separator,
            1,
        )
    else:
        raise ValueError(f"The specified main function [{venv_main_func}] does not match expected format `module_name:function_name`.")

    curr_py_exec = StateStride[
        os.getenv(
            EnvVar.var_PROTOPRIMER_PY_EXEC.value,
            ConfConstInput.default_PROTOPRIMER_PY_EXEC,
        )
    ]

    selected_main = proto_main
    try:
        # NOTE: `state_stride_src_updated_reached` forces restart with this `StateStride`:
        if curr_py_exec.value >= StateStride.stride_src_updated.value:
            venv_module = importlib.import_module(module_name)
            selected_main = getattr(venv_module, func_name)
            if exec_mode == ExecMode.mode_start:
                remove_protoprimer_env_vars(os.environ)
        elif curr_py_exec.value >= StateStride.stride_deps_updated.value:
            # TODO: It may not work in instant cases when `protoprimer` is not a dependency.
            # Switch from running `proto_code` to installed `venv` code:
            venv_module = importlib.import_module(f"{ConfConstGeneral.name_protoprimer_package}.{ConfConstGeneral.name_primer_kernel_module}")
            selected_main = getattr(venv_module, proto_main.__name__)
    except ImportError:
        if curr_py_exec.value >= StateStride.stride_src_updated.value:
            raise AssertionError(
                f"Failed to import `{module_name}` with `{EnvVar.var_PROTOPRIMER_PY_EXEC.value}` [{curr_py_exec.name}]. "
                f"{get_import_error_hint(module_name)} "
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
            )

    selected_main()


if __name__ == "__main__":
    proto_main()
