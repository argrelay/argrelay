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

# SPDX-License-Identifier: MIT
# Copyright (C) 2025 Alexey Pakseykin
# Source: https://github.com/uvsmtid/protoprimer
"""

TODO: TODO_91_75_37_57.implement_shebang_update.md / FT_02_89_37_65.shebang_line.md and update this comment:
The script must be run with Python 3.
Ensure that `python3` is in the `PATH` for shebang to work.
"""
from __future__ import annotations

import argparse
import atexit
import datetime
import enum
import importlib
import importlib.util
import json
import logging

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import typing
import venv
from types import CodeType
from typing import (
    Any,
    Generic,
    TypeVar,
)

# The release process ensures that content in this file matches the version below while tagging the release commit
# (otherwise, if the file comes from a different commit, the version is irrelevant):
__version__ = "0.5.1"

logger: logging.Logger = logging.getLogger()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


ValueType = TypeVar("ValueType")
DataValueType = TypeVar("DataValueType")


def main(
    configure_env_context: typing.Callable[[], EnvContext] | None = None,
):

    try:
        ensure_min_python_version()

        if configure_env_context is None:
            env_ctx = EnvContext()
        else:
            # See UC_10_80_27_57.extend_DAG.md:
            env_ctx = configure_env_context()

        # TODO: Do not call `state_graph.eval_state` directly - evaluate state via child state (to check that this is eligible).
        #       But... What is the child state here?

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_run_mode_executed: bool = env_ctx.state_graph.eval_state(
            TargetState.target_run_mode_executed.value.name
        )
        assert state_run_mode_executed
        atexit.register(lambda: env_ctx.print_exit_line(0))
    except SystemExit as sys_exit:
        exit_code: int = sys_exit.code
        if exit_code is None or exit_code == 0:
            atexit.register(lambda: env_ctx.print_exit_line(0))
        else:
            atexit.register(lambda: env_ctx.print_exit_line(exit_code))
        # We only catch `SystemExit` to print the status line.
        # The actual exit code is already in-flight with `SystemExit`, propagate it:
        raise
    except:
        atexit.register(lambda: env_ctx.print_exit_line(1))
        raise


def ensure_min_python_version():

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """
    Ensure the running Python interpreter is >= (major, minor, patch).
    """

    # FT_84_11_73_28: supported python versions:
    version_tuple: tuple[int, int, int] = (3, 7, 0)

    if sys.version_info < version_tuple:
        raise AssertionError(
            f"The version of Python used [{sys.version_info}] is below the min required [{version_tuple}]"
        )


class PythonExecutable(enum.IntEnum):
    """
    Python executables started during the bootstrap process - each replaces the executable program (via `os.execv`).

    See FT_72_45_12_06.python_executable.md
    """


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    # `python` executable has not been categorized yet:
    py_exec_unknown = -1

    # To run `proto_code` by any `python` outside `venv`:
    py_exec_arbitrary = 1

    # To run `python` of specific version (to create `venv` using that `python`):
    py_exec_required = 2

    # To use `venv` (to install packages):
    py_exec_venv = 3

    # To use the latest `protoprimer` package:
    py_exec_deps_updated = 4

    # To use the latest `proto_code` source:
    py_exec_src_updated = 5

    def __str__(self):
        return f"{self.name}[{self.value}]"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



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

    back_light_gray = "\033[47m"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    back_bright_red = "\033[101m"
    back_bright_green = "\033[102m"
    back_bright_yellow = "\033[103m"

    fore_dark_black = "\033[30m"
    fore_dark_red = "\033[31m"
    fore_dark_green = "\033[32m"
    fore_dark_yellow = "\033[33m"
    fore_dark_blue = "\033[34m"
    fore_dark_magenta = "\033[35m"
    fore_dark_cyan = "\033[36m"
    fore_dark_gray = "\033[90m"

    fore_bright_gray = "\033[90m"
    fore_bright_red = "\033[91m"
    fore_bright_green = "\033[92m"
    fore_bright_yellow = "\033[93m"
    fore_bright_blue = "\033[94m"
    fore_bright_magenta = "\033[95m"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    fore_bright_cyan = "\033[96m"
    fore_bright_white = "\033[97m"

    fore_bold_dark_red = "\033[1;31m"

    # Semantic colors:

    field_name = f"{fore_bright_magenta}"
    field_description = f"{fore_bright_cyan}"
    field_review = f"{fore_bright_green}"
    error_text = f"{back_bright_yellow}{fore_dark_red}"

    config_comment = f"{fore_bright_green}"
    config_missing = f"{fore_bright_blue}"
    config_unused = f"{fore_bright_yellow}"

    no_style = ""
    reset_style = "\033[0m"



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class KeyWord(enum.Enum):

    key_input = "input"
    key_primer = "primer"
    key_client = "client"
    key_global = "global"
    key_env = "env"
    key_local = "local"
    key_derived = "derived"

    key_var = "var"
    key_tmp = "tmp"
    key_log = "log"
    key_venv = "venv"
    key_cache = "cache"


class TopDir(enum.Enum):
    """
    Top-level directories (or dirs under `TopDir.dir_var`).

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """

    dir_var = f"{KeyWord.key_var.value}"
    dir_tmp = f"{KeyWord.key_tmp.value}"
    dir_log = f"{KeyWord.key_log.value}"
    dir_venv = f"{KeyWord.key_venv.value}"
    dir_cache = f"{KeyWord.key_cache.value}"


class ConfLeap(enum.Enum):
    """
    See FT_89_41_35_82.conf_leap.md
    """

    # surrogate: no associated config file:
    leap_input = f"{KeyWord.key_input.value}"

    leap_primer = f"{KeyWord.key_primer.value}"

    # TODO: Rename, use `global` instead:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    leap_client = f"{KeyWord.key_client.value}"

    # TODO: Remove, use `local` instead:
    leap_env = f"{KeyWord.key_env.value}"

    # surrogate: no associated config file:
    leap_derived = f"{KeyWord.key_derived.value}"

    leap_global = f"{KeyWord.key_global.value}"
    leap_local = f"{KeyWord.key_local.value}"


class PrimerRuntime(enum.Enum):
    """
    See FT_14_52_73_23.primer_runtime.md
    """

    runtime_proto = "proto"

    runtime_neo = "neo"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



class RunMode(enum.Enum):
    """
    Various modes the script can be run in.

    See FT_11_27_29_83.run_mode.md
    """

    mode_prime = "prime"

    # See UC_61_12_90_59.upgrade_venv.md
    mode_upgrade = "upgrade"

    # TODO: rename to "conf"?
    mode_config = "config"

    # TODO: implement?
    mode_check = "check"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


class CommandAction(enum.Enum):

    action_reinstall = "reinstall"

    action_command = "command"


class FilesystemObject(enum.Enum):

    fs_object_file = "file"

    fs_object_dir = "dir"

    fs_object_symlink = "symlink"


class PathType(enum.Enum):

    # If both paths are possible (absolute or relative):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    path_any = "any_path"

    # Relative path:
    path_rel = "rel_path"

    # Absolute path:
    path_abs = "abs_path"


class EnvVar(enum.Enum):
    """
    See FT_08_92_69_92.env_var.md
    """

    var_PROTOPRIMER_STDERR_LOG_LEVEL = "PROTOPRIMER_STDERR_LOG_LEVEL"

    var_PROTOPRIMER_PY_EXEC = "PROTOPRIMER_PY_EXEC"

    var_PROTOPRIMER_DO_INSTALL = "PROTOPRIMER_DO_INSTALL"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    var_PROTOPRIMER_PROTO_CODE = "PROTOPRIMER_PROTO_CODE"

    var_PROTOPRIMER_CONF_BASENAME = "PROTOPRIMER_CONF_BASENAME"

    var_PROTOPRIMER_START_ID = "PROTOPRIMER_START_ID"

    var_PROTOPRIMER_PACKAGE_DRIVER = "PROTOPRIMER_PACKAGE_DRIVER"

    # TODO: Consider splitting `is_test_run()` and `*_TEST_MODE` into different `feature_story`-ies.
    # TODO: Consider renaming `*_TEST_MODE` into something like `*_TEST_RESTART` (to emphasise what it actually indicates).
    var_PROTOPRIMER_TEST_MODE = "PROTOPRIMER_TEST_MODE"
    """
    See: FT_83_60_72_19.test_perimeter.md / test_fast_fat_min_mocked
    """


class ConfDst(enum.Enum):
    """
    See FT_23_37_64_44.conf_dst.md


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    TODO: Is this supposed to be called conf src (instead of `conf dst`)?
    """

    dst_shebang = "shebang"

    dst_global = "gconf"

    dst_local = "lconf"


class ValueName(enum.Enum):

    value_stderr_log_level = "stderr_log_level"

    value_do_install = "do_install"

    value_run_mode = "run_mode"

    value_final_state = "final_state"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    value_py_exec = "py_exec"

    value_primer_runtime = "primer_runtime"

    value_start_id = "start_id"

    value_project_descriptors = "project_descriptors"

    value_install_extras = "install_extras"

    value_package_driver = "package_driver"


class PathName(enum.Enum):

    path_proto_code = "proto_code"

    # TODO: use another suffix (not `dir`) as `dir` is specified by `FilesystemObject.fs_object_dir`
    # TODO: make use of it in naming states (instead of using only `path_proto_code`):
    path_proto_dir = "proto_dir"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    # TODO: Add a `feature_topic` for `ref root`:
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

    # TODO: Rename to "lconf_link" (otherwise, `local_conf_symlink_rel_path` does not reflect anything about `lconf` or `leap_env`):
    path_link_name = "link_name"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    path_default_env = "default_env"

    path_selected_env = f"selected_env"

    path_required_python = "required_python"

    path_local_venv = "local_venv"

    path_local_log = "local_log"

    path_local_tmp = "local_tmp"

    path_local_cache = "local_cache"

    path_build_root = "build_root"


class ParsedArg(enum.Enum):

    name_selected_env_dir = (

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        f"{PathName.path_selected_env.value}_{FilesystemObject.fs_object_dir.value}"
    )

    name_reinstall = f"do_{CommandAction.action_reinstall.value}"

    name_command = f"run_{CommandAction.action_command.value}"

    name_run_mode = str(ValueName.value_run_mode.value)
    name_final_state = str(ValueName.value_final_state.value)


class LogLevel(enum.Enum):
    name_quiet = "quiet"
    name_verbose = "verbose"


class SyntaxArg:

    arg_final_state = f"--{ParsedArg.name_final_state.value}"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    arg_c = f"-{CommandAction.action_command.value[0]}"
    arg_command = f"--{CommandAction.action_command.value}"

    arg_q = f"-{LogLevel.name_quiet.value[0]}"
    arg_quiet = f"--{LogLevel.name_quiet.value}"
    dest_quiet = f"{ValueName.value_stderr_log_level.value}_{LogLevel.name_quiet.value}"

    arg_v = f"-{LogLevel.name_verbose.value[0]}"
    arg_verbose = f"--{LogLevel.name_verbose.value}"
    dest_verbose = (
        f"{ValueName.value_stderr_log_level.value}_{LogLevel.name_verbose.value}"
    )

    arg_e = f"-{KeyWord.key_env.value[0]}"
    arg_env = f"--{KeyWord.key_env.value}"


class ConfField(enum.Enum):
    """
    Lists all conf fields from persisted files for every `ConfLeap.*`.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """

    ####################################################################################################################
    # `ConfLeap.leap_primer`-specific

    # state_ref_root_dir_abs_path_inited:
    field_ref_root_dir_rel_path = f"{PathName.path_ref_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # state_global_conf_dir_abs_path_inited
    field_global_conf_dir_rel_path = f"{PathName.path_global_conf.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    ####################################################################################################################
    # `ConfLeap.leap_client`-specific

    # state_local_conf_symlink_abs_path_inited:
    field_local_conf_symlink_rel_path = f"{PathName.path_local_conf.value}_{FilesystemObject.fs_object_symlink.value}_{PathType.path_rel.value}"

    # state_selected_env_dir_rel_path_inited:
    field_default_env_dir_rel_path = f"{PathName.path_default_env.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ####################################################################################################################
    # `ConfLeap.leap_env`-specific

    # None at the moment.

    ####################################################################################################################
    # Common overridable `global` and `local` fields: FT_23_37_64_44.conf_dst.md

    # state_required_python_file_abs_path_inited:
    field_required_python_file_abs_path = f"{PathName.path_required_python.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_abs.value}"

    # state_local_venv_dir_abs_path_inited:
    field_local_venv_dir_rel_path = f"{PathName.path_local_venv.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_log_dir_abs_path_inited:
    field_local_log_dir_rel_path = f"{PathName.path_local_log.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_tmp_dir_abs_path_inited:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    field_local_tmp_dir_rel_path = f"{PathName.path_local_tmp.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # TODO: combine by parent dir (~ `./var`):
    # state_local_cache_dir_abs_path_inited:
    field_local_cache_dir_rel_path = f"{PathName.path_local_cache.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # state_package_driver_inited:
    field_package_driver = f"{ValueName.value_package_driver.value}"

    # parent of `field_build_root_dir_rel_path` & `field_install_extras`:
    # state_project_descriptors_inited:
    field_project_descriptors = f"{ValueName.value_project_descriptors.value}"

    ####################################################################################################################

    # child of `field_project_descriptors`:
    field_build_root_dir_rel_path = f"{PathName.path_build_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    # child of `field_project_descriptors`:
    field_install_extras = f"{ValueName.value_install_extras.value}"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



class PackageDriverBase:

    def get_type(
        self,
    ) -> PackageDriverType:
        raise NotImplementedError()

    def is_mine_venv(
        self,
        local_venv_dir_abs_path: str,
    ) -> bool:
        return self.get_type() == get_venv_type(local_venv_dir_abs_path)

    def create_venv(
        self,
        required_python_file_abs_path: str,
        local_venv_dir_abs_path: str,
    ) -> None:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        logger.info(f"creating `venv` [{local_venv_dir_abs_path}]")
        self._create_venv_impl(required_python_file_abs_path, local_venv_dir_abs_path)

    def _create_venv_impl(
        self,
        required_python_file_abs_path: str,
        local_venv_dir_abs_path: str,
    ) -> None:
        raise NotImplementedError()

    def install_packages(
        self,
        required_python_file_abs_path: str,
        given_packages: list[str],
    ):
        """
        Install packages (which are not necessarily listed in any of the `pyproject.toml` files).

        This is against UC_78_58_06_54.no_stray_packages.md (in relation to the main `venv`),
        but it is required for separate non-main `venv`-s created for tools (like `uv`).

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        """
        sub_proc_args: list[str] = self.get_install_dependencies_cmd(
            required_python_file_abs_path,
        )
        sub_proc_args.extend(given_packages)

        logger.info(f"installing packages: {' '.join(sub_proc_args)}")

        subprocess.check_call(sub_proc_args)

    def install_dependencies(
        self,
        ref_root_dir_abs_path: str,
        required_python_file_abs_path: str,
        constraints_file_abs_path: str,
        project_descriptors: list[dict],
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
            project_build_root_dir_rel_path = project_descriptor[
                ConfField.field_build_root_dir_rel_path.value
            ]
            project_build_root_dir_abs_path = os.path.join(
                ref_root_dir_abs_path,
                project_build_root_dir_rel_path,
            )

            install_extras: list[str]
            if ConfField.field_install_extras.value in project_descriptor:
                install_extras = project_descriptor[

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                    ConfField.field_install_extras.value
                ]
            else:
                install_extras = []

            editable_project_install_args.append("--editable")
            if len(install_extras) > 0:
                editable_project_install_args.append(
                    f"{project_build_root_dir_abs_path}[{','.join(install_extras)}]"
                )
            else:
                editable_project_install_args.append(
                    f"{project_build_root_dir_abs_path}"
                )

        sub_proc_args = self.get_install_dependencies_cmd(
            required_python_file_abs_path,
        )
        sub_proc_args.extend(
            [

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                "--constraint",
                constraints_file_abs_path,
            ]
        )

        sub_proc_args.extend(editable_project_install_args)

        logger.info(f"installing projects: {' '.join(sub_proc_args)}")

        subprocess.check_call(sub_proc_args)

    def get_install_dependencies_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:
        raise NotImplementedError()

    def pin_versions(
        self,
        required_python_file_abs_path: str,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        constraints_file_abs_path: str,
    ) -> None:
        logger.info(
            f"generating version constraints file [{constraints_file_abs_path}]"
        )
        with open(constraints_file_abs_path, "w") as f:
            subprocess.check_call(
                self._get_pin_versions_cmd(required_python_file_abs_path),
                stdout=f,
            )

    def _get_pin_versions_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:
        raise NotImplementedError()


class PackageDriverPip(PackageDriverBase):


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def get_type(
        self,
    ) -> PackageDriverType:
        return PackageDriverType.driver_pip

    def _create_venv_impl(
        self,
        required_python_file_abs_path: str,
        local_venv_dir_abs_path: str,
    ) -> None:
        venv.create(
            local_venv_dir_abs_path,
            with_pip=True,
            upgrade_deps=True,
        )

    def get_install_dependencies_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return [
            required_python_file_abs_path,
            "-m",
            "pip",
            "install",
        ]

    def _get_pin_versions_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:
        return [
            required_python_file_abs_path,
            "-m",
            "pip",
            "freeze",
            "--exclude-editable",
        ]



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class PackageDriverUv(PackageDriverBase):

    def __init__(
        self,
        uv_exec_abs_path: str,
    ):
        self.uv_exec_abs_path: str = uv_exec_abs_path

    def get_type(
        self,
    ) -> PackageDriverType:
        return PackageDriverType.driver_uv

    def _create_venv_impl(
        self,
        required_python_file_abs_path: str,
        local_venv_dir_abs_path: str,
    ) -> None:
        subprocess.check_call(
            [

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                self.uv_exec_abs_path,
                "venv",
                "--python",
                required_python_file_abs_path,
                local_venv_dir_abs_path,
            ]
        )

    def get_install_dependencies_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:
        return [
            self.uv_exec_abs_path,
            "pip",
            "install",
            "--python",
            required_python_file_abs_path,
        ]


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def _get_pin_versions_cmd(
        self,
        required_python_file_abs_path: str,
    ) -> list[str]:
        return [
            self.uv_exec_abs_path,
            "pip",
            "freeze",
            "--exclude-editable",
            "--python",
            required_python_file_abs_path,
        ]


class ShellType(enum.Enum):

    shell_bash = "bash"

    shell_zsh = "zsh"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


def remove_protoprimer_env_vars(env_vars: dict[str, str]) -> dict[str, str]:
    for env_var in EnvVar:
        env_vars.pop(env_var.value, None)
    return env_vars


class ShellDriverBase:

    def __init__(
        self,
        shell_abs_path: str,
        shell_env_vars: dict[str, str],
        cache_dir_abs_path: str,
    ):
        self.shell_abs_path: str = shell_abs_path
        self.shell_args: list[str] = [
            self.shell_abs_path,
        ]
        self.shell_env_vars: dict[str, str] = shell_env_vars

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.cache_dir_abs_path: str = cache_dir_abs_path

    def get_type(self) -> ShellType:
        raise NotImplementedError()

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
    def get_venv_activate_script_abs_path(
        venv_abs_path: str,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> str:
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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

source {self.get_venv_activate_script_abs_path(venv_abs_path)}
""",
        )

    def configure_interactive_shell(self, has_command: bool) -> None:
        """
        Implements: UC_36_72_11_12.pipe_to_execute_with_activated_venv.md
        """
        raise NotImplementedError()

    def run_shell(
        self,
        command_line: str | None,
        stderr_log_handler: logging.Handler,
        venv_abs_path: str,
    ) -> int:

        self.write_init_file(venv_abs_path)

        self.configure_interactive_shell(command_line is not None)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

        os.execve(
            self.shell_abs_path,
            self.shell_args,
            self.shell_env_vars,
        )

        return 0


class ShellDriverBash(ShellDriverBase):

    def get_type(
        self,
    ) -> ShellType:
        return ShellType.shell_bash

    def get_init_file_basename(self):
        return ".bashrc"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def configure_interactive_shell(self, has_command: bool) -> None:
        self.shell_args.extend(
            [
                # `bash` uses explicit override for `.bashrc`:
                "--init-file",
                self.get_init_file_abs_path(),
            ]
        )


class ShellDriverZsh(ShellDriverBase):

    def get_type(
        self,
    ) -> ShellType:
        return ShellType.shell_zsh

    def get_init_file_basename(self):
        return ".zshrc"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def configure_interactive_shell(self, has_command: bool) -> None:
        if not sys.stdin.closed and not sys.stdin.isatty() and not has_command:
            # Unlike `bash`, `zsh` reads `tty` instead of `stdin` (for UI control) unless `-s` is specified:
            self.shell_args.extend(
                [
                    "-s",
                ]
            )
        # `zsh` takes "dot dir" path to find overridden `.zshrc`:
        self.shell_env_vars["ZDOTDIR"] = os.path.dirname(self.get_init_file_abs_path())


def _get_shell_driver(cache_dir_abs_path: str) -> ShellDriverBase:

    var_shell = "SHELL"
    shell_abs_path: str | None = os.environ.get(var_shell, None)
    shell_driver_type: type[ShellDriverBase]

    if shell_abs_path is None:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        # TODO: Implement `ShellDriverSh` using `/bin/sh` instead:
        logger.warning(f"env var `{var_shell}` is not set - assuming `bash` as default")
        shell_abs_path = shutil.which("bash")
        shell_driver_type = ShellDriverBash
    elif os.path.basename(shell_abs_path) == ShellType.shell_bash.value:
        shell_driver_type = ShellDriverBash
    elif os.path.basename(shell_abs_path) == ShellType.shell_zsh.value:
        shell_driver_type = ShellDriverZsh
    else:
        raise ValueError(f"env var `{var_shell}` has unknown value [{shell_abs_path}]")

    return shell_driver_type(
        shell_abs_path=shell_abs_path,
        shell_env_vars=remove_protoprimer_env_vars(os.environ.copy()),
        cache_dir_abs_path=cache_dir_abs_path,
    )


class PackageDriverType(enum.Enum):
    """

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    See UC_09_61_98_94.installer_pip_vs_uv.md
    """

    driver_pip = PackageDriverPip

    driver_uv = PackageDriverUv


class ConfConstGeneral:

    # The project name = package name:
    name_protoprimer_package = "protoprimer"

    # Concept name of the FT_90_65_67_62.proto_code.md:
    name_proto_code = "proto_code"

    # The main module of the `protoprimer` package (this file):
    name_primer_kernel_module = "primer_kernel"

    # The default name of for the module of the client own copy of `proto_code` (this file).

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    # It is a different name from `name_primer_kernel_module` purely to avoid confusion.
    default_proto_code_module = "proto_kernel"

    # File name of the FT_90_65_67_62.proto_code.md:
    default_proto_code_basename = f"{default_proto_code_module}.py"

    name_uv_package = "uv"

    curr_dir_rel_path = "."

    # TODO: use lambdas to generate based on input (instead of None):
    # This is a value declared for completeness,
    # but unused (evaluated dynamically via the bootstrap process):
    input_based = None

    file_rel_path_venv_bin = os.path.join(
        "bin",
    )

    file_rel_path_venv_python = os.path.join(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

    log_section_delimiter = "=" * 5

    func_get_proto_code_generated_boilerplate_single_header = lambda module_obj: (
        f"""
################################################################################
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

    func_get_proto_code_generated_boilerplate_multiple_body = lambda module_obj: (
        f"""
########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
"""
    )

    relative_path_field_note: str = (
        f"The path is relative to the `{PathName.path_ref_root.value}` dir specified in the `{ConfField.field_ref_root_dir_rel_path.value}` field."
    )
    common_field_global_note: str = (

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        f"This field can be specified in global config (see `{ConfLeap.leap_client.name}`) but it is override-able by local environment-specific config (see `{ConfLeap.leap_env.name}`)."
    )
    common_field_local_note: str = (
        f"This local environment-specific field overrides the global one (see description in `{ConfLeap.leap_client.name}`)."
    )
    func_note_derived_based_on_common = lambda field_name: (
        f"This value is derived from `{field_name}` in `{ConfLeap.leap_client.name}` (override-able in `{ConfLeap.leap_env.name}`) - see description there."
    )
    func_note_derived_based_on_conf_leap_field = lambda field_name, conf_leap: (
        f"This value is derived from `{field_name}` - see description in `{conf_leap.name}`."
    )


class ConfConstInput:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_input
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    default_proto_conf_dir_rel_path: str = f"{ConfConstGeneral.name_proto_code}"

    conf_file_ext = "json"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_primer`:
    default_file_basename_conf_primer = (
        f"{ConfConstGeneral.name_protoprimer_package}.{conf_file_ext}"
    )

    ext_env_var_VIRTUAL_ENV: str = "VIRTUAL_ENV"
    ext_env_var_PATH: str = "PATH"
    ext_env_var_PYTHONPATH: str = "PYTHONPATH"

    default_PROTOPRIMER_STDERR_LOG_LEVEL: str = "WARNING"

    default_PROTOPRIMER_PY_EXEC: str = PythonExecutable.py_exec_unknown.name

    default_PROTOPRIMER_DO_INSTALL: str = str(True)


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


class ConfConstPrimer:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_primer
    """

    default_client_conf_dir_rel_path: str = f"{ConfDst.dst_global.value}"

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_client`:
    default_file_basename_leap_client: str = (
        ConfConstInput.default_file_basename_conf_primer
    )

    # TODO: Is this still needed if we propagate conf file base name primer -> client -> env?
    default_client_conf_file_rel_path: str = os.path.join(
        default_client_conf_dir_rel_path,
        default_file_basename_leap_client,
    )



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class ConfConstClient:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_client
    """

    # TODO: Is this used? If link_name is not specified, the env conf dir becomes ref root dir:
    default_dir_rel_path_leap_env_link_name: str = os.path.join(
        ConfDst.dst_local.value,
    )

    # FT_59_95_81_63.env_layout.md / max layout
    default_default_env_dir_rel_path: str = os.path.join(
        "dst",
        "default_env",
    )

    # Next FT_89_41_35_82.conf_leap.md: `ConfLeap.leap_env`:
    default_file_basename_leap_env: str = (
        ConfConstInput.default_file_basename_conf_primer
    )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    default_env_conf_file_rel_path: str = os.path.join(
        default_default_env_dir_rel_path,
        default_file_basename_leap_env,
    )

    default_pyproject_toml_basename = "pyproject.toml"


class ConfConstEnv:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_env
    """

    # TODO: This may not work everywhere:
    default_file_abs_path_python = "/usr/bin/python"

    default_dir_rel_path_venv = "venv"

    default_dir_rel_path_log = "log"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    default_dir_rel_path_tmp = "tmp"

    default_dir_rel_path_cache = "cache"

    default_package_driver = PackageDriverType.driver_uv.name

    default_project_descriptors = [
        {
            ConfField.field_build_root_dir_rel_path.value: ".",
            ConfField.field_install_extras.value: [],
        },
    ]

    constraints_txt_basename = "constraints.txt"


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
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
        help="decrease log verbosity level",
    )
    parent_argparser.add_argument(
        # See: FT_38_73_38_52.log_verbosity.md
        SyntaxArg.arg_v,
        SyntaxArg.arg_verbose,
        action="count",
        dest=SyntaxArg.dest_verbose,
        default=0,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        help="increase log verbosity level",
    )
    return parent_argparser


def _create_child_argparser(
    parent_argparsers,
):
    def create_prime_parser(sub_command_parsers):
        sub_command_desc = "Prime the environment to make it ready to use."
        parser_prime = sub_command_parsers.add_parser(
            RunMode.mode_prime.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_prime.set_defaults(
            run_mode=RunMode.mode_prime.value,
        )
        parser_prime.add_argument(
            SyntaxArg.arg_e,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            "--env",
            type=str,
            default=None,
            dest=ParsedArg.name_selected_env_dir.value,
            metavar=ParsedArg.name_selected_env_dir.value,
            help=(
                f"Path to the env-specific config dir. "
                f"If specified, `{RunMode.mode_prime.value}` run mode creates the symlink to that dir. "
                f"If not specified, the existing symlink is reused. "
            ),
        )
        parser_prime.add_argument(
            SyntaxArg.arg_c,
            SyntaxArg.arg_command,
            type=str,
            dest=ParsedArg.name_command.value,
            metavar=ParsedArg.name_command.value,
            help="Command to execute after the bootstrap.",
        )
        parser_prime.add_argument(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

    def create_upgrade_parser(sub_command_parsers):
        sub_command_desc = (
            "Re-create `venv`, re-install dependencies, and re-pin versions."
        )
        parser_upgrade = sub_command_parsers.add_parser(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            RunMode.mode_upgrade.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_upgrade.set_defaults(
            run_mode=RunMode.mode_upgrade.value,
        )

    def create_config_parser(sub_command_parsers):
        sub_command_desc = "Print effective config."
        parser_config = sub_command_parsers.add_parser(
            RunMode.mode_config.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_config.set_defaults(
            run_mode=RunMode.mode_config.value,
        )

    def create_check_parser(sub_command_parsers):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        sub_command_desc = "Check the environment configuration."
        parser_check = sub_command_parsers.add_parser(
            RunMode.mode_check.value,
            help=sub_command_desc,
            description=sub_command_desc,
        )
        parser_check.set_defaults(
            run_mode=RunMode.mode_check.value,
        )

    child_argparser = CustomArgumentParser(
        description=(
            f"Bootstrap the environment (see default `{RunMode.mode_prime.value}` mode) "
            f"according to the configuration (see `{RunMode.mode_config.value}` mode)."
        ),
        parents=parent_argparsers,
    )

    child_argparsers = child_argparser.add_subparsers(
        dest=ParsedArg.name_run_mode.value,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        title="Run modes",
        description=f"Select one of the following sub-commands as a run mode (default: `{RunMode.mode_prime.value}`).",
        metavar="run_mode",
    )
    child_argparsers.required = False

    create_prime_parser(child_argparsers)
    create_upgrade_parser(child_argparsers)
    create_config_parser(child_argparsers)
    create_check_parser(child_argparsers)

    return child_argparser


def parse_args(remaining_argv=None):
    """
    Parse CLI args by creating parent and child (sub-command) parsers.

    This function uses a two-phase parsing to allow common options
    which can be placed anywhere:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    * ... -q prime (option before sub-command)
    * ... prime -q (option after sub-command)
    """

    if remaining_argv is None:
        remaining_argv = sys.argv[1:]

    # Phase 1: parse common args:
    parent_argparser = _create_parent_argparser()
    (
        parsed_args,
        remaining_argv,
    ) = parent_argparser.parse_known_args(remaining_argv)

    # Phase 2: parse sub-command args:
    child_argparser = _create_child_argparser(
        parent_argparsers=[
            parent_argparser,
        ],
    )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    # TODO: use constants:
    if "-h" not in remaining_argv and "--help" not in remaining_argv:
        try:
            # Try to parse with `prime` as the default sub-command:
            parsed_args = child_argparser.parse_args(
                [RunMode.mode_prime.value] + remaining_argv,
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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                exit(2)
    else:
        parsed_args = child_argparser.parse_args(
            remaining_argv,
            namespace=parsed_args,
        )

    return parsed_args


def str_to_bool(v: str) -> bool:
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError(f"[{bool.__name__}]-like value expected.")


########################################################################################################################
# Visitors for config nodes.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# See: FT_19_44_42_19.effective_config.md


class AbstractConfigVisitor:
    """
    Implements the visitor pattern for classed derived from `AbstractConfigNode`.
    """

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ) -> None:
        pass

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        pass

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        pass

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        pass


class RenderConfigVisitor(AbstractConfigVisitor):
    """
    Render a JSON-like data structure into data coded in `python` (with annotations as comments).

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    It renders loaded config as: FT_19_44_42_19.effective_config.md
    """

    def __init__(
        self,
        is_quiet: bool = False,
    ):
        self.is_quiet: bool = is_quiet
        self.rendered_value: str = ""

    def render_node(
        self,
        config_node: "AbstractConfigNode",
    ) -> str:
        s: str = ""
        if not self.is_quiet:
            s += " " * config_node.node_indent + os.linesep
        s += self._render_node_annotation(config_node)


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        rendered_value: str = self._render_node_value(config_node)
        if config_node.is_present:
            s += rendered_value
        else:
            s += self._comment_with_indent(
                rendered_value,
                config_node,
            )
        return s

    def _render_node_annotation(
        self,
        config_node: "AbstractConfigNode",
    ) -> str:
        if self.is_quiet:
            return ""
        note_text = config_node.note_text
        if len(note_text.strip()) == 0:
            return ""
        annotation_lines = note_text.splitlines()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        s = ""
        for annotation_line in annotation_lines:
            s += (
                " " * config_node.node_indent
                + f"{config_node.note_color.value}# {annotation_line}{TermColor.reset_style.value}"
                + os.linesep
            )
        return s

    @staticmethod
    def _render_node_name(
        config_node: "AbstractConfigNode",
    ) -> str:
        if config_node.node_name is None:
            return ""
        return f"{json.dumps(config_node.node_name)}: "

    def _render_node_value(
        self,
        config_node: "AbstractConfigNode",

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> str:
        config_node.accept_visitor(self)
        return self.rendered_value

    def _comment_with_indent(
        self,
        rendered_text: str,
        config_node: "AbstractConfigNode",
    ) -> str:
        if self.is_quiet:
            return ""
        deactivated_lines = []
        rendered_lines = rendered_text.splitlines()
        for rendered_line in rendered_lines:
            deactivated_lines.append(
                rendered_line[: config_node.node_indent]
                + f"{config_node.note_color.value}# "
                + rendered_line[config_node.node_indent :]
                + f"{TermColor.reset_style.value}"
            )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return os.linesep.join(deactivated_lines)

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ):
        s: str = ""
        s += (
            " " * dict_node.node_indent
            + self._render_node_name(dict_node)
            + "{"
            + os.linesep
        )
        for child_name, child_node in dict_node.child_nodes.items():
            rendered_child = self.render_node(child_node)
            s += rendered_child
            if rendered_child or not self.is_quiet:
                s += os.linesep
        s += " " * dict_node.node_indent + "},"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.rendered_value = s

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ):
        s: str = ""
        s += (
            " " * list_node.node_indent
            + self._render_node_name(list_node)
            + "["
            + os.linesep
        )
        for child_node in list_node.child_nodes:
            rendered_child = self.render_node(child_node)
            s += rendered_child
            if rendered_child or not self.is_quiet:
                s += os.linesep
        s += " " * list_node.node_indent + "],"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.rendered_value = s

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ):
        s: str = ""
        if isinstance(value_node.orig_data, str):
            s += (
                " " * value_node.node_indent
                + self._render_node_name(value_node)
                # Use double-quote for `str`:
                + f"{json.dumps(value_node.orig_data)}"
                + ","
            )
        else:
            s += (
                " " * value_node.node_indent
                + self._render_node_name(value_node)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                + f"{repr(value_node.orig_data)}"
                + ","
            )
        self.rendered_value = s

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ):
        # Remove the last char (which is supposed to be `,`):
        rendered_child: str = self.render_node(root_node.child_node)[:-1]
        s: str = ""
        s += " " * root_node.node_indent + f"{root_node.node_name} = (" + os.linesep
        s += rendered_child + os.linesep
        s += " " * root_node.node_indent + ")"
        self.rendered_value = s


class ConfigBuilderVisitor(AbstractConfigVisitor):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """
    Builds a config node and visits it to build children config nodes.
    """

    def build_config_node(
        self,
        orig_data: Any,
        **kwargs,
    ) -> "AbstractConfigNode":
        if isinstance(orig_data, dict):
            return self.build_dict_node(
                orig_data=orig_data,
                **kwargs,
            )
        elif isinstance(orig_data, list):
            return self.build_list_node(
                orig_data=orig_data,
                **kwargs,
            )
        else:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            return self.build_value_node(
                orig_data=orig_data,
                **kwargs,
            )

    def build_dict_node(
        self,
        **kwargs,
    ) -> "AbstractDictNode":
        kwargs.pop("is_present", None)
        return AbstractDictNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def build_list_node(
        self,
        **kwargs,
    ) -> "AbstractListNode":

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        kwargs.pop("is_present", None)
        return AbstractListNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def build_value_node(
        self,
        **kwargs,
    ) -> "AbstractValueNode":
        kwargs.pop("is_present", None)
        return AbstractValueNode(
            is_present=True,
            **kwargs,
        )

    def build_root_node(
        self,
        **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> "AbstractRootNode":
        kwargs.pop("is_present", None)
        return AbstractRootNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ) -> None:
        if dict_node.orig_data is None:
            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        for field_name, field_value in dict_node.orig_data.items():
            child_node = self.build_config_node(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                node_name=field_name,
                node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
                orig_data=field_value,
                **kwargs,
            )
            dict_node.child_nodes[field_name] = child_node

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:
        if list_node.orig_data is None:
            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        for list_item in list_node.orig_data:
            child_node = self.build_config_node(
                node_name=None,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                node_indent=list_node.node_indent + AbstractConfigNode.indent_size,
                orig_data=list_item,
                **kwargs,
            )
            list_node.child_nodes.append(child_node)

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        # Value nodes have no children.
        pass

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        if root_node.orig_data is None:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        root_node.child_node = self.build_config_node(
            node_name=None,
            node_indent=root_node.node_indent + AbstractConfigNode.indent_size,
            orig_data=root_node.orig_data,
            **kwargs,
        )


class AnnotateUnusedVisitor(AbstractConfigVisitor):
    """
    Annotates a config node as unused (not recursively).
    """

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        **kwargs,
    ) -> None:
        dict_node.note_text = f"This `dict` is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        dict_node.note_color = TermColor.config_unused

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:
        list_node.note_text = f"This `list` is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        list_node.note_color = TermColor.config_unused

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        value_node.note_text = f"This value is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        value_node.note_color = TermColor.config_unused

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        root_node.note_text = f"This config is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        root_node.note_color = TermColor.config_unused


class UnusedConfigBuilderVisitor(ConfigBuilderVisitor):
    """
    Builds a config node (recursively) and annotates that top-level node as unused.
    """

    def __init__(
        self,
    ):
        self.recursion_level: int = 0


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def build_config_node(
        self,
        orig_data: Any,
        **kwargs,
    ) -> "AbstractConfigNode":
        self.recursion_level += 1
        config_node: AbstractConfigNode = super().build_config_node(
            orig_data=orig_data,
            **kwargs,
        )
        self.recursion_level -= 1
        if self.recursion_level == 0:
            # Set annotation only for the top-level node:
            config_node.accept_visitor(AnnotateUnusedVisitor())
        return config_node


########################################################################################################################
# Abstract config node types.
# See: FT_19_44_42_19.effective_config.md

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



class AbstractConfigNode(Generic[ValueType]):
    """
    Models a node in a JSON-like (nested) data structure.

    It loads config from: FT_48_62_07_98.config_format.md
    """

    indent_size: int = 4

    def __init__(
        self,
        node_name: str | None,
        node_indent: int,
        is_present: bool,
        orig_data: ValueType | None,
        **kwargs,
    ):
        self.node_name: str | None = node_name

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.node_indent: int = node_indent

        # Unlike simply setting `orig_data` to `None`, setting `is_present` to `False`
        # allows distinguishing between (A) a valid `None` value and (B) a missing value.
        self.is_present: bool = is_present

        self.orig_data: ValueType | None = orig_data

        self.note_text: str = ""
        self.note_color: TermColor = (
            TermColor.config_comment if is_present else TermColor.config_missing
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        """
        Accept a `AbstractConfigVisitor`.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        """
        raise NotImplementedError()


class AbstractDictNode(AbstractConfigNode[dict]):
    """
    Models `{ ... }` JSON-like `dict`.
    """

    def __init__(
        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_nodes: dict[str, AbstractConfigNode] = {}
        self.accept_visitor(
            child_builder,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_dict(
            self,
            **kwargs,
        )


class AbstractListNode(AbstractConfigNode[list]):
    """
    Models `[ ... ]` JSON-like `list`.
    """

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_nodes: list[AbstractConfigNode] = []
        self.accept_visitor(
            child_builder,
            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_list(
            self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            **kwargs,
        )


class AbstractValueNode(AbstractConfigNode[ValueType]):
    """
    Models any simple value in JSON-like data structure (neither `list` nor `dict`).
    """

    def __init__(
        self,
        orig_data: ValueType | None,
        **kwargs,
    ):
        super().__init__(
            orig_data=orig_data,
            **kwargs,
        )
        assert not isinstance(orig_data, list)
        assert not isinstance(orig_data, dict)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_value(
            self,
            **kwargs,
        )


class AbstractRootNode(AbstractConfigNode[ValueType]):
    """
    Wraps any given `child_node` as `node_name = ( child_node )`.

    Syntactically, it represents an assignment to the `node_name` var and
    allows accessing the assigned data via `compile_effective_config`.
    """


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def __init__(
        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_node: AbstractConfigNode | None = None
        self.accept_visitor(
            child_builder,
            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_root(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            self,
            **kwargs,
        )

    def compile_effective_config(
        self,
    ) -> Any:
        """
        Produces rendered config and compiles it to access data.
        """
        generated_code = RenderConfigVisitor().render_node(self)
        # TODO: Instead, maybe configure rendering without colors?
        generated_code = self._erase_annotation_colors(generated_code)
        compiled_code: CodeType = compile(generated_code, "<string>", "exec")
        exec_namespace = {}
        exec(compiled_code, exec_namespace)
        return exec_namespace[self.node_name]

    @staticmethod
    def _erase_annotation_colors(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        generated_code: str,
    ):
        for term_color in [
            TermColor.config_comment,
            TermColor.config_missing,
            TermColor.config_unused,
            TermColor.reset_style,
        ]:
            generated_code = generated_code.replace(term_color.value, "")
        return generated_code


class AbstractConfLeapRootNode(AbstractRootNode):
    """
    Base implementation for all `ConfLeap.*`.
    """

    def __init__(
        self,
        conf_leap: ConfLeap,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            node_name=conf_leap.name,
            is_present=True,
            child_builder=child_builder,
            **kwargs,
        )


class AbstractConfLeapNodeBuilder(ConfigBuilderVisitor):

    @staticmethod
    def _create_used_dict_field(
        dict_node: AbstractDictNode,
        field_name: str,
        node_class: type,
        conf_leap: ConfLeap,
        **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> AbstractDictNode:
        field_name = field_name
        kwargs.pop("is_present", None)
        kwargs.pop("orig_data", None)
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        field_node: AbstractConfigNode = node_class(
            node_name=field_name,
            node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
            is_present=(field_name in dict_node.orig_data),
            orig_data=dict_node.orig_data.get(field_name, None),
            conf_leap=conf_leap,
            **kwargs,
        )
        dict_node.child_nodes[field_name] = field_node
        return field_node

    def _create_common_fields(
        self,
        dict_node: AbstractDictNode,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        conf_leap: ConfLeap,
    ):
        # Common overridable `global` and `local` fields: FT_23_37_64_44.conf_dst.md

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_required_python_file_abs_path.value,
            node_class=Node_field_required_python_file_abs_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_venv_dir_rel_path.value,
            node_class=Node_field_local_venv_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            field_name=ConfField.field_local_log_dir_rel_path.value,
            node_class=Node_field_local_log_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_tmp_dir_rel_path.value,
            node_class=Node_field_local_tmp_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_cache_dir_rel_path.value,
            node_class=Node_field_local_cache_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            dict_node=dict_node,
            field_name=ConfField.field_package_driver.value,
            node_class=Node_field_package_driver,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_project_descriptors.value,
            node_class=Node_field_project_descriptors,
            conf_leap=conf_leap,
        )

    @staticmethod
    def _create_unused_dict_fields(
        dict_node: AbstractDictNode,
    ):
        for field_name, field_value in dict_node.orig_data.items():

            if field_name not in dict_node.child_nodes:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                dict_node.child_nodes[
                    field_name
                ] = UnusedConfigBuilderVisitor().build_config_node(
                    node_name=field_name,
                    node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
                    orig_data=field_value,
                )


########################################################################################################################
# `ConfLeap.leap_input` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_input(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_input

        field_node: AbstractConfigNode

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_proto_code_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            f"Value `{EnvState.state_proto_code_file_abs_path_inited.name}` is an absolute path to `{ConfConstGeneral.name_proto_code}`.\n"
            f"It allows resolving all other relative paths (via `{PathName.path_ref_root.value}` - see field `{ConfField.field_ref_root_dir_rel_path.value}`).\n"
        )

        field_node = self._create_used_dict_field(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            dict_node=dict_node,
            field_name=EnvState.state_primer_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        # TODO: Link to `ConfLeap.leap_derived` fields.
        field_node.note_text = (
            f"Value `{EnvState.state_primer_conf_file_abs_path_inited.name}` is an absolute path to `{ConfLeap.leap_primer}` config file.\n"
            f"The config file is selected from the list of possible candidates (whichever is found first, replacing extension to `.{ConfConstInput.conf_file_ext}`):\n"
            f"*   basename of the entry script,\n"
            f"*   basename of the `{ConfConstGeneral.name_proto_code}` file,\n"
            f"*   default `{ConfConstInput.default_file_basename_conf_primer}`.\n"
            f"Note that the selected config file basename is subsequently re-used for others:\n"
            f"*   see `{EnvState.state_global_conf_file_abs_path_inited.name}` for `{ConfLeap.leap_client.name}`,\n"
            f"*   see `{EnvState.state_local_conf_file_abs_path_inited.name}` for `{ConfLeap.leap_env.name}`.\n"
        )

        self._create_unused_dict_fields(dict_node)


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


# noinspection PyPep8Naming
class RootNode_input(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_input`.
    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_input,
            child_builder=Builder_RootNode_input(),
            **kwargs,
        )
        self.note_text = (
            f"The `{ConfLeap.leap_input.name}` data is taken from the `{ConfConstGeneral.name_proto_code}` process input (not configured in files):\n"
            f"*   CLI args, environment variables, current directory, ...\n"
            f"*   combination of the above with applied defaults.\n"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )


########################################################################################################################
# `ConfLeap.leap_primer` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_primer(AbstractConfLeapNodeBuilder):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
    ):
        self.state_primer_conf_file_abs_path_inited: str = (
            state_primer_conf_file_abs_path_inited
        )

    def visit_dict(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:
        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_ref_root_dir_rel_path.value,
            node_class=Node_field_ref_root_dir_rel_path,
            state_primer_conf_file_abs_path_inited=self.state_primer_conf_file_abs_path_inited,
            conf_leap=ConfLeap.leap_primer,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_global_conf_dir_rel_path.value,
            node_class=Node_field_global_conf_dir_rel_path,
            state_primer_conf_file_abs_path_inited=self.state_primer_conf_file_abs_path_inited,
            conf_leap=ConfLeap.leap_primer,
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_primer(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_primer`.
    """

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_primer,
            child_builder=Builder_RootNode_primer(
                state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
            ),
            **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )
        self.state_primer_conf_file_abs_path_inited: str = (
            state_primer_conf_file_abs_path_inited
        )
        self.note_text = f"The `{ConfLeap.leap_primer.name}` data is loaded from the [{self.state_primer_conf_file_abs_path_inited}] file."


# noinspection PyPep8Naming
class Node_field_ref_root_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.state_primer_conf_file_abs_path_inited: str = (
            state_primer_conf_file_abs_path_inited

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )
        self.note_text = (
            f"Field `{ConfField.field_ref_root_dir_rel_path.value}` points to the dir called `{PathName.path_ref_root.value}`.\n"
            f"The path is relative to the `{ConfConstGeneral.name_proto_code}` file [{self.state_primer_conf_file_abs_path_inited}].\n"
            f"Normally, the `{PathName.path_ref_root.value}` dir is the client repo root, but it can be anything.\n"
            f"See `{EnvState.state_ref_root_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"the derived abs path is the base path for all the configured relative paths (except for this field itself, obviously).\n"
        )


# noinspection PyPep8Naming
class Node_field_global_conf_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )
        self.state_primer_conf_file_abs_path_inited: str = (
            state_primer_conf_file_abs_path_inited
        )
        self.note_text = (
            f"Field `{ConfField.field_global_conf_dir_rel_path.value}` points to the global config dir (as opposed to local config dir `{ConfField.field_local_conf_symlink_rel_path.value}`).\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"See `{EnvState.state_global_conf_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"normally, the resolved global config dir contains all other global client config files.\n"
        )


########################################################################################################################
# `ConfLeap.leap_client` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_client(AbstractConfLeapNodeBuilder):


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_client

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_conf_symlink_rel_path.value,
            node_class=Node_field_local_conf_symlink_rel_path,
            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_default_env_dir_rel_path.value,
            node_class=Node_field_default_env_dir_rel_path,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_common_fields(
            dict_node=dict_node,
            conf_leap=conf_leap,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_client(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_client`.
    """

    def __init__(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_global_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_client,
            child_builder=Builder_RootNode_client(),
            **kwargs,
        )
        self.state_global_conf_file_abs_path_inited: str = (
            state_global_conf_file_abs_path_inited
        )
        self.note_text = f"The `{ConfLeap.leap_client.name}` data is loaded from the [{self.state_global_conf_file_abs_path_inited}] file."


# noinspection PyPep8Naming
class Node_field_local_conf_symlink_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ):
        super().__init__(
            **kwargs,
        )
        self.note_text = (
            f"Field `{ConfField.field_local_conf_symlink_rel_path.value}` points to local config dir (as opposed to the global config dir `{ConfField.field_global_conf_dir_rel_path.value}`).\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"The basename of this path is a symlink set to the actual dir with environment-specific config.\n"
            f"If the symlink does not exist yet, its target is set from:\n"
            f"*   either field `{ConfField.field_default_env_dir_rel_path.value}`,\n"
            f"*   or arg `{SyntaxArg.arg_env}` which can also be used to re-set the symlink target to a new path.\n"
            f"See `{EnvState.state_global_conf_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"normally, the resolved local config dir contains all local environment-specific config files.\n"
        )


# noinspection PyPep8Naming
class Node_field_default_env_dir_rel_path(AbstractValueNode[str]):

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.note_text = (
            f"Field `{ConfField.field_default_env_dir_rel_path.value}` is the default path where `{ConfField.field_local_conf_symlink_rel_path.value}` symlink can point to.\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"The path is ignored when the `{ConfField.field_local_conf_symlink_rel_path.value}` symlink already exists.\n"
            f"Arg `{SyntaxArg.arg_env}` overrides this `{ConfField.field_default_env_dir_rel_path.value}` field.\n"
        )


# noinspection PyPep8Naming
class Node_field_required_python_file_abs_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_required_python_file_abs_path.value}` selects `python` version.\n"
                f"The value specifies absolute path to `python` interpreter which is used to create `venv`.\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_venv_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_venv_dir_rel_path.value}` points to the dir where `venv` (`python` virtual environment) is created.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_log_dir_rel_path(AbstractValueNode[str]):

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_log_dir_rel_path.value}` points to the dir with log files created for each script execution.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_tmp_dir_rel_path(AbstractValueNode[str]):


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_tmp_dir_rel_path.value}` points to the dir with temporary files created for some commands.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_cache_dir_rel_path(AbstractValueNode[str]):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_cache_dir_rel_path.value}` points to the dir with cached files created for some commands.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class Node_field_package_driver(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_package_driver.value}` selects a tool to manage packages:\n"
                f'*   specify "{PackageDriverType.driver_pip.name}" to use native `pip`,\n'
                f'*   specify "{PackageDriverType.driver_uv.name}" to use fast `uv`.\n'
                f"{ConfConstGeneral.common_field_global_note}\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


# noinspection PyPep8Naming
class Builder_Node_field_project_descriptors(AbstractConfLeapNodeBuilder):

    def build_dict_node(
        self,
        node_name: str | None,
        node_indent: int,
        orig_data: dict,
        conf_leap: ConfLeap,
        **kwargs,
    ) -> "AbstractDictNode":
        return Node_project_descriptor(
            node_indent=node_indent,
            orig_data=orig_data,
            conf_leap=conf_leap,
            **kwargs,
        )



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Node_field_project_descriptors(AbstractListNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            conf_leap=conf_leap,
            child_builder=Builder_Node_field_project_descriptors(),
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_project_descriptors.value}` lists `python` projects and their installation details.\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                # See: UC_78_58_06_54.no_stray_packages.md:
                f"Note that the `{ConfConstGeneral.name_protoprimer_package}` does not manage package dependencies itself.\n"
                f"Instead, the `{ConfConstGeneral.name_protoprimer_package}` relies on `{ConfConstClient.default_pyproject_toml_basename}` file per `python` project to specify these dependencies.\n"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                f"See `{EnvState.state_project_descriptors_inited.name}` in `{ConfLeap.leap_derived.name}`.\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"
        elif conf_leap == ConfLeap.leap_derived:
            self.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_project_descriptors.value)}\n"


# noinspection PyPep8Naming
class Builder_Node_project_descriptor(AbstractConfLeapNodeBuilder):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.conf_leap: ConfLeap = conf_leap

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:
        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_build_root_dir_rel_path.value,
            node_class=Node_field_build_root_dir_rel_path,
            conf_leap=self.conf_leap,
            **kwargs,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_install_extras.value,
            node_class=Node_field_install_extras,
            conf_leap=self.conf_leap,
            **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class Node_project_descriptor(AbstractDictNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        kwargs.pop("node_name", None)
        kwargs.pop("is_present", None)
        super().__init__(
            node_name=None,
            is_present=True,
            child_builder=Builder_Node_project_descriptor(
                conf_leap=conf_leap,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ),
            **kwargs,
        )


# noinspection PyPep8Naming
class Node_field_build_root_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap in [
            ConfLeap.leap_client,
            ConfLeap.leap_derived,
        ]:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            self.note_text = (
                f"This is similar to specifying the dir of `{ConfConstClient.default_pyproject_toml_basename}` for `pip`:\n"
                f"pip install path/to/project\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
            )


# noinspection PyPep8Naming
class Node_field_install_extras(AbstractListNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            child_builder=ConfigBuilderVisitor(),
            **kwargs,
        )
        if conf_leap in [

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ConfLeap.leap_client,
            ConfLeap.leap_derived,
        ]:
            self.note_text = (
                f"This is similar to specifying a list of `extra_item`-s per `path/to/project` for `pip`:\n"
                f"pip install path/to/project[extra_item_1,extra_item_2,...]\n"
            )


########################################################################################################################
# `ConfLeap.leap_env` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_env(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        **kwargs,
    ) -> None:

        self._create_common_fields(
            dict_node=dict_node,
            conf_leap=ConfLeap.leap_env,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_env(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_env`.
    """

    def __init__(
        self,
        state_local_conf_file_abs_path_inited: str,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_env,
            child_builder=Builder_RootNode_env(),
            **kwargs,
        )
        self.state_local_conf_file_abs_path_inited: str = (
            state_local_conf_file_abs_path_inited
        )
        self.note_text = f"The `{ConfLeap.leap_env.name}` data is loaded from the [{self.state_local_conf_file_abs_path_inited}] file."


########################################################################################################################
# `ConfLeap.leap_derived` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_derived(AbstractConfLeapNodeBuilder):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_derived

        field_node: AbstractConfigNode

        # ===
        # `ConfLeap.leap_input`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_proto_code_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_proto_code_file_abs_path_inited.name, ConfLeap.leap_input)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_primer_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"

        # ===
        # `ConfLeap.leap_primer`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_ref_root_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_ref_root_dir_rel_path.value, ConfLeap.leap_primer)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_global_conf_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_global_conf_dir_rel_path.value, ConfLeap.leap_primer)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_global_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        field_node.note_text = (
            # TODO: It is not derived from just this:
            #       *   dirname is from `field_global_conf_dir_rel_path`
            #       *   basename is from `state_primer_conf_file_abs_path_inited`
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"
        )

        # ===
        # `ConfLeap.leap_client`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_selected_env_dir_rel_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            # TODO: Either default or --env arg:
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_default_env_dir_rel_path.value, ConfLeap.leap_client)}\n"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_conf_symlink_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_local_conf_symlink_rel_path.value, ConfLeap.leap_client)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            # TODO: It is not derived from just this:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            #       *   dirname is from `field_local_conf_symlink_rel_path`
            #       *   basename is from `state_primer_conf_file_abs_path_inited`
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"
        )

        # ===
        # `ConfLeap.leap_env`
        # nothing specific

        # ===
        # `ConfLeap.leap_derived`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_required_python_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_required_python_file_abs_path.value)}\n"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_venv_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_venv_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_log_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_log_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            dict_node=dict_node,
            field_name=EnvState.state_local_tmp_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_tmp_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_cache_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_cache_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_package_driver_inited.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_package_driver.value)}\n"

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_project_descriptors_inited.name,
            node_class=Node_field_project_descriptors,
            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_derived(AbstractConfLeapRootNode):
    """

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    Root node for `ConfLeap.leap_derived`.
    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_derived,
            child_builder=Builder_RootNode_derived(),
            **kwargs,
        )
        self.note_text = (
            f"The `{ConfLeap.leap_derived.name}` data is derived from other data - it is computed by:\n"
            f"*   applying defaults to missing field values\n"
            f"*   combining with other field values\n"
            f"Effectively, this is what ultimately used by the `{ConfConstGeneral.name_protoprimer_package}`.\n"
        )



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

########################################################################################################################


class RunStrategy:
    """
    See related:
    *   `RunMode`
    *   FT_11_27_29_83.run_mode.md
    """

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        raise NotImplementedError()


class ExitCodeReporter(RunStrategy):
    """
    This strategy requires state to return `int` value (as exit code).

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

        No special DAG traversal because nodes traverse their own dependencies.
        But it may not reach all nodes because
        dependencies will be conditionally evaluated by the implementation of those nodes.
        """

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        # NOTE: The `EnvContext.final_state` must return `int` with this strategy:
        exit_code: int = state_node.eval_own_state()
        assert type(exit_code) is int, "`exit_code` must be an `int`"
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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.env_ctx: EnvContext = env_ctx
        self.state_name: str = state_name

        # Ensure no duplicates:
        assert len(parent_states) == len(set(parent_states))

        self.parent_states: list[str] = parent_states

        assert type(state_name) is str

        for state_parent in parent_states:
            assert type(state_parent) is str

    def get_state_name(
        self,
    ) -> str:
        return self.state_name

    def get_parent_states(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> list[str]:
        return self.parent_states

    def eval_parent_state(
        self,
        parent_state: str,
    ) -> typing.Any:
        if parent_state not in self.parent_states:
            raise AssertionError(
                f"parent_state[{parent_state}] is not parent of [{self.state_name}]"
            )
        return self.env_ctx.state_graph.eval_state(parent_state)

    def eval_own_state(
        self,
    ) -> ValueType:
        return self._eval_own_state()

    def _eval_own_state(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> ValueType:
        raise NotImplementedError()


class AbstractCachingStateNode(StateNode[ValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
        auto_bootstrap_parents: bool = True,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=parent_states,
            state_name=state_name,
        )
        self.auto_bootstrap_parents: bool = auto_bootstrap_parents
        self.is_cached: bool = False

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self.cached_value: ValueType | None = None

    def _eval_own_state(
        self,
    ) -> ValueType:
        if not self.is_cached:

            if self.auto_bootstrap_parents:
                # Bootstrap all dependencies:
                for state_name in self.parent_states:
                    self.eval_parent_state(state_name)

            # See FT_30_24_95_65.state_idempotency.md
            self.cached_value = self._eval_state_once()
            logger.debug(
                f"state [{self.state_name}] evaluated value [{self.cached_value}]"
            )
            self.is_cached = True

        return self.cached_value

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def _eval_state_once(
        self,
    ) -> ValueType:
        raise NotImplementedError()


class AbstractOverriddenFieldCachingStateNode(AbstractCachingStateNode[ValueType]):
    """
    Base class which overrides field values from `ConfLeap.leap_client` and `ConfLeap.leap_env`.

    See: FT_00_22_19_59.derived_config.md
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
        auto_bootstrap_parents: bool = True,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=parent_states,
            state_name=state_name,
            auto_bootstrap_parents=auto_bootstrap_parents,
        )
        # FT_00_22_19_59.derived_config.md: requires values from both files:
        assert (
            EnvState.state_client_conf_file_data_loaded.name in parent_states
            and EnvState.state_env_conf_file_data_loaded.name in parent_states
        )

    def _get_overridden_value_or_default(
        self,
        field_name: str,
        default_field_value: DataValueType,
    ) -> DataValueType:
        """
        Implements config overrides: FT_23_37_64_44.conf_dst.md

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        """

        state_client_conf_file_data_loaded: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data_loaded.name
        )
        state_env_conf_file_data_loaded: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data_loaded.name
        )
        field_value: DataValueType
        if field_name in state_env_conf_file_data_loaded:
            field_value = state_env_conf_file_data_loaded[field_name]
        else:
            field_value = state_client_conf_file_data_loaded.get(
                field_name,
                default_field_value,
            )
        return field_value


########################################################################################################################

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



# noinspection PyPep8Naming
class Bootstrapper_state_input_stderr_log_level_var_loaded(
    AbstractCachingStateNode[int]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name,
                EnvState.state_input_stderr_log_level_var_loaded.name,
            ),
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def _eval_state_once(
        self,
    ) -> ValueType:
        default_stderr_level: str = os.getenv(
            EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value,
            ConfConstInput.default_PROTOPRIMER_STDERR_LOG_LEVEL,
        )
        if str.isdigit(default_stderr_level):
            state_input_stderr_log_level_var_loaded: int = int(default_stderr_level)
            assert state_input_stderr_log_level_var_loaded >= 0
        else:
            state_input_stderr_log_level_var_loaded: int = getattr(
                logging,
                default_stderr_level,
            )
        return state_input_stderr_log_level_var_loaded


# noinspection PyPep8Naming

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class Bootstrapper_state_input_do_install_var_loaded(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name,
                EnvState.state_input_do_install_var_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_do_install_var_loaded: bool = str_to_bool(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            os.getenv(
                EnvVar.var_PROTOPRIMER_DO_INSTALL.value,
                ConfConstInput.default_PROTOPRIMER_DO_INSTALL,
            )
        )
        return state_input_do_install_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_default_stderr_log_handler_configured(
    AbstractCachingStateNode[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            parent_states=[
                EnvState.state_input_stderr_log_level_var_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_default_stderr_log_handler_configured.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_var_loaded.name
        )
        assert state_input_stderr_log_level_var_loaded >= 0


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        stderr_handler: logging.Handler = configure_stderr_log_handler(
            state_input_stderr_log_level_var_loaded,
        )

        return stderr_handler


# noinspection PyPep8Naming
class Bootstrapper_state_args_parsed(AbstractCachingStateNode[argparse.Namespace]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_args_parsed.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed: argparse.Namespace = parse_args()
        return state_args_parsed


# noinspection PyPep8Naming
class Bootstrapper_state_input_stderr_log_level_eval_finalized(
    AbstractCachingStateNode[int]
):
    """
    There is a narrow window between the default log level is set and this state is evaluated.
    To control the default log level, see `EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL`.
    """


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_var_loaded.name,
                EnvState.state_default_stderr_log_handler_configured.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_stderr_log_level_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> ValueType:

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_var_loaded.name,
        )

        state_default_stderr_logger_configured: logging.Handler = (
            self.eval_parent_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        parsed_args = self.eval_parent_state(EnvState.state_args_parsed.name)
        stderr_log_level_quiet_count: int = getattr(
            parsed_args,
            SyntaxArg.dest_quiet,
        )
        stderr_log_level_verbose_count: int = getattr(
            parsed_args,
            SyntaxArg.dest_verbose,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

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

            relative_log_level = 10 * (
                stderr_log_level_quiet_count - stderr_log_level_verbose_count
            )

            stderr_log_level_eval_finalized = base_log_level + relative_log_level

            if stderr_log_level_eval_finalized < logging.NOTSET:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                stderr_log_level_eval_finalized = logging.NOTSET

        state_default_stderr_logger_configured.setLevel(stderr_log_level_eval_finalized)
        assert isinstance(
            state_default_stderr_logger_configured.formatter,
            StderrLogFormatter,
        )
        state_default_stderr_logger_configured.formatter.set_verbosity_level(
            stderr_log_level_eval_finalized
        )

        # Set default log level for subsequent invocations:
        level_var_value: str = logging.getLevelName(stderr_log_level_eval_finalized)
        assert isinstance(level_var_value, str)
        if " " in level_var_value:
            # Due to some hacks in the `python` `logging` library,
            # it may return non-existing level names - use number instead:
            level_var_value = str(stderr_log_level_eval_finalized)
        os.environ[EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL.value] = level_var_value


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        # Remove stack trace for levels >= WARNING (it will only print the exception itself):
        if stderr_log_level_eval_finalized >= logging.WARNING:
            # Avoid changing that in tests - it changes the global state and causes many tests to fail unexpectedly:
            if not is_test_run():
                sys.tracebacklimit = 0

        return stderr_log_level_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_run_mode_arg_loaded(AbstractCachingStateNode[RunMode]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_run_mode_arg_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )
        state_input_run_mode_arg_loaded: RunMode = RunMode(
            getattr(
                state_args_parsed,
                ParsedArg.name_run_mode.value,
            )
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return state_input_run_mode_arg_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_input_final_state_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_input_final_state_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_args_parsed = self.eval_parent_state(EnvState.state_args_parsed.name)
        state_input_final_state_eval_finalized: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_final_state.value,
            # NOTE: The value is only set for `RunMode.mode_prime`, otherwise, this default is used:
            None,
        )

        if state_input_final_state_eval_finalized is None:
            # TODO: Fix duplicated logs: try default bootstrap - this line is printed repeatedly.
            #       Pass the arg after the start to subsequent `switch_python` calls.
            logger.info(
                f"selecting `final_state`[{self.env_ctx.final_state}] as no `{SyntaxArg.arg_final_state}` specified"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            )
            state_input_final_state_eval_finalized = self.env_ctx.final_state

        return state_input_final_state_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_run_mode_executed(AbstractCachingStateNode[bool]):
    """
    This is a special node - it traverses ALL nodes.

    BUT: It does not depend on ALL nodes - instead, it uses a run mode strategy implementation.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded.name,
                EnvState.state_input_final_state_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_run_mode_executed.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_stderr_log_level_eval_finalized = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )
        assert state_input_stderr_log_level_eval_finalized >= 0

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        state_input_final_state_eval_finalized: str = self.eval_parent_state(
            EnvState.state_input_final_state_eval_finalized.name
        )

        state_input_run_mode_arg_loaded: RunMode = self.eval_parent_state(
            EnvState.state_input_run_mode_arg_loaded.name
        )

        state_node: StateNode = self.env_ctx.state_graph.state_nodes[
            state_input_final_state_eval_finalized
        ]

        selected_strategy: RunStrategy
        if state_input_run_mode_arg_loaded is None:
            raise ValueError(f"run mode is not defined")
        elif state_input_run_mode_arg_loaded == RunMode.mode_prime:
            selected_strategy = ExitCodeReporter(self.env_ctx)
        elif state_input_run_mode_arg_loaded == RunMode.mode_upgrade:
            selected_strategy = ExitCodeReporter(self.env_ctx)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        elif state_input_run_mode_arg_loaded == RunMode.mode_config:
            selected_strategy = ExitCodeReporter(self.env_ctx)
            state_node = self.env_ctx.state_graph.state_nodes[
                EnvState.state_effective_config_data_printed.name
            ]
        else:
            raise ValueError(
                f"cannot handle run mode [{state_input_run_mode_arg_loaded}]"
            )

        selected_strategy.execute_strategy(state_node)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_input_py_exec_var_loaded(
    AbstractCachingStateNode[PythonExecutable]
):


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_py_exec_var_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        return PythonExecutable[

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_input_start_id_var_loaded(AbstractCachingStateNode[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_input_start_id_var_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        return os.getenv(
            EnvVar.var_PROTOPRIMER_START_ID.value,
            get_default_start_id(),
        )


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_code_file_abs_path_var_loaded(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_proto_code_file_abs_path_var_loaded: str | None = os.getenv(
            EnvVar.var_PROTOPRIMER_PROTO_CODE.value,
            None,
        )
        if state_input_proto_code_file_abs_path_var_loaded is not None:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            if not os.path.isabs(state_input_proto_code_file_abs_path_var_loaded):
                raise AssertionError(
                    f"`{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}` must specify absolute path"
                )
            if not os.path.isfile(state_input_proto_code_file_abs_path_var_loaded):
                raise AssertionError(
                    f"file {state_input_proto_code_file_abs_path_var_loaded} is not available"
                )
        return state_input_proto_code_file_abs_path_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_arbitrary_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Implements UC_90_98_17_93.run_under_venv.md.
    """

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_start_id_var_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_arbitrary_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_input_py_exec_var_loaded.name
        )

        state_input_start_id_var_loaded: str = self.eval_parent_state(
            EnvState.state_input_start_id_var_loaded.name
        )

        if (
            state_input_py_exec_var_loaded.value
            == PythonExecutable.py_exec_unknown.value
        ):
            log_python_context(logging.DEBUG)

            # UC_90_98_17_93.run_under_venv.md
            # Switch out of the current `venv` -
            # it might be a wrong one,
            # and even if it is the right one,
            # child states require out of `venv` execution.

            cleaned_env = os.environ.copy()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


            orig_venv_abs_path = cleaned_env.pop(
                ConfConstInput.ext_env_var_VIRTUAL_ENV, None
            )
            orig_PYTHONPATH_value = cleaned_env.pop(
                ConfConstInput.ext_env_var_PYTHONPATH, None
            )
            orig_PATH_value: str = cleaned_env.get(ConfConstInput.ext_env_var_PATH, "")

            if orig_venv_abs_path is not None:
                # Remove `venv/bin` dir from the `PATH` env var:
                venv_bin_abs_path: str = os.path.join(orig_venv_abs_path, "bin")
                PATH_parts: list[str] = orig_PATH_value.split(os.pathsep)
                cleaned_path_parts = [p for p in PATH_parts if p != venv_bin_abs_path]
                cleaned_env[ConfConstInput.ext_env_var_PATH] = os.pathsep.join(
                    cleaned_path_parts
                )

            path_to_curr_python = get_path_to_curr_python()
            path_to_next_python = get_path_to_base_python()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=path_to_curr_python,
                next_py_exec=PythonExecutable.py_exec_arbitrary,
                next_python_path=path_to_next_python,
                start_id=state_input_start_id_var_loaded,
                proto_code_abs_file_path=None,
                required_environ=cleaned_env,
            )

        return state_input_py_exec_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_proto_code_file_abs_path_inited(AbstractCachingStateNode[str]):
    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_code_file_abs_path_var_loaded.name,
                EnvState.state_py_exec_arbitrary_reached.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_proto_code_file_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_arbitrary_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_arbitrary_reached.name
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_input_proto_code_file_abs_path_var_loaded: str | None = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_var_loaded.name
            )
        )

        state_proto_code_file_abs_path_inited: str
        if state_py_exec_arbitrary_reached.value >= PythonExecutable.py_exec_venv.value:
            if state_input_proto_code_file_abs_path_var_loaded is None:
                raise AssertionError(
                    f"`{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}` is not specified at `{EnvState.state_py_exec_arbitrary_reached.name}` [{state_py_exec_arbitrary_reached}]"
                )
            # rely on the path given in env var:
            state_proto_code_file_abs_path_inited = (
                state_input_proto_code_file_abs_path_var_loaded
            )
        else:
            log_python_context()
            if os.environ.get(EnvVar.var_PROTOPRIMER_TEST_MODE.value, None) is None:
                assert not is_venv()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                state_proto_code_file_abs_path_inited = os.path.abspath(__file__)
            else:
                # `EnvVar.var_PROTOPRIMER_TEST_MODE`: rely on the path given in env var:
                assert state_input_proto_code_file_abs_path_var_loaded is not None
                state_proto_code_file_abs_path_inited = (
                    state_input_proto_code_file_abs_path_var_loaded
                )

        assert os.path.isabs(state_proto_code_file_abs_path_inited)
        return state_proto_code_file_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_primer_conf_file_abs_path_inited(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_proto_code_file_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_conf_file_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        """
        Select the conf file name from a list of candidate basenames (whichever is found first).
        """
        state_proto_code_file_abs_path_inited = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_proto_code_file_abs_path_inited.name
        )

        proto_code_dir_abs_path: str = os.path.dirname(
            state_proto_code_file_abs_path_inited
        )

        candidate_basenames = []
        conf_basename_from_env = os.environ.get(
            EnvVar.var_PROTOPRIMER_CONF_BASENAME.value, None
        )
        if conf_basename_from_env is not None:
            candidate_basenames.append(conf_basename_from_env)

        candidate_basenames.extend(
            [
                f"{pathlib.Path(sys.argv[0]).stem}.{ConfConstInput.conf_file_ext}",
                f"{pathlib.Path(state_proto_code_file_abs_path_inited).stem}.{ConfConstInput.conf_file_ext}",
                ConfConstInput.default_file_basename_conf_primer,
            ]

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

        for candidate_basename in candidate_basenames:
            candidate_conf_file_abs_path = os.path.join(
                proto_code_dir_abs_path,
                candidate_basename,
            )
            logger.debug(f"candidate conf file name: {candidate_conf_file_abs_path}")
            if os.path.exists(candidate_conf_file_abs_path):
                return candidate_conf_file_abs_path

        # Use `ConfConstInput.default_file_basename_conf_primer` even if not found
        # because it names conf files for other `ConfLeap.*`:
        return os.path.join(
            proto_code_dir_abs_path,
            ConfConstInput.default_file_basename_conf_primer,
        )


# noinspection PyPep8Naming

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class Bootstrapper_state_primer_conf_file_data_loaded(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_primer_conf_file_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_conf_file_data_loaded.name,
            ),

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )
        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_primer_conf_file_abs_path_inited.name
        )

        file_data: dict
        if os.path.exists(state_primer_conf_file_abs_path_inited):
            file_data = read_json_file(state_primer_conf_file_abs_path_inited)
            verify_conf_file_data_contains_known_fields_only(
                state_primer_conf_file_abs_path_inited,
                file_data,
            )
        else:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            warn_on_missing_conf_file(state_primer_conf_file_abs_path_inited)
            file_data = {}

        if can_print_effective_config(self):

            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(
                EnvState.state_input_stderr_log_level_eval_finalized.name
            )
            is_quiet: bool = state_input_stderr_log_level_eval_finalized > logging.INFO

            if is_quiet:
                # Print this note early
                logging.warning(
                    f"Showing plain config data - use option `-v` (`--verbose`) to annotate it with descriptions."
                )

            # Print `ConfLeap.leap_input` data together:
            # ===
            # `ConfLeap.leap_input`:
            conf_input = RootNode_input(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                node_indent=0,
                orig_data={
                    EnvState.state_proto_code_file_abs_path_inited.name: state_proto_code_file_abs_path_inited,
                    EnvState.state_primer_conf_file_abs_path_inited.name: state_primer_conf_file_abs_path_inited,
                },
            )
            print(RenderConfigVisitor(is_quiet=is_quiet).render_node(conf_input))

            # ===
            # `ConfLeap.leap_primer`:
            conf_primer = RootNode_primer(
                node_indent=0,
                orig_data=file_data,
                state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor(is_quiet=is_quiet).render_node(conf_primer))

        return file_data



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_ref_root_dir_abs_path_inited(AbstractCachingStateNode[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_primer_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_ref_root_dir_abs_path_inited.name,
            ),
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_proto_code_file_abs_path_inited = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

        proto_code_dir_abs_path: str = os.path.dirname(
            state_proto_code_file_abs_path_inited
        )

        state_primer_conf_file_data_loaded: dict = self.eval_parent_state(
            EnvState.state_primer_conf_file_data_loaded.name
        )

        field_client_dir_rel_path: str | None = state_primer_conf_file_data_loaded.get(
            ConfField.field_ref_root_dir_rel_path.value,
            None,
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_ref_root_dir_abs_path_inited: str
        if field_client_dir_rel_path is None:
            logger.warning(
                f"Field `{ConfField.field_ref_root_dir_rel_path.value}` is [{field_client_dir_rel_path}] - use [{RunMode.mode_config.value}] sub-command for description."
            )
            state_ref_root_dir_abs_path_inited = proto_code_dir_abs_path
        else:
            state_ref_root_dir_abs_path_inited = os.path.join(
                proto_code_dir_abs_path,
                field_client_dir_rel_path,
            )

        state_ref_root_dir_abs_path_inited = os.path.normpath(
            state_ref_root_dir_abs_path_inited
        )

        assert os.path.isabs(state_ref_root_dir_abs_path_inited)
        return state_ref_root_dir_abs_path_inited



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_global_conf_dir_abs_path_inited(AbstractCachingStateNode[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_conf_file_data_loaded.name,
                EnvState.state_ref_root_dir_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_global_conf_dir_abs_path_inited.name,
            ),
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )

        state_primer_conf_file_data_loaded: dict = self.eval_parent_state(
            EnvState.state_primer_conf_file_data_loaded.name
        )

        field_client_config_dir_rel_path: str | None = (
            state_primer_conf_file_data_loaded.get(
                ConfField.field_global_conf_dir_rel_path.value,
                None,
            )
        )

        state_global_conf_dir_abs_path_inited: str | None

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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
class Bootstrapper_state_global_conf_file_abs_path_inited(
    AbstractCachingStateNode[str]
):

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_conf_file_abs_path_inited.name,
                EnvState.state_global_conf_dir_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_global_conf_file_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_primer_conf_file_abs_path_inited.name
        )
        conf_file_base_name = os.path.basename(state_primer_conf_file_abs_path_inited)

        state_global_conf_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_global_conf_dir_abs_path_inited.name
        )

        state_global_conf_file_abs_path_inited: str = os.path.join(
            state_global_conf_dir_abs_path_inited,
            conf_file_base_name,
        )

        return state_global_conf_file_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_data_loaded(AbstractCachingStateNode[dict]):


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_global_conf_file_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_conf_file_data_loaded.name,
            ),
        )

    def _eval_state_once(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
    ) -> ValueType:

        state_global_conf_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_global_conf_file_abs_path_inited.name
        )

        file_data: dict
        if os.path.exists(state_global_conf_file_abs_path_inited):
            file_data = read_json_file(state_global_conf_file_abs_path_inited)
            verify_conf_file_data_contains_known_fields_only(
                state_global_conf_file_abs_path_inited,
                file_data,
            )
        else:
            warn_on_missing_conf_file(state_global_conf_file_abs_path_inited)
            file_data = {}

        if can_print_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_input_stderr_log_level_eval_finalized.name
            )
            is_quiet: bool = state_input_stderr_log_level_eval_finalized > logging.INFO

            conf_client = RootNode_client(
                node_indent=0,
                orig_data=file_data,
                state_global_conf_file_abs_path_inited=state_global_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor(is_quiet=is_quiet).render_node(conf_client))

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_selected_env_dir_rel_path_inited(
    AbstractCachingStateNode[str]
):

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_selected_env_dir_rel_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        client_local_env_dir_any_path: str | None = (
            self._select_client_local_env_dir_any_path()
        )
        if client_local_env_dir_any_path is None:
            return None

        client_local_env_dir_abs_path: str = self._select_client_local_env_dir_abs_path(
            client_local_env_dir_any_path
        )

        if not os.path.isdir(client_local_env_dir_abs_path):
            raise AssertionError(
                f"`{PathName.path_selected_env.value}` [{client_local_env_dir_abs_path}] must be a dir."
            )

        state_ref_root_dir_abs_path_inited = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )
        if not is_sub_path(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            client_local_env_dir_abs_path,
            state_ref_root_dir_abs_path_inited,
        ):
            raise AssertionError(
                f"`{PathName.path_selected_env.value}` [{client_local_env_dir_abs_path}] is not under `{EnvState.state_ref_root_dir_abs_path_inited.name}` [{state_ref_root_dir_abs_path_inited}]."
            )

        state_selected_env_dir_rel_path_inited: str = os.path.normpath(
            rel_path(
                client_local_env_dir_abs_path,
                state_ref_root_dir_abs_path_inited,
            )
        )

        assert ".." not in pathlib.Path(state_selected_env_dir_rel_path_inited).parts

        return state_selected_env_dir_rel_path_inited

    def _select_client_local_env_dir_any_path(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> str | None:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )
        env_conf_dir_any_path: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_selected_env_dir.value,
            # NOTE: The value is only set for `RunMode.mode_prime`, otherwise, this default is used:
            None,
        )
        if env_conf_dir_any_path is None:
            # Use the default env configured:
            state_client_conf_file_data_loaded: dict = self.eval_parent_state(
                EnvState.state_client_conf_file_data_loaded.name
            )
            field_default_env_dir_rel_path: str | None = (
                state_client_conf_file_data_loaded.get(
                    ConfField.field_default_env_dir_rel_path.value,
                    None,
                )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            )
            if field_default_env_dir_rel_path is None:
                logger.warning(
                    f"Field `{ConfField.field_default_env_dir_rel_path.value}` is [{field_default_env_dir_rel_path}] - use [{RunMode.mode_config.value}] sub-command for description."
                )
                return None
            if os.path.isabs(field_default_env_dir_rel_path):
                raise AssertionError(
                    f"Field `{ConfField.field_default_env_dir_rel_path.value}` must be a relative path."
                )
            return field_default_env_dir_rel_path
        else:
            return env_conf_dir_any_path

    def _select_client_local_env_dir_abs_path(
        self,
        client_local_env_dir_any_path: str,
    ) -> str:
        """
        Determine the target dir abs path by trying the path it is relative to.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        *   If the input path is already absolute, return as is.
        *   Use ref root as the base first.
        *   Use curr dir as the base last.
        """

        if os.path.isabs(client_local_env_dir_any_path):
            return client_local_env_dir_any_path
        else:
            state_ref_root_dir_abs_path_inited = self.eval_parent_state(
                EnvState.state_ref_root_dir_abs_path_inited.name
            )
            # ===
            abs_path = os.path.join(
                state_ref_root_dir_abs_path_inited,
                client_local_env_dir_any_path,
            )
            if os.path.isdir(abs_path):
                return abs_path
            # ===

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            abs_path = os.path.join(
                os.getcwd(),
                client_local_env_dir_any_path,
            )
            if os.path.isdir(abs_path):
                return abs_path
            # ===
            raise AssertionError(
                f"`{PathName.path_selected_env.value}` [{client_local_env_dir_any_path}] is relative to neither `{PathName.path_ref_root.value}` [{state_ref_root_dir_abs_path_inited}] nor curr dir [{os.getcwd()}]."
            )


# noinspection PyPep8Naming
class Bootstrapper_state_local_conf_symlink_abs_path_inited(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_selected_env_dir_rel_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_conf_symlink_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_ref_root_dir_abs_path_inited.name
        )

        state_selected_env_dir_rel_path_inited: str | None = self.eval_parent_state(
            EnvState.state_selected_env_dir_rel_path_inited.name
        )

        if state_selected_env_dir_rel_path_inited is None:
            # No symlink target => no `conf_leap` => use `client_conf`:
            return state_ref_root_dir_abs_path_inited

        state_client_conf_file_data_loaded: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data_loaded.name
        )
        client_env_conf_link_name_dir_rel_path: str | None = (
            state_client_conf_file_data_loaded.get(
                ConfField.field_local_conf_symlink_rel_path.value,
                None,
            )
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        # Convert to absolute:
        state_local_conf_symlink_abs_path_inited: str
        if client_env_conf_link_name_dir_rel_path is None:
            state_local_conf_symlink_abs_path_inited = (
                state_ref_root_dir_abs_path_inited
            )
        else:
            # TODO: Handle via AssertionError:
            assert not os.path.isabs(client_env_conf_link_name_dir_rel_path)
            state_local_conf_symlink_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                client_env_conf_link_name_dir_rel_path,
            )

        if os.path.exists(state_local_conf_symlink_abs_path_inited):
            if os.path.islink(state_local_conf_symlink_abs_path_inited):
                if os.path.isdir(state_local_conf_symlink_abs_path_inited):
                    # Compare the existing link target and the configured one:
                    conf_dir_path = os.path.normpath(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                        os.readlink(state_local_conf_symlink_abs_path_inited)
                    )
                    if state_selected_env_dir_rel_path_inited != conf_dir_path:
                        raise AssertionError(
                            f"The symlink [{state_local_conf_symlink_abs_path_inited}] target [{conf_dir_path}] is not the same as the provided target [{state_selected_env_dir_rel_path_inited}]."
                        )
                else:
                    raise AssertionError(
                        f"The symlink [{state_local_conf_symlink_abs_path_inited}] target [{state_local_conf_symlink_abs_path_inited}] is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The entry [{state_local_conf_symlink_abs_path_inited}] is not a symlink.",
                )
        else:
            os.symlink(
                os.path.normpath(state_selected_env_dir_rel_path_inited),
                state_local_conf_symlink_abs_path_inited,
            )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return state_local_conf_symlink_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_local_conf_file_abs_path_inited(AbstractCachingStateNode[str]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_conf_file_abs_path_inited.name,
                EnvState.state_local_conf_symlink_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_conf_file_abs_path_inited.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_primer_conf_file_abs_path_inited.name
        )
        conf_file_base_name = os.path.basename(state_primer_conf_file_abs_path_inited)

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        state_local_conf_file_abs_path_inited = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            conf_file_base_name,
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        return state_local_conf_file_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_data_loaded(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_local_conf_file_abs_path_inited.name,
            ],

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            state_name=if_none(
                state_name,
                EnvState.state_env_conf_file_data_loaded.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_local_conf_file_abs_path_inited = self.eval_parent_state(
            EnvState.state_local_conf_file_abs_path_inited.name
        )

        file_data: dict
        if os.path.exists(state_local_conf_file_abs_path_inited):
            file_data = read_json_file(state_local_conf_file_abs_path_inited)
            verify_conf_file_data_contains_known_fields_only(
                state_local_conf_file_abs_path_inited,
                file_data,
            )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        else:
            warn_on_missing_conf_file(state_local_conf_file_abs_path_inited)
            file_data = {}

        if can_print_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(
                EnvState.state_input_stderr_log_level_eval_finalized.name
            )
            is_quiet: bool = state_input_stderr_log_level_eval_finalized > logging.INFO

            conf_env = RootNode_env(
                node_indent=0,
                orig_data=file_data,
                state_local_conf_file_abs_path_inited=state_local_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor(is_quiet=is_quiet).render_node(conf_env))

        return file_data



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_required_python_file_abs_path_inited(
    AbstractOverriddenFieldCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_required_python_file_abs_path_inited.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_required_python_file_abs_path_inited: str = (
            self._get_overridden_value_or_default(
                ConfField.field_required_python_file_abs_path.value,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.default_file_abs_path_python,
            )
        )

        if not os.path.isabs(state_required_python_file_abs_path_inited):
            # TODO: Really? Do we really want to allow specifying `python` using rel path?
            #       Regardless, even if rel path, the `field_required_python_file_abs_path.value` should remove `abs` from the name then.
            state_required_python_file_abs_path_inited = os.path.join(
                self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                    EnvState.state_ref_root_dir_abs_path_inited.name
                ),
                state_required_python_file_abs_path_inited,
            )

        return state_required_python_file_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_local_venv_dir_abs_path_inited(
    AbstractOverriddenFieldCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_venv_dir_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_local_venv_dir_abs_path_inited: str = (
            self._get_overridden_value_or_default(
                ConfField.field_local_venv_dir_rel_path.value,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfConstEnv.default_dir_rel_path_venv,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            )
        )

        if not os.path.isabs(state_local_venv_dir_abs_path_inited):
            state_ref_root_dir_abs_path_inited = self.eval_parent_state(
                EnvState.state_ref_root_dir_abs_path_inited.name
            )
            state_local_venv_dir_abs_path_inited = os.path.join(
                state_ref_root_dir_abs_path_inited,
                state_local_venv_dir_abs_path_inited,
            )

        assert os.path.isabs(state_local_venv_dir_abs_path_inited)
        return state_local_venv_dir_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_local_log_dir_abs_path_inited(
    AbstractOverriddenFieldCachingStateNode[str]
):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_log_dir_abs_path_inited.name,
            ),
        )

    def _eval_state_once(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
    ) -> ValueType:

        field_local_log_dir_rel_path: str = self._get_overridden_value_or_default(
            ConfField.field_local_log_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_log,
        )

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )

        state_local_log_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_log_dir_rel_path,
        )
        state_local_log_dir_abs_path_inited = os.path.normpath(
            state_local_log_dir_abs_path_inited
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        assert os.path.isabs(state_local_log_dir_abs_path_inited)
        return state_local_log_dir_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_local_tmp_dir_abs_path_inited(
    AbstractOverriddenFieldCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_tmp_dir_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        field_local_tmp_dir_rel_path: str = self._get_overridden_value_or_default(
            ConfField.field_local_tmp_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_tmp,
        )

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_local_tmp_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_tmp_dir_rel_path,
        )
        state_local_tmp_dir_abs_path_inited = os.path.normpath(
            state_local_tmp_dir_abs_path_inited
        )

        assert os.path.isabs(state_local_tmp_dir_abs_path_inited)
        return state_local_tmp_dir_abs_path_inited


# noinspection PyPep8Naming
class Bootstrapper_state_local_cache_dir_abs_path_inited(
    AbstractOverriddenFieldCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_local_cache_dir_abs_path_inited.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        field_local_cache_dir_rel_path: str = self._get_overridden_value_or_default(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ConfField.field_local_cache_dir_rel_path.value,
            ConfConstEnv.default_dir_rel_path_cache,
        )

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )

        state_local_cache_dir_abs_path_inited = os.path.join(
            state_ref_root_dir_abs_path_inited,
            field_local_cache_dir_rel_path,
        )
        state_local_cache_dir_abs_path_inited = os.path.normpath(
            state_local_cache_dir_abs_path_inited
        )

        assert os.path.isabs(state_local_cache_dir_abs_path_inited)
        return state_local_cache_dir_abs_path_inited



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_package_driver_inited(
    AbstractOverriddenFieldCachingStateNode[PackageDriverType]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_package_driver_inited.name,
            ),

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        field_package_driver: PackageDriverType
        if os.environ.get(EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value, None) is None:
            field_package_driver = PackageDriverType[
                self._get_overridden_value_or_default(
                    ConfField.field_package_driver.value,
                    ConfConstEnv.default_package_driver,
                )
            ]
        else:
            field_package_driver = PackageDriverType[
                os.environ.get(EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER.value)
            ]

        return field_package_driver


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


# noinspection PyPep8Naming
class Bootstrapper_state_project_descriptors_inited(
    AbstractOverriddenFieldCachingStateNode[list]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_file_data_loaded.name,
                EnvState.state_env_conf_file_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_project_descriptors_inited.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        project_descriptors: list = self._get_overridden_value_or_default(
            ConfField.field_project_descriptors.value,
            ConfConstEnv.default_project_descriptors,
        )

        return project_descriptors


# noinspection PyPep8Naming
class Bootstrapper_state_derived_conf_data_loaded(AbstractCachingStateNode[dict]):
    """
    Implements: FT_00_22_19_59.derived_config.md
    """

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_local_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_env`
            # nothing specific
            # ===
            # `ConfLeap.leap_derived`
            EnvState.state_required_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_package_driver_inited.name,
            EnvState.state_project_descriptors_inited.name,
        ]

        # TODO: Is this needed given the list of dependencies in `derived_data_env_states`?
        parent_states = [
            EnvState.state_input_run_mode_arg_loaded.name,
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_primer_conf_file_data_loaded.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_client_conf_file_data_loaded.name,
            EnvState.state_env_conf_file_data_loaded.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            *self.derived_data_env_states,
        ]

        # The list parent states sorted by their definition order in `EnvState`:
        parent_states.sort(
            key=lambda parent_state: [enum_item.name for enum_item in EnvState].index(
                parent_state
            ),
        )

        super().__init__(
            env_ctx=env_ctx,
            parent_states=parent_states,
            state_name=if_none(
                state_name,
                EnvState.state_derived_conf_data_loaded.name,
            ),

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        config_data_derived = {}
        for derived_data_env_state in self.derived_data_env_states:
            evaluated_value = self.eval_parent_state(derived_data_env_state)
            if isinstance(evaluated_value, enum.Enum):
                config_data_derived[derived_data_env_state] = evaluated_value.name
            else:
                config_data_derived[derived_data_env_state] = evaluated_value

        if can_print_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(
                EnvState.state_input_stderr_log_level_eval_finalized.name
            )
            is_quiet: bool = state_input_stderr_log_level_eval_finalized > logging.INFO


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            conf_derived = RootNode_derived(
                node_indent=0,
                orig_data=config_data_derived,
            )
            print(RenderConfigVisitor(is_quiet=is_quiet).render_node(conf_derived))

        return config_data_derived


# noinspection PyPep8Naming
class Bootstrapper_state_effective_config_data_printed(AbstractCachingStateNode[int]):
    """
    Implements: FT_19_44_42_19.effective_config.md
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_derived_conf_data_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_effective_config_data_printed.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        # Nothing to do:
        # If we reach this state,
        # then, transitively, effective configs for all `ConfLeap.*` has been printed.
        return 0



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

# noinspection PyPep8Naming
class Bootstrapper_state_default_file_log_handler_configured(
    AbstractCachingStateNode[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_stderr_log_level_eval_finalized.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_local_log_dir_abs_path_inited.name,
            ],
            state_name=if_none(
                state_name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_default_file_log_handler_configured.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_start_id_var_loaded: str = self.eval_parent_state(
            EnvState.state_input_start_id_var_loaded.name
        )

        state_local_log_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_log_dir_abs_path_inited.name
        )

        state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_eval_finalized.name
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        script_path = sys.argv[0]
        script_name = os.path.basename(script_path)

        file_handler = configure_file_log_handler(
            script_name,
            state_input_start_id_var_loaded,
            state_input_stderr_log_level_eval_finalized,
            state_local_log_dir_abs_path_inited,
        )

        return file_handler


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_required_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Recursively runs this script inside the `python` interpreter required by the client.


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    The `python` interpreter required by the client is saved into `field_required_python_file_abs_path`.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_local_conf_file_abs_path_inited.name,
                EnvState.state_required_python_file_abs_path_inited.name,
                EnvState.state_local_venv_dir_abs_path_inited.name,
                EnvState.state_local_tmp_dir_abs_path_inited.name,
                EnvState.state_default_file_log_handler_configured.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_required_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_required_reached: PythonExecutable

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_default_file_log_handler_configured = self.eval_parent_state(
            EnvState.state_default_file_log_handler_configured.name
        )

        # TODO: Unused, but plugged in to form complete DAG: consider adding intermediate state to plug it in:
        state_local_tmp_dir_abs_path_inited = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_local_tmp_dir_abs_path_inited.name
        )

        state_input_start_id_var_loaded: str = self.eval_parent_state(
            EnvState.state_input_start_id_var_loaded.name
        )

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

        state_required_python_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_required_python_file_abs_path_inited.name
        )
        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_venv_dir_abs_path_inited.name

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )

        assert not is_sub_path(
            state_required_python_file_abs_path_inited,
            state_local_venv_dir_abs_path_inited,
        ), f"Configured `python` [{state_required_python_file_abs_path_inited}] must be outside of configured `venv` [{state_local_venv_dir_abs_path_inited}]"

        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        # Do not do anything if beyond `PythonExecutable.py_exec_required`:
        if state_input_py_exec_var_loaded >= PythonExecutable.py_exec_required:
            return state_input_py_exec_var_loaded

        assert not is_sub_path(
            path_to_curr_python,
            state_local_venv_dir_abs_path_inited,
        ), f"Current `python` [{path_to_curr_python}] must be outside of the `venv` [{state_local_venv_dir_abs_path_inited}]."

        if path_to_curr_python != state_required_python_file_abs_path_inited:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_arbitrary
            state_py_exec_required_reached = PythonExecutable.py_exec_arbitrary
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=path_to_curr_python,
                next_py_exec=PythonExecutable.py_exec_required,
                next_python_path=state_required_python_file_abs_path_inited,
                start_id=state_input_start_id_var_loaded,
                proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
            )
        else:
            assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_required
            state_py_exec_required_reached = PythonExecutable.py_exec_required

        return state_py_exec_required_reached


# noinspection PyPep8Naming
class Bootstrapper_state_reinstall_triggered(AbstractCachingStateNode[bool]):
    """

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    Removes current `venv` dir and `constraints.txt` file (to trigger their re-creation subsequently).
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_local_conf_symlink_abs_path_inited.name,
                EnvState.state_local_venv_dir_abs_path_inited.name,
                EnvState.state_local_tmp_dir_abs_path_inited.name,
                EnvState.state_py_exec_required_reached.name,
            ],
            state_name=if_none(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                state_name,
                EnvState.state_reinstall_triggered.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_start_id_var_loaded: str = self.eval_parent_state(
            EnvState.state_input_start_id_var_loaded.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        do_reinstall: bool = state_args_parsed.run_mode == RunMode.mode_upgrade.value

        state_py_exec_required_reached = self.eval_parent_state(
            EnvState.state_py_exec_required_reached.name
        )
        assert state_py_exec_required_reached >= PythonExecutable.py_exec_required

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

        # Reinstall can only happen outside `venv`:
        if not (
            do_reinstall
            and state_py_exec_required_reached == PythonExecutable.py_exec_required
        ):
            return False

        state_local_venv_dir_abs_path_inited = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_local_venv_dir_abs_path_inited.name
        )
        if os.path.exists(state_local_venv_dir_abs_path_inited):

            # Move old `venv` to temporary directory:

            state_local_tmp_dir_abs_path_inited = self.eval_parent_state(
                EnvState.state_local_tmp_dir_abs_path_inited.name
            )

            moved_venv_dir = os.path.join(
                state_local_tmp_dir_abs_path_inited,
                f"venv.before.{state_input_start_id_var_loaded}",
            )

            logger.info(
                f"moving `venv` dir from [{state_local_venv_dir_abs_path_inited}] to [{moved_venv_dir}]"
            )

            shutil.move(state_local_venv_dir_abs_path_inited, moved_venv_dir)

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        state_local_conf_symlink_abs_path_inited = self.eval_parent_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )
        constraints_txt_path = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            ConfConstEnv.constraints_txt_basename,
        )
        if os.path.exists(constraints_txt_path):
            logger.info(f"removing version constraints file [{constraints_txt_path}]")
            os.remove(constraints_txt_path)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_package_driver_prepared(
    AbstractCachingStateNode[PackageDriverBase]
):
    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_required_python_file_abs_path_inited.name,
                EnvState.state_local_cache_dir_abs_path_inited.name,
                EnvState.state_package_driver_inited.name,
                EnvState.state_reinstall_triggered.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_package_driver_prepared.name,
            ),
        )

    def _eval_state_once(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> ValueType:

        state_required_python_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_required_python_file_abs_path_inited.name
        )

        state_package_driver_inited: PackageDriverType = self.eval_parent_state(
            EnvState.state_package_driver_inited.name
        )

        state_local_cache_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_cache_dir_abs_path_inited.name
        )

        package_driver: PackageDriverBase
        if PackageDriverType.driver_uv == state_package_driver_inited:
            # TODO: assert python version suitable for `uv`

            uv_venv_abs_path = os.path.join(
                # TODO: make it relative to "cache/venv" specifically (instead of directly to "cache"):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                state_local_cache_dir_abs_path_inited,
                # TODO: take from config (or default constant):
                "venv",
                # TODO: take from config (or default constant):
                "uv.venv",
            )
            uv_exec_abs_path = os.path.join(
                uv_venv_abs_path,
                ConfConstGeneral.file_rel_path_venv_uv,
            )

            if not os.path.exists(uv_exec_abs_path):
                # To use `PackageDriverType.driver_uv`, use `PackageDriverType.driver_pip` to install `uv` first:
                pip_driver = PackageDriverPip()
                pip_driver.create_venv(
                    state_required_python_file_abs_path_inited,
                    uv_venv_abs_path,
                )
                uv_exec_venv_python_abs_path = os.path.join(
                    uv_venv_abs_path,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                    ConfConstGeneral.file_rel_path_venv_python,
                )
                pip_driver.install_packages(
                    uv_exec_venv_python_abs_path,
                    [
                        ConfConstGeneral.name_uv_package,
                    ],
                )

            assert os.path.isfile(uv_exec_abs_path)

            package_driver = PackageDriverUv(
                uv_exec_abs_path=uv_exec_abs_path,
            )

        elif PackageDriverType.driver_pip == state_package_driver_inited:
            # Nothing to do:
            # `PackageDriverType.driver_pip` is available by default with the new `venv` without installation.
            package_driver = PackageDriverPip()
        else:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            raise AssertionError(
                f"unsupported `{PackageDriverType.__name__}` [{state_package_driver_inited.name}]"
            )

        return package_driver


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_venv_reached(
    AbstractCachingStateNode[PythonExecutable]
):
    """
    Creates `venv` and switches to `python` from there.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_local_conf_file_abs_path_inited.name,
                EnvState.state_required_python_file_abs_path_inited.name,
                EnvState.state_local_venv_dir_abs_path_inited.name,
                EnvState.state_reinstall_triggered.name,
                EnvState.state_package_driver_prepared.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_venv_reached.name,
            ),
        )

    def _eval_state_once(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
    ) -> ValueType:

        state_py_exec_venv_reached: PythonExecutable

        state_input_start_id_var_loaded: str = self.eval_parent_state(
            EnvState.state_input_start_id_var_loaded.name
        )

        state_reinstall_triggered: bool = self.eval_parent_state(
            EnvState.state_reinstall_triggered.name
        )

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        state_required_python_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_required_python_file_abs_path_inited.name
        )
        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_venv_dir_abs_path_inited.name
        )

        state_package_driver_prepared: PackageDriverBase = self.eval_parent_state(
            EnvState.state_package_driver_prepared.name
        )

        venv_path_to_python: str = os.path.join(
            state_local_venv_dir_abs_path_inited,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python: str = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")

        # Do not do anything if beyond `PythonExecutable.py_exec_venv`:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        if state_input_py_exec_var_loaded >= PythonExecutable.py_exec_venv:
            return state_input_py_exec_var_loaded

        if is_sub_path(
            path_to_curr_python,
            state_local_venv_dir_abs_path_inited,
        ):
            raise AssertionError(
                f"Current `python` [{path_to_curr_python}] must be outside of `venv` [{state_local_venv_dir_abs_path_inited}]."
            )

        if os.environ.get(EnvVar.var_PROTOPRIMER_TEST_MODE.value, None) is None:
            if path_to_curr_python != state_required_python_file_abs_path_inited:
                raise AssertionError(
                    f"Current `python` [{path_to_curr_python}] must match the required one [{state_required_python_file_abs_path_inited}]."
                )

        assert state_input_py_exec_var_loaded <= PythonExecutable.py_exec_required
        state_py_exec_venv_reached = PythonExecutable.py_exec_required
        if not os.path.exists(state_local_venv_dir_abs_path_inited):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            state_package_driver_prepared.create_venv(
                state_required_python_file_abs_path_inited,
                state_local_venv_dir_abs_path_inited,
            )
        else:
            logger.info(
                f"reusing existing `venv` [{state_local_venv_dir_abs_path_inited}]"
            )
            if not state_package_driver_prepared.is_mine_venv(
                state_local_venv_dir_abs_path_inited,
            ):
                raise AssertionError(
                    f"`venv` [{state_local_venv_dir_abs_path_inited}] was not created by this driver [{state_package_driver_prepared.get_type().name}] retry with [{CommandAction.action_reinstall.value}]"
                )

        switch_python(
            curr_py_exec=state_input_py_exec_var_loaded,
            curr_python_path=state_required_python_file_abs_path_inited,
            next_py_exec=PythonExecutable.py_exec_venv,
            next_python_path=venv_path_to_python,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            start_id=state_input_start_id_var_loaded,
            proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
        )

        return state_py_exec_venv_reached


# noinspection PyPep8Naming
class Bootstrapper_state_protoprimer_package_installed(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_do_install_var_loaded.name,
                EnvState.state_args_parsed.name,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                EnvState.state_ref_root_dir_abs_path_inited.name,
                EnvState.state_local_conf_symlink_abs_path_inited.name,
                EnvState.state_project_descriptors_inited.name,
                EnvState.state_package_driver_prepared.name,
                EnvState.state_py_exec_venv_reached.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_protoprimer_package_installed.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_input_do_install_var_loaded: bool = self.eval_parent_state(
            EnvState.state_input_do_install_var_loaded.name
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )

        state_py_exec_venv_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_venv_reached.name
        )
        assert state_py_exec_venv_reached >= PythonExecutable.py_exec_venv

        state_ref_root_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_ref_root_dir_abs_path_inited.name
        )

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        state_project_descriptors_inited: list[dict] = self.eval_parent_state(
            EnvState.state_project_descriptors_inited.name
        )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        state_package_driver_prepared: PackageDriverBase = self.eval_parent_state(
            EnvState.state_package_driver_prepared.name
        )

        do_reinstall: bool = (
            state_args_parsed.run_mode == CommandAction.action_reinstall.value
        )

        do_install: bool = (
            state_py_exec_venv_reached == PythonExecutable.py_exec_venv
            and (do_reinstall or state_input_do_install_var_loaded)
        )

        if not do_install:
            return False

        constraints_txt_path = os.path.join(
            state_local_conf_symlink_abs_path_inited,
            ConfConstEnv.constraints_txt_basename,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        )
        if not os.path.exists(constraints_txt_path):
            logger.info(f"creating empty constraints file [{constraints_txt_path}]")
            write_text_file(constraints_txt_path, "")

        if len(state_project_descriptors_inited) == 0:
            logger.warning(
                f"{ValueName.value_project_descriptors.value} is empty - nothing to install"
            )
            return True

        state_package_driver_prepared.install_dependencies(
            state_ref_root_dir_abs_path_inited,
            get_path_to_curr_python(),
            constraints_txt_path,
            state_project_descriptors_inited,
        )

        return True


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


# noinspection PyPep8Naming
class Bootstrapper_state_version_constraints_generated(AbstractCachingStateNode[bool]):
    """
    Implements UC_44_82_07_30.requirements_lock.md.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_local_conf_symlink_abs_path_inited.name,
                EnvState.state_package_driver_prepared.name,
                EnvState.state_protoprimer_package_installed.name,
            ],
            state_name=if_none(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                state_name,
                EnvState.state_version_constraints_generated.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_protoprimer_package_installed: bool = self.eval_parent_state(
            EnvState.state_protoprimer_package_installed.name
        )

        if not state_protoprimer_package_installed:
            return False

        state_local_conf_symlink_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_conf_symlink_abs_path_inited.name
        )

        state_package_driver_prepared: PackageDriverBase = self.eval_parent_state(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            EnvState.state_package_driver_prepared.name
        )

        state_package_driver_prepared.pin_versions(
            get_path_to_curr_python(),
            os.path.join(
                state_local_conf_symlink_abs_path_inited,
                ConfConstEnv.constraints_txt_basename,
            ),
        )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_deps_updated_reached(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_version_constraints_generated.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_deps_updated_reached.name,
            ),
        )

    def _eval_state_once(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
    ) -> ValueType:

        state_py_exec_deps_updated_reached: PythonExecutable

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

        state_version_constraints_generated: bool = self.eval_parent_state(
            EnvState.state_version_constraints_generated.name
        )

        if (
            state_input_py_exec_var_loaded.value
            < PythonExecutable.py_exec_deps_updated.value

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        ):
            venv_path_to_python = get_path_to_curr_python()

            state_input_start_id_var_loaded: str = self.eval_parent_state(
                EnvState.state_input_start_id_var_loaded.name
            )

            state_py_exec_deps_updated_reached = PythonExecutable.py_exec_deps_updated
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"
            )
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_deps_updated,
                next_python_path=venv_path_to_python,
                start_id=state_input_start_id_var_loaded,
                proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
            )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        else:
            # Successfully reached the end goal:
            state_py_exec_deps_updated_reached = state_input_py_exec_var_loaded

        return state_py_exec_deps_updated_reached


# noinspection PyPep8Naming
class Bootstrapper_state_proto_code_updated(AbstractCachingStateNode[bool]):
    """
    Return `True` if content of the `proto_kernel` has changed.

    TODO: UC_52_87_82_92.conditional_auto_update.md
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_py_exec_deps_updated_reached.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_proto_code_updated.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_py_exec_deps_updated_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_deps_updated_reached.name
        )
        assert (

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            state_py_exec_deps_updated_reached >= PythonExecutable.py_exec_deps_updated
        )

        if state_py_exec_deps_updated_reached != PythonExecutable.py_exec_deps_updated:
            # Update only after package installation, otherwise, nothing to do:
            return False

        state_proto_code_file_abs_path_inited = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )
        assert os.path.isabs(state_proto_code_file_abs_path_inited)
        assert not os.path.islink(state_proto_code_file_abs_path_inited)
        assert os.path.isfile(state_proto_code_file_abs_path_inited)

        assert is_venv()
        try:
            import protoprimer
        except ImportError:
            logger.warning(
                f"Module `{ConfConstGeneral.name_protoprimer_package}` is missing in `venv`. "

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                f"{get_import_error_hint(ConfConstGeneral.name_protoprimer_package)} "
            )
            # These must be "instant" conditions.
            # No module => no update:
            return False

        # Use generator from an immutable (source) `primer_kernel`
        # instead of the current local (target) `proto_code` module to avoid:
        # generated code inside generated code inside generated code ...
        generated_content_single_header: str = (
            protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_single_header(
                protoprimer.primer_kernel
            )
        )
        generated_content_multiple_body: str = (
            protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate_multiple_body(
                protoprimer.primer_kernel
            )
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        # Use `primer_kernel` from installed package as the source for `proto_code` update:
        primer_kernel_abs_path = os.path.abspath(protoprimer.primer_kernel.__file__)
        primer_kernel_text: str = read_text_file(primer_kernel_abs_path)
        proto_code_text_old: str = read_text_file(
            state_proto_code_file_abs_path_inited,
        )

        # Update body:
        proto_code_text_periodic = insert_every_n_lines(
            input_text=primer_kernel_text,
            insert_text=generated_content_multiple_body,
            every_n=20,
        )

        # Update header:
        file_lines = proto_code_text_periodic.splitlines()
        file_lines.insert(1, generated_content_single_header)
        proto_code_text_new = "\n".join(file_lines)

        logger.debug(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_proto_code_file_abs_path_inited` [{state_proto_code_file_abs_path_inited}]"
        )
        write_text_file(
            file_path=state_proto_code_file_abs_path_inited,
            file_data=proto_code_text_new,
        )

        is_updated: bool = proto_code_text_old != proto_code_text_new
        return is_updated


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_src_updated_reached(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
                EnvState.state_input_py_exec_var_loaded.name,
                EnvState.state_input_start_id_var_loaded.name,
                EnvState.state_proto_code_file_abs_path_inited.name,
                EnvState.state_proto_code_updated.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_src_updated_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> ValueType:


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_py_exec_src_updated_reached: PythonExecutable

        state_input_py_exec_var_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_var_loaded.name
        )

        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_proto_code_file_abs_path_inited.name
        )

        state_proto_code_updated: bool = self.eval_parent_state(
            EnvState.state_proto_code_updated.name
        )
        if not state_proto_code_updated:
            # If not updated, no point to restart:
            state_py_exec_src_updated_reached = PythonExecutable.py_exec_src_updated
            return state_py_exec_src_updated_reached

        venv_path_to_python = get_path_to_curr_python()


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        if (
            state_input_py_exec_var_loaded.value
            < PythonExecutable.py_exec_src_updated.value
        ):

            state_input_start_id_var_loaded: str = self.eval_parent_state(
                EnvState.state_input_start_id_var_loaded.name
            )

            state_py_exec_src_updated_reached = PythonExecutable.py_exec_src_updated
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_proto_code_updated.name}] effective"
            )
            switch_python(
                curr_py_exec=state_input_py_exec_var_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_src_updated,
                next_python_path=venv_path_to_python,
                start_id=state_input_start_id_var_loaded,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                proto_code_abs_file_path=state_proto_code_file_abs_path_inited,
            )
        else:
            # Successfully reached the end goal:
            state_py_exec_src_updated_reached = state_input_py_exec_var_loaded

        return state_py_exec_src_updated_reached


# noinspection PyPep8Naming
class Bootstrapper_state_command_executed(AbstractCachingStateNode[int]):
    """
    If `ParsedArg.name_command`, this state replaces the current process with a shell executing the given command.
    """

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str] | None = None,
        state_name: str | None = None,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=if_none(
                parent_states,
                [
                    EnvState.state_default_stderr_log_handler_configured.name,
                    EnvState.state_args_parsed.name,
                    EnvState.state_local_venv_dir_abs_path_inited.name,
                    EnvState.state_local_cache_dir_abs_path_inited.name,
                    EnvState.state_py_exec_src_updated_reached.name,
                ],
            ),
            state_name=if_none(
                state_name,
                EnvState.state_command_executed.name,
            ),
        )

        self.start_interactive_shell: bool = False

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def _eval_state_once(
        self,
    ) -> ValueType:

        state_default_stderr_log_handler_configured: logging.Handler = (
            self.eval_parent_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        state_py_exec_src_updated_reached: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_src_updated_reached.name
        )
        assert state_py_exec_src_updated_reached >= PythonExecutable.py_exec_src_updated

        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_local_venv_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_venv_dir_abs_path_inited.name
        )

        state_local_cache_dir_abs_path_inited: str = self.eval_parent_state(
            EnvState.state_local_cache_dir_abs_path_inited.name,
        )

        shell_driver: ShellDriverBase = _get_shell_driver(
            state_local_cache_dir_abs_path_inited
        )

        command_line: str | None = getattr(
            state_args_parsed,
            ParsedArg.name_command.value,
            None,
        )

        if command_line is not None or self.start_interactive_shell:
            return shell_driver.run_shell(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                command_line,
                state_default_stderr_log_handler_configured,
                state_local_venv_dir_abs_path_inited,
            )
        else:
            # Otherwise, exit_code is 0:
            return 0


########################################################################################################################


class EnvState(enum.Enum):
    """
    Environment states to be reached during the bootstrap process.

    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).
    The value of `AbstractCachingStateNode` assigned is the default implementation for the state,
    and the only reason it is assigned is purely for the quick navigation across the source code in the IDE.


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    FT_68_54_41_96.state_dependency.md
    """

    state_input_stderr_log_level_var_loaded = (
        Bootstrapper_state_input_stderr_log_level_var_loaded
    )

    state_input_do_install_var_loaded = Bootstrapper_state_input_do_install_var_loaded

    state_default_stderr_log_handler_configured = (
        Bootstrapper_state_default_stderr_log_handler_configured
    )

    state_args_parsed = Bootstrapper_state_args_parsed

    state_input_stderr_log_level_eval_finalized = (
        Bootstrapper_state_input_stderr_log_level_eval_finalized
    )

    state_input_run_mode_arg_loaded = Bootstrapper_state_input_run_mode_arg_loaded

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    state_input_final_state_eval_finalized = (
        Bootstrapper_state_input_final_state_eval_finalized
    )

    # Special case: triggers everything:
    state_run_mode_executed = Bootstrapper_state_run_mode_executed

    state_input_py_exec_var_loaded = Bootstrapper_state_input_py_exec_var_loaded

    state_input_start_id_var_loaded = Bootstrapper_state_input_start_id_var_loaded

    state_input_proto_code_file_abs_path_var_loaded = (
        Bootstrapper_state_input_proto_code_file_abs_path_var_loaded
    )

    state_py_exec_arbitrary_reached = Bootstrapper_state_py_exec_arbitrary_reached

    state_proto_code_file_abs_path_inited = (
        Bootstrapper_state_proto_code_file_abs_path_inited

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    )

    state_primer_conf_file_abs_path_inited = (
        Bootstrapper_state_primer_conf_file_abs_path_inited
    )

    # `ConfLeap.leap_primer`:
    state_primer_conf_file_data_loaded = Bootstrapper_state_primer_conf_file_data_loaded

    state_ref_root_dir_abs_path_inited = Bootstrapper_state_ref_root_dir_abs_path_inited

    state_global_conf_dir_abs_path_inited = (
        Bootstrapper_state_global_conf_dir_abs_path_inited
    )

    state_global_conf_file_abs_path_inited = (
        Bootstrapper_state_global_conf_file_abs_path_inited
    )

    # `ConfLeap.leap_client`:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    state_client_conf_file_data_loaded = Bootstrapper_state_client_conf_file_data_loaded

    state_selected_env_dir_rel_path_inited = (
        Bootstrapper_state_selected_env_dir_rel_path_inited
    )

    state_local_conf_symlink_abs_path_inited = (
        Bootstrapper_state_local_conf_symlink_abs_path_inited
    )

    state_local_conf_file_abs_path_inited = (
        Bootstrapper_state_local_conf_file_abs_path_inited
    )

    # `ConfLeap.leap_env`:
    state_env_conf_file_data_loaded = Bootstrapper_state_env_conf_file_data_loaded

    state_required_python_file_abs_path_inited = (
        Bootstrapper_state_required_python_file_abs_path_inited
    )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_venv_dir_abs_path_inited = (
        Bootstrapper_state_local_venv_dir_abs_path_inited
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_log_dir_abs_path_inited = (
        Bootstrapper_state_local_log_dir_abs_path_inited
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_tmp_dir_abs_path_inited = (
        Bootstrapper_state_local_tmp_dir_abs_path_inited
    )

    # TODO: log, tmp, venv, ... dirs should better be configured at client level:
    state_local_cache_dir_abs_path_inited = (
        Bootstrapper_state_local_cache_dir_abs_path_inited
    )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    state_package_driver_inited = Bootstrapper_state_package_driver_inited

    state_project_descriptors_inited = Bootstrapper_state_project_descriptors_inited

    # `ConfLeap.leap_derived`:
    state_derived_conf_data_loaded = Bootstrapper_state_derived_conf_data_loaded

    state_effective_config_data_printed = (
        Bootstrapper_state_effective_config_data_printed
    )

    state_default_file_log_handler_configured = (
        Bootstrapper_state_default_file_log_handler_configured
    )

    state_py_exec_required_reached = Bootstrapper_state_py_exec_required_reached

    state_reinstall_triggered = Bootstrapper_state_reinstall_triggered


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    state_package_driver_prepared = Bootstrapper_state_package_driver_prepared

    state_py_exec_venv_reached = Bootstrapper_state_py_exec_venv_reached

    # TODO: rename to "client" (or "ref"?): `client_project_descriptors_installed`:
    state_protoprimer_package_installed = (
        Bootstrapper_state_protoprimer_package_installed
    )

    state_version_constraints_generated = (
        Bootstrapper_state_version_constraints_generated
    )

    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_py_exec_deps_updated_reached = Bootstrapper_state_py_exec_deps_updated_reached

    # TODO: rename according to the final name:
    state_proto_code_updated = Bootstrapper_state_proto_code_updated

    state_py_exec_src_updated_reached = Bootstrapper_state_py_exec_src_updated_reached

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    state_command_executed = Bootstrapper_state_command_executed


class TargetState(enum.Enum):
    """
    Special `EnvState`-s.
    """

    # Used for `EnvState.state_status_line_printed` to report exit code:
    target_stderr_log_handler = EnvState.state_default_stderr_log_handler_configured

    # A special state which triggers execution in the specific `RunMode`:
    target_run_mode_executed = EnvState.state_run_mode_executed

    # TODO: This should be `state_derived_conf_data_loaded`:
    # When all config files loaded:
    target_config_loaded = EnvState.state_package_driver_inited

    # The final state before switching to `PrimerRuntime.runtime_neo`:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    target_proto_bootstrap_completed = EnvState.state_command_executed


class StateGraph:
    """
    It is a graph, which must be a DAG.
    """

    def __init__(
        self,
    ):
        self.state_nodes: dict[str, StateNode] = {}

    def register_node(
        self,
        state_node: StateNode,
        replace_existing: bool = False,
    ) -> StateNode | None:
        state_name: str = state_node.get_state_name()
        if state_name in self.state_nodes:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            if replace_existing:
                existing_node = self.state_nodes[state_name]
                self.state_nodes[state_name] = state_node
                return existing_node
            else:
                raise AssertionError(
                    f"[{StateNode.__name__}] for [{state_name}] is already registered."
                )
        else:
            self.state_nodes[state_name] = state_node
            return None

    def get_state_node(
        self,
        state_name: str,
    ) -> StateNode | None:
        return self.state_nodes[state_name]

    def eval_state(
        self,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        state_name: str,
    ) -> Any:
        try:
            state_node = self.state_nodes[state_name]
        except KeyError:
            logger.error(f"`state_name` [{state_name}] is not registered.")
            raise
        return state_node.eval_own_state()


class MutableValue(Generic[ValueType]):
    """
    A mutable value which must be evaluated (initialized) via one of the `StateNode`-s before it can be used.

    This class provides an N-to-1 mechanism where N x `StateNode`-s update 1 x named `MutableValue`.

    Immutable values produced by `StateNode`-s cannot be changed -
    once evaluated, these values stay the same.
    Unlike `StateNode` values, `MutableValue` can evolve.


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    NOTE: The issue with `MutableValue`-s is that the order of reading/writing them is important.
    To avoid defects, always read them last (after evaluation of all parent `StateNode` states).
    It is not required to bootstrap to the latest `StateNode` updating the given `MutableValue`
    because some of these `StateNode`-s may not be (transitive) parents.
    But, if the current `StateNode` depends on parents updating that `MutableValue`,
    read it after evaluation of all parent states.
    """

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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        self,
        state_node: StateNode,
    ) -> ValueType:

        # This ensures that the `StateNode` using that `MutableValue`
        # declares `state_name` as a dependency:
        init_value = state_node.eval_parent_state(self.state_name)

        if self.curr_value is None:
            self.curr_value = init_value

        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after get [{self.curr_value}] in [{state_node.get_state_name()}]"
        )
        return self.curr_value

    def set_curr_value(
        self,
        state_node: StateNode | None,
        curr_value: ValueType,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    ) -> None:
        # TODO: Shell we also ensure that the `StateNode` using that `MutableValue` has necessary dependencies on write?

        if self.curr_value is None:
            raise AssertionError(
                f"`{MutableValue.__name__}` [{self.state_name}] cannot be set as it is not initialized yet."
            )
        state_name: str | None = None
        self.curr_value = curr_value
        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after set [{self.curr_value}] in [{state_node.get_state_name()}]"
        )


class EnvContext:

    def __init__(
        self,
    ):
        self.state_graph: StateGraph = StateGraph()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


        # TODO: Do not set it on `EnvContext` - use bootstrap-able values:
        self.final_state: str = TargetState.target_proto_bootstrap_completed.value.name

        self._build_default_graph()

    def _build_default_graph(self):
        """
        Registers all defined `EnvState`-s.
        """
        for env_state in EnvState:
            self.state_graph.register_node(env_state.value(self))

    def print_exit_line(
        self,
        exit_code: int,
        test_failure: bool = False,
    ) -> None:
        """
        Print a color-coded status message to stderr.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        """
        assert type(exit_code) is int, "`exit_code` must be an `int`"

        state_default_stderr_log_handler_configured: logging.Handler = (
            self.state_graph.eval_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        status_name: str
        is_reportable: bool
        if exit_code == 0:
            color_status = (
                f"{TermColor.back_dark_green.value}{TermColor.fore_dark_black.value}"
            )
            status_name = "SUCCESS"
            is_reportable = (
                state_default_stderr_log_handler_configured.level <= logging.INFO
            )
        else:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            if not test_failure and is_test_run():
                # Avoid confusing output with "FAILURE" in tests:
                status_name = "TEST_EXIT"
                color_status = f"{TermColor.back_dark_yellow.value}{TermColor.fore_dark_black.value}"
            else:
                status_name = "FAILURE"
                color_status = f"{TermColor.back_dark_red.value}{TermColor.fore_bright_white.value}"

            is_reportable = (
                state_default_stderr_log_handler_configured.level <= logging.CRITICAL
            )

        if is_reportable:
            print(
                f"{color_status}{status_name}{TermColor.reset_style.value} [{exit_code}]: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,
                flush=True,
            )



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

class PythonExecutableFilter(logging.Filter):
    """
    This filter sets the value of `py_exec_name` for each log entry without filtering any record.
    """

    def filter(
        self,
        record,
    ):
        record.py_exec_name = os.getenv(
            EnvVar.var_PROTOPRIMER_PY_EXEC.value,
            PythonExecutable.py_exec_unknown.name,
        )
        # Do not filter:
        return True


class UtcTimeFormatter(logging.Formatter):
    """
    Custom formatter with the proper timestamp.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """

    def __init__(
        self,
        print_date: bool,
        print_time: bool,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
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
            record.created, datetime.timezone.utc
        )
        iso_str = log_timestamp.isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )

        if self.print_date and self.print_time:
            return iso_str

        date_part, time_part = iso_str.split("T")

        if self.print_date:
            return date_part
        else:
            return time_part


class FileLogFormatter(UtcTimeFormatter):

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


    def __init__(
        self,
    ):
        # noinspection SpellCheckingInspection
        super().__init__(
            print_date=True,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s %(filename)s:%(lineno)d %(message)s",
        )


class StderrLogFormatter(UtcTimeFormatter):
    """
    Custom formatter with color and format based on log level for stderr.
    """

    color_reset = TermColor.reset_style.value
    color_set = {
        "CRITICAL": TermColor.fore_bold_dark_red.value,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        info_formatter = UtcTimeFormatter(
            print_date=False,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s %(message)s",
        )
        debug_formatter = UtcTimeFormatter(
            print_date=True,
            print_time=True,
            fmt="%(asctime)s pid:%(process)d %(levelname)s py:%(py_exec_name)s %(filename)s:%(lineno)d %(message)s",
        )
        self.verbose_formatters = {
            # Anything above `logging.INFO` use default (least verbose):
            logging.INFO: info_formatter,
            # Most verbose:
            logging.DEBUG: debug_formatter,
            logging.NOTSET: debug_formatter,
        }
        self.verbosity_level = verbosity_level

    def set_verbosity_level(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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


def configure_stderr_log_handler(
    state_input_stderr_log_level_var_loaded: int,
) -> logging.Handler:
    """
    Implements for `stderr` log: FT_38_73_38_52.log_verbosity.md
    """

    # Log everything (the filters are supposed to be set on output handlers instead):
    logger.setLevel(logging.NOTSET)

    handler_class = logging.StreamHandler
    stderr_handler: logging.Handler | None = None
    if os.environ.get(EnvVar.var_PROTOPRIMER_TEST_MODE.value, None) is not None:
        # Prevent duplicate handler (when `os.execv*` calls restart `main` again in tests).
        # Select `stderr` handler:
        for handler_instance in logger.handlers:
            if isinstance(handler_instance, handler_class):
                if handler_instance.stream is sys.stderr:
                    stderr_handler = handler_instance

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                    break

    if stderr_handler is None:
        stderr_handler: logging.Handler = handler_class(sys.stderr)

        stderr_handler.addFilter(PythonExecutableFilter())
        stderr_handler.setFormatter(
            StderrLogFormatter(state_input_stderr_log_level_var_loaded)
        )

        logger.addHandler(stderr_handler)

    stderr_handler.setLevel(state_input_stderr_log_level_var_loaded)
    return stderr_handler


def configure_file_log_handler(
    script_name: str,
    state_input_start_id_var_loaded: str,
    state_input_stderr_log_level_eval_finalized: int,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    state_local_log_dir_abs_path_inited: str,
) -> logging.Handler:
    """
    Implements for log file: FT_38_73_38_52.log_verbosity.md
    """

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

    os.makedirs(state_local_log_dir_abs_path_inited, exist_ok=True)


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    if not os.path.exists(log_file_abs_path):
        # Explain missing logs to avoid confusion:
        write_text_file(
            log_file_abs_path,
            f"""
{ConfConstGeneral.log_section_delimiter} file log starts at [{PythonExecutable.py_exec_arbitrary.name}] after its config is resolved {ConfConstGeneral.log_section_delimiter}

""",
        )

    file_handler: logging.Handler = logging.FileHandler(log_file_abs_path)
    file_handler.addFilter(PythonExecutableFilter())

    file_formatter = FileLogFormatter()

    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    return file_handler

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



def rename_to_moved_state_name(state_name: str) -> str:
    """
    See UC_27_40_17_59.replace_by_new_and_use_old.md
    """
    return f"_{state_name}"


def warn_on_missing_conf_file(
    file_abs_path: str,
) -> None:
    logger.warning(
        f"File [{file_abs_path}] does not exist - use [{RunMode.mode_config.value}] sub-command for description."
    )


def can_print_effective_config(
    state_node: StateNode,
) -> bool:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """
    See: FT_19_44_42_19.effective_config.md
    """

    state_input_run_mode_arg_loaded: RunMode = state_node.eval_parent_state(
        EnvState.state_input_run_mode_arg_loaded.name
    )

    state_input_py_exec_var_loaded: PythonExecutable = state_node.eval_parent_state(
        EnvState.state_input_py_exec_var_loaded.name
    )

    return (
        state_input_py_exec_var_loaded.value
        # `PythonExecutable.py_exec_arbitrary` ensures that the path to `proto_code` is outside `venv`:
        == PythonExecutable.py_exec_arbitrary.value
        and state_input_run_mode_arg_loaded == RunMode.mode_config
    )



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

def verify_conf_file_data_contains_known_fields_only(
    file_path: str,
    file_data: dict,
) -> None:
    """
    Verifies that the config file data contains no unknown fields.

    Because config files can be combined, any defined field (regardless of `ConfLeap`) is possible.

    See: FT_00_22_19_59.derived_config.md
    """
    # TODO: After removal of `--wizard` is this still needed?
    #       All unknown fields are reported by `config`.


def switch_python(
    curr_py_exec: PythonExecutable,
    curr_python_path: str,
    next_py_exec: PythonExecutable,
    next_python_path: str,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    start_id: str,
    proto_code_abs_file_path: str | None,
    required_environ: dict | None = None,
):
    logger.info(
        f"switching from current `python` interpreter [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{EnvVar.var_PROTOPRIMER_PROTO_CODE.value}`[{proto_code_abs_file_path}]"
    )
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


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    required_environ[EnvVar.var_PROTOPRIMER_PY_EXEC.value] = next_py_exec.name
    required_environ[EnvVar.var_PROTOPRIMER_START_ID.value] = start_id
    if proto_code_abs_file_path is not None:
        required_environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = (
            proto_code_abs_file_path
        )

    logger.info(
        f"exec_argv: {exec_argv}"
        "\n"
        "\n"
        f"{ConfConstGeneral.log_section_delimiter} <<<[{curr_py_exec.name}]<<< {ConfConstGeneral.log_section_delimiter} >>>[{next_py_exec.name}]>>> {ConfConstGeneral.log_section_delimiter}"
        "\n"
    )
    os.execve(
        path=next_python_path,
        argv=exec_argv,
        env=required_environ,
    )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


def print_delegate_line(
    arg_list: list[str],
    stderr_log_handler: logging.Handler,
) -> None:

    color_delegate = (
        f"{TermColor.back_dark_blue.value}{TermColor.fore_bright_white.value}"
    )
    color_reset = TermColor.reset_style.value

    is_reportable: bool = stderr_log_handler.level <= logging.INFO
    if is_reportable:
        command_line = get_shell_command_line(arg_list)
        print(
            f"{color_delegate}DELEGATE{color_reset}: {command_line}",
            file=sys.stderr,
            flush=True,
        )


########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########


def get_file_name_timestamp():
    """
    Generate a timestamp acceptable to be embedded into a filename.
    """

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Format: "YYYYMMDDTHHMMSSZ"
    file_timestamp = now_utc.strftime("%Y%m%dT%H%M%S") + "Z"
    return file_timestamp


def get_default_start_id():
    return f"{get_file_name_timestamp()}.{os.getpid()}"


def is_sub_path(
    abs_sub_path: str,
    abs_base_base: str,
) -> bool:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    try:
        rel_path(
            abs_sub_path,
            abs_base_base,
        )
        return True
    except ValueError:
        return False


def rel_path(
    target_any_path: str,
    source_any_path: str,
) -> str:
    return str(
        pathlib.PurePath(target_any_path).relative_to(pathlib.PurePath(source_any_path))
    )


def get_path_to_curr_python() -> str:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    return sys.executable


def get_path_to_base_python():
    path_to_next_python = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_python,
    )
    return path_to_next_python


def get_script_command_line():
    return get_shell_command_line(sys.argv)


def get_shell_command_line(arg_list: list[str]):
    command_line = " ".join(shlex.quote(arg_item) for arg_item in arg_list)
    return command_line



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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
        file_obj.write("\n")


def read_text_file(
    file_path: str,
) -> str:
    with open(file_path, "r", encoding="utf-8") as file_obj:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return file_obj.read()


def write_text_file(
    file_path: str,
    file_data: str,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(file_data)


def insert_every_n_lines(
    input_text: str,
    insert_text: str,
    every_n: int,
) -> str:
    """
    Insert `insert_text` into `input_text` after `every_n` lines.

    Original use case: add boilerplate text indicating generated content throughout entire file.

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """
    input_lines: list[str] = input_text.splitlines()
    output_text = []

    for line_n, text_line in enumerate(input_lines, 1):
        output_text.append(text_line)
        if line_n % every_n == 0:
            output_text.append(insert_text)

    return (
        "\n".join(output_text)
        +
        # Add new line to ensure line of the `output_text` is not modified:
        "\n"
        +
        # This extra banner fixes the issue of fighting `pre-commit` plugins
        # when the previous new line is a trailing one
        # (trailing line is normally removed by `pre-commit`):
        f"{insert_text}"
        + "\n"

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    )


def if_none(
    given_value: ValueType | None,
    default_value: ValueType,
) -> ValueType:
    if given_value is None:
        return default_value
    else:
        return given_value


def is_venv() -> bool:
    # TODO: assert VIRTUAL_ENV or not assert?
    if sys.prefix != sys.base_prefix:
        # assert os.environ["VIRTUAL_ENV"]
        return True
    else:
        # assert not os.environ["VIRTUAL_ENV"]

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        return False


def is_uv_venv(
    venv_cfg_file_abs_path: str,
) -> bool:
    with open(venv_cfg_file_abs_path, "r") as cfg_file:
        for file_line in cfg_file:
            if file_line.strip().startswith(f"{ConfConstGeneral.name_uv_package} ="):
                return True
    return False


def is_pip_venv(
    venv_cfg_file_abs_path: str,
) -> bool:
    # Not sure how to check if it regular `venv` other than saying it is not by `uv`:
    return not is_uv_venv(
        venv_cfg_file_abs_path,
    )

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########



def is_test_run() -> bool:
    """
    See: FT_83_60_72_19.test_perimeter.md
    """
    # TODO: use constant:
    return "pytest" in sys.modules


def get_venv_type(
    local_venv_dir_abs_path: str,
) -> PackageDriverType:
    venv_cfg_file_abs_path = os.path.join(
        local_venv_dir_abs_path,
        # TODO: use constant:
        "pyvenv.cfg",
    )
    if not os.path.exists(venv_cfg_file_abs_path):
        raise AssertionError(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            f"File [{venv_cfg_file_abs_path}] does not exist",
        )

    if is_uv_venv(venv_cfg_file_abs_path):
        return PackageDriverType.driver_uv
    elif is_pip_venv(venv_cfg_file_abs_path):
        return PackageDriverType.driver_pip
    else:
        raise AssertionError(
            f"Cannot determine `venv` type by file [{venv_cfg_file_abs_path}]",
        )


def log_python_context(log_level: int = logging.INFO):
    """
    This function helps to ensure and verify:
    UC_88_09_19_74.no_installation_outside_venv.md
    """
    logger.log(
        log_level,

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

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

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        f"`sys.base_prefix`: {sys.base_prefix}",
    )
    logger.log(
        log_level,
        f"`sys.executable`: {sys.executable}",
    )


def get_import_error_hint(
    neo_main_module: str,
) -> str:
    # See: UC_78_58_06_54.no_stray_packages.md
    return f"Is `{neo_main_module}` a (transitive) dependency of any `{ConfConstClient.default_pyproject_toml_basename}` being installed?"


def switch_to_venv(
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       See usage - find a way to automatically provide it given the path to the `proto_kernel`.
    ref_root_dir_abs_path: str,
) -> bool:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

    """
    This is a helper function to run FT_75_87_82_46 entry script by `python` executable from `venv`.

    The entry script must know how to compute the path to `ref_root_dir_abs_path`
    (e.g., it must know its path within the client dir structure).

    The function fails if `venv` is not created - the user must trigger the bootstrap manually.

    :return: `True` if already inside `venv`, otherwise start itself inside `venv`.
    """

    if not is_venv():

        venv_bin = os.path.join(
            ref_root_dir_abs_path,
            # TODO: UC_54_26_66_63: This might be extracted from config:
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        venv_python = os.path.join(

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

            ref_root_dir_abs_path,
            # TODO: UC_54_26_66_63: This might be extracted from config:
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        if not os.path.exists(venv_python):
            raise AssertionError(
                f"`{venv_python}` does not exist - has `venv` been bootstrapped?"
            )

        # Equivalent of `./venv/bin/activate` to configure `PATH` env var:
        os.environ[ConfConstInput.ext_env_var_PATH] = (
            venv_bin + os.pathsep + os.environ.get(ConfConstInput.ext_env_var_PATH, "")
        )

        # Throws or never returns:
        os.execv(
            venv_python,
            [

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

                venv_python,
                *sys.argv,
            ],
        )
    else:
        # already switched:
        return True


def run_main(
    neo_main_module: str,
    neo_main_function: str,
):
    """
    Implements FT_14_52_73_23.primer_runtime.md transition
    from `PrimerRuntime.runtime_proto` to `PrimerRuntime.runtime_neo`.
    If `ImportError` occurs (when `venv` is not ready), it falls back to running `main` from `proto_kernel`.
    """
    try:
        # `PrimerRuntime.runtime_neo`:

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

        custom_module = importlib.import_module(neo_main_module)
        selected_main = getattr(custom_module, neo_main_function)
    except ImportError:
        py_exec = PythonExecutable[
            os.getenv(
                EnvVar.var_PROTOPRIMER_PY_EXEC.value,
                ConfConstInput.default_PROTOPRIMER_PY_EXEC,
            )
        ]
        if py_exec.value >= PythonExecutable.py_exec_src_updated.value:
            raise AssertionError(
                f"Failed to import `{neo_main_module}` with `{EnvVar.var_PROTOPRIMER_PY_EXEC.value}` [{py_exec.name}]. "
                f"{get_import_error_hint(neo_main_module)} "
            )
        # `PrimerRuntime.runtime_proto`:
        selected_main = main

    selected_main()



########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########

if __name__ == "__main__":
    main()

########### !!!!! GENERATED CONTENT - ANY CHANGES WILL BE LOST !!!!! ###########
