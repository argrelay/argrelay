#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alexey Pakseykin
# See: https://github.com/uvsmtid/protoprimer
"""

TODO: Implement FT_02_89_37_65.shebang_line.md and update this comment:
The script must be run with Python 3.
Ensure that `python3` is in `PATH` for shebang to work.

Alternatively, run under a specific `python` interpreter:

    ```
    /path/to/pythonX ./path/to/protoprimer/entry/script.py
    ```

For example:

    ```
    /opt/bin/python ./prime

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ```

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
import subprocess
import sys
import tempfile
import typing
import venv

__version__ = "0.0.5"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


from typing import (
    Any,
    Generic,
    TypeVar,
)

logger: logging.Logger = logging.getLogger()

StateValueType = TypeVar("StateValueType")


def main(
    configure_env_context: typing.Callable[[], EnvContext] | None = None,
):

    try:
        ensure_min_python_version()

        if configure_env_context is None:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            env_ctx = EnvContext()
        else:
            # See UC_10_80_27_57.extend_dag.md:
            env_ctx = configure_env_context()

        # TODO: Do not call `state_graph.eval_state` directly - evaluate state via child state (to check that this is eligible).
        #       But... What is the child state here?
        state_run_mode_executed: bool = env_ctx.state_graph.eval_state(
            TargetState.target_run_mode_executed
        )
        assert state_run_mode_executed
        atexit.register(lambda: env_ctx.report_success_status(0))
    except SystemExit as sys_exit:
        if sys_exit.code == 0:
            atexit.register(lambda: env_ctx.report_success_status(0))
        else:
            atexit.register(lambda: env_ctx.report_success_status(1))
        raise
    except:
        atexit.register(lambda: env_ctx.report_success_status(1))

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        raise


def ensure_min_python_version():
    """
    Ensure the running Python interpreter is >= (major, minor, patch).
    """

    # FT_84_11_73_28: supported python versions:
    version_tuple: tuple[int, int, int] = (3, 8, 0)

    if sys.version_info < version_tuple:
        raise AssertionError(
            f"The version of Python used [{sys.version_info}] is below the min required [{version_tuple}]"
        )


class TermColor(enum.Enum):
    """
    Color codes for terminal text

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


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

    back_bright_red = "\033[101m"
    back_bright_green = "\033[102m"
    back_bright_yellow = "\033[103m"


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
    fore_bright_cyan = "\033[96m"
    fore_bright_white = "\033[97m"

    fore_bold_dark_red = "\033[1;31m"


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    # Semantic colors:

    field_name = f"{fore_bright_magenta}"
    field_description = f"{fore_bright_cyan}"
    field_review = f"{fore_bright_green}"
    error_text = f"{back_bright_yellow}{fore_dark_red}"

    reset_style = "\033[0m"


class ConfLeap(enum.Enum):
    """
    See FT_89_41_35_82.conf_leap.md
    """

    leap_input = "input"

    leap_primer = "primer"

    leap_client = "client"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    leap_env = "env"


class PrimerRuntime(enum.Enum):
    """
    See FT_14_52_73_23.primer_runtime.md
    """

    phase_proto = "proto"

    phase_venv = "venv"

    phase_neo = "neo"


class RunMode(enum.Enum):
    """
    Various modes the script can be run in.


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    See FT_11_27_29_83.run_mode.md
    """

    mode_prime = "prime"

    # TODO: implement:
    mode_check = "check"

    mode_wizard = "wizard"

    mode_graph = "graph"


class WizardStage(enum.Enum):

    wizard_started = "wizard_started"

    wizard_finished = "wizard_finished"



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

class FilesystemObject(enum.Enum):

    fs_object_file = "file"

    fs_object_dir = "dir"


class PathType(enum.Enum):

    # If both paths are possible (absolute or relative):
    path_any = "any_path"

    # Relative path:
    path_rel = "rel_path"

    # Absolute path:
    path_abs = "abs_path"


class EnvVar(enum.Enum):

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    """
    See FT_08_92_69_92.env_var.md
    """

    env_var_PROTOPRIMER_DEFAULT_LOG_LEVEL = "PROTOPRIMER_DEFAULT_LOG_LEVEL"


class ConfDst(enum.Enum):
    """
    See FT_23_37_64_44.conf_dst.md
    """

    dst_shebang = "shebang"

    dst_global = "gconf"

    dst_local = "lconf"


class ValueName(enum.Enum):

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    value_stderr_log_level = "stderr_log_level"

    value_run_mode = "run_mode"

    value_wizard_stage = "wizard_stage"

    value_target_state = "target_state"

    value_py_exec = "py_exec"

    value_primer_runtime = "primer_runtime"

    value_project_descriptors = "project_descriptors"

    value_install_extras = "install_extras"


class PathName(enum.Enum):


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    path_proto_code = "proto_code"

    # TODO: make use of it in naming states (instead of using only `path_proto_code`):
    path_proto_dir = "proto_dir"

    # TODO: Add a `feature_topic` for `ref root`:
    path_ref_root = "ref_root"

    # See FT_89_41_35_82.conf_leap.md / primer
    path_conf_primer = f"conf_{ConfLeap.leap_primer.value}"

    # See FT_89_41_35_82.conf_leap.md / env
    path_conf_client = f"conf_{ConfLeap.leap_client.value}"

    # See FT_89_41_35_82.conf_leap.md / env
    path_conf_env = f"conf_{ConfLeap.leap_env.value}"

    # TODO: Rename to "lconf_link"
    path_link_name = "link_name"


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    # TODO: Rename to "default_env"
    path_default_target = "default_target"

    path_local_env = "local_env"

    path_local_python = "local_python"

    path_local_venv = "local_venv"

    path_build_root = "build_root"


class CommandArg(enum.Enum):
    name_proto_code = (
        f"{PathName.path_proto_code.value}_{FilesystemObject.fs_object_file.value}"
    )

    name_py_exec = str(ValueName.value_py_exec.value)
    name_primer_runtime = str(ValueName.value_primer_runtime.value)
    name_run_mode = str(ValueName.value_run_mode.value)

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    name_wizard_stage = str(ValueName.value_wizard_stage.value)
    name_target_state = str(ValueName.value_target_state.value)


# TODO: Add file_log_level (but not via CLI, via config):
class LogLevel(enum.Enum):
    name_silent = "silent"
    name_quiet = "quiet"
    name_verbose = "verbose"


class ArgConst:

    arg_mode_graph = f"--{RunMode.mode_graph.value}"
    arg_mode_prime = f"--{RunMode.mode_prime.value}"
    arg_mode_check = f"--{RunMode.mode_check.value}"
    arg_mode_wizard = f"--{RunMode.mode_wizard.value}"

    arg_proto_code_abs_file_path = f"--{CommandArg.name_proto_code.value}"
    arg_py_exec = f"--{CommandArg.name_py_exec.value}"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    arg_primer_runtime = f"--{CommandArg.name_primer_runtime.value}"
    arg_run_mode = f"--{CommandArg.name_run_mode.value}"
    arg_wizard_stage = f"--{CommandArg.name_wizard_stage.value}"
    arg_target_state = f"--{CommandArg.name_target_state.value}"

    arg_s = f"-{LogLevel.name_silent.value[0]}"
    arg_silent = f"--{LogLevel.name_silent.value}"
    dest_silent = f"{ValueName.value_stderr_log_level}_{LogLevel.name_silent.value}"

    arg_q = f"-{LogLevel.name_quiet.value[0]}"
    arg_quiet = f"--{LogLevel.name_quiet.value}"
    dest_quiet = f"{ValueName.value_stderr_log_level}_{LogLevel.name_quiet.value}"

    arg_v = f"-{LogLevel.name_verbose.value[0]}"
    arg_verbose = f"--{LogLevel.name_verbose.value}"
    dest_verbose = f"{ValueName.value_stderr_log_level}_{LogLevel.name_verbose.value}"


class ConfField(enum.Enum):


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    field_primer_ref_root_dir_rel_path = f"{ConfLeap.leap_primer.value}_{PathName.path_ref_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_primer_conf_client_file_rel_path = f"{ConfLeap.leap_primer.value}_{PathName.path_conf_client.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_rel.value}"

    field_client_link_name_dir_rel_path = f"{ConfLeap.leap_client.value}_{PathName.path_link_name.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_client_default_target_dir_rel_path = f"{ConfLeap.leap_client.value}_{PathName.path_default_target.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_local_python_file_abs_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_python.value}_{FilesystemObject.fs_object_file.value}_{PathType.path_abs.value}"

    field_env_local_venv_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_local_venv.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_project_descriptors = (
        f"{ConfLeap.leap_env.value}_{ValueName.value_project_descriptors.value}"
    )

    field_env_build_root_dir_rel_path = f"{ConfLeap.leap_env.value}_{PathName.path_build_root.value}_{FilesystemObject.fs_object_dir.value}_{PathType.path_rel.value}"

    field_env_install_extras = (
        f"{ConfLeap.leap_env.value}_{ValueName.value_install_extras.value}"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    )


class ConfConstGeneral:

    name_proto_code = "proto_code"
    name_primer_kernel_module = "primer_kernel"
    default_proto_code_module = "proto_kernel"
    default_proto_code_basename = f"{default_proto_code_module}.py"

    # TODO: use lambdas to generate based on input (instead of None):
    # This is a value declared for completeness,
    # but unused (evaluated dynamically via the bootstrap process):
    input_based = None

    file_rel_path_venv_bin = os.path.join(
        "bin",
    )

    file_rel_path_venv_python = os.path.join(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        file_rel_path_venv_bin,
        "python",
    )

    file_rel_path_venv_activate = os.path.join(
        file_rel_path_venv_bin,
        "activate",
    )

    # TODO: Split into tall part (put once at the top) and short part (put repeatedly):
    func_get_proto_code_generated_boilerplate = lambda module_obj: (
        f"""
################################################################################
# Generated content:
# This is a (proto) copy of `{module_obj.__name__}` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################
"""
    )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################



class ConfConstInput:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_input
    """

    file_abs_path_script = ConfConstGeneral.input_based
    dir_abs_path_current = ConfConstGeneral.input_based

    # Next T_89_41_35_82.conf_leap.md: `ConfLeap.leap_primer`:
    default_file_basename_conf_primer = f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_primer.value}.json"

    ext_env_var_PATH: str = "PATH"

    default_PROTOPRIMER_DEFAULT_LOG_LEVEL: str = "INFO"


class ConfConstPrimer:
    """

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    Constants for FT_89_41_35_82.conf_leap.md / leap_primer
    """

    # Next T_89_41_35_82.conf_leap.md: `ConfLeap.leap_client`:
    default_client_conf_file_rel_path = os.path.join(
        f"{ConfDst.dst_global.value}",
        f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_client.value}.json",
    )


class ConfConstClient:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_client
    """

    default_dir_rel_path_leap_env_link_name = os.path.join(
        ConfDst.dst_local.value,
    )

    # TODO: By default, it may point to the same dir where `ConfLeap.leap_client` resides:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    default_client_default_target_dir_rel_path = "."

    # Next T_89_41_35_82.conf_leap.md: `ConfLeap.leap_env`:
    default_file_basename_leap_env = f"{ConfConstGeneral.default_proto_code_module}.{PathName.path_conf_env.value}.json"


class ConfConstEnv:
    """
    Constants for FT_89_41_35_82.conf_leap.md / leap_env
    """

    # TODO: This may not work everywhere:
    default_file_abs_path_python = "/usr/bin/python"

    default_dir_rel_path_venv = "venv"

    default_project_descriptors = []


class FieldWizardMeta:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def __init__(
        self,
        field_name: str,
        field_help: typing.Callable[[FieldWizardMeta, StateNode, dict], str],
        field_leap: ConfLeap,
        # Field name which contains this field as a nested structure (normally, `None`):
        root_ancestor_field: str | None,
        # Warn if the wizard cannot handle the field:
        warn_if_not_wizard_able: typing.Callable[
            [FieldWizardMeta, StateNode, dict], str | None
        ],
        read_value: typing.Callable[[FieldWizardMeta, StateNode, dict], str],
        validate_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ],
        review_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ],
        write_value: typing.Callable[[FieldWizardMeta, StateNode, dict, str], None],

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ):
        self.field_name: str = field_name
        self.field_help: typing.Callable[[FieldWizardMeta, StateNode, dict], str] = (
            FieldWizardMeta.get_callable(field_help)
        )
        self.field_leap: ConfLeap = field_leap
        # Set to `field_name` if `none` for simplicity:
        self.root_ancestor_field: str = (
            field_name if root_ancestor_field is None else root_ancestor_field
        )
        self.warn_if_not_wizard_able: typing.Callable[
            [FieldWizardMeta, StateNode, dict], str | None
        ] = FieldWizardMeta.get_callable(warn_if_not_wizard_able)
        self.read_value: typing.Callable[[FieldWizardMeta, StateNode, dict], str] = (
            FieldWizardMeta.get_callable(read_value)
        )
        self.validate_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], str | None
        ] = FieldWizardMeta.get_callable(validate_value)
        self.review_value: typing.Callable[

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            [FieldWizardMeta, StateNode, dict, str], str | None
        ] = FieldWizardMeta.get_callable(review_value)
        self.write_value: typing.Callable[
            [FieldWizardMeta, StateNode, dict, str], None
        ] = FieldWizardMeta.get_callable(write_value)

    @staticmethod
    def get_callable(staticmethod_or_callable):
        """
        This explicit function is only needed for earlier Python (e.g. 3.8) due to PEP 695 - ask LLM why.
        """
        if isinstance(staticmethod_or_callable, staticmethod):
            return staticmethod_or_callable.__func__
        else:
            return staticmethod_or_callable


class WizardField(enum.Enum):

    @staticmethod

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    def enumerate_conf_leap_fields(
        conf_leap: ConfLeap,
    ) -> list[tuple[int, WizardField]]:
        enumerated_conf_leap_fields: list[tuple[int, WizardField]] = []
        for total_ordinal_i, wizard_field in enumerate(WizardField):
            if wizard_field.value.field_leap == conf_leap:
                enumerated_conf_leap_fields.append((total_ordinal_i, wizard_field))
        return enumerated_conf_leap_fields

    @staticmethod
    def warn_if_not_wizard_able_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str | None:
        """
        Wizard is limited to simple field-value pairs only in the root of the conf file.
        But `ConfField.field_env_build_root_dir_rel_path` is part of a `list` of nested `dict`-s.
        Since the wizard is supposed to be used only for initial setup,
        it only supports updating a path to a lone project.

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        Essentially, the wizard reduces that field to a single field-value pair only.
        """
        assert (
            wizard_meta.field_name == ConfField.field_env_build_root_dir_rel_path.value
        )
        warn_text = (
            f"WARNING: Field [{ConfField.field_env_build_root_dir_rel_path.value}] cannot be updated by the wizard anymore. "
            f"To use the wizard for this field again, remove the entire [{ConfField.field_env_project_descriptors.value}] field manually. "
            f"See in the corresponding [{FieldWizardMeta.__name__}] entry in the code. "
        )
        if ConfField.field_env_project_descriptors.value not in file_data:
            return None
        field_env_project_descriptors = file_data[
            ConfField.field_env_project_descriptors.value
        ]
        assert isinstance(field_env_project_descriptors, list)
        if len(field_env_project_descriptors) > 1:
            return warn_text
        if len(field_env_project_descriptors) < 1:
            return None

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        single_project_descriptor = field_env_project_descriptors[0]
        assert isinstance(single_project_descriptor, dict)

        if (
            ConfField.field_env_build_root_dir_rel_path.value
            in single_project_descriptor
        ):
            build_root = single_project_descriptor[
                ConfField.field_env_build_root_dir_rel_path.value
            ]
            assert isinstance(build_root, str)

        if ConfField.field_env_install_extras.value in single_project_descriptor:
            install_extras = single_project_descriptor[
                ConfField.field_env_install_extras.value
            ]
            assert isinstance(install_extras, list)
            if len(install_extras) > 0:
                return warn_text


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        return None

    @staticmethod
    def read_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str:
        """
        Reads a single value of `ConfField.field_env_build_root_dir_rel_path`.

        See `warn_if_not_wizard_able_field_env_build_root_dir_rel_path`.
        """
        single_project = WizardField.get_assumed_single_project_descriptor(file_data)

        field_env_build_root_dir_rel_path: str
        if ConfField.field_env_build_root_dir_rel_path.value in single_project:
            field_env_build_root_dir_rel_path = single_project[
                ConfField.field_env_build_root_dir_rel_path.value
            ]

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        else:
            field_env_build_root_dir_rel_path = "."
        assert isinstance(field_env_build_root_dir_rel_path, str)

        return field_env_build_root_dir_rel_path

    @staticmethod
    def write_field_env_build_root_dir_rel_path(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> None:
        """
        Writes a single value of `ConfField.field_env_build_root_dir_rel_path`.

        See `warn_if_not_wizard_able_field_env_build_root_dir_rel_path`.
        """
        single_project = WizardField.get_assumed_single_project_descriptor(file_data)
        single_project[ConfField.field_env_build_root_dir_rel_path.value] = field_value

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        file_data[ConfField.field_env_project_descriptors.value] = [
            single_project,
        ]

    @staticmethod
    def get_assumed_single_project_descriptor(file_data: dict) -> dict:
        project_descriptors: list[dict]
        if ConfField.field_env_project_descriptors.value in file_data:
            project_descriptors = file_data[
                ConfField.field_env_project_descriptors.value
            ]
        else:
            project_descriptors = []
        assert isinstance(project_descriptors, list)
        if len(project_descriptors) < 1:
            project_descriptors.append({})
        assert len(project_descriptors) == 1
        single_project = project_descriptors[0]
        return single_project


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    @staticmethod
    def read_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
    ) -> str:
        return file_data[wizard_meta.field_name]

    @staticmethod
    def validate_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> str | None:
        return None

    @staticmethod
    def validate_rel_path_exists(
        wizard_meta,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_node,
        file_data,
        rel_path: str,
        base_name: str,
        base_abs_path: str,
    ) -> str | None:
        full_abs_path: str = os.path.join(
            base_abs_path,
            rel_path,
        )
        if os.path.exists(full_abs_path):
            return None
        else:
            return f"The base `{base_name}` [{base_abs_path}] and relative `{wizard_meta.field_name}` [{rel_path}] point to a non-existent path [{full_abs_path}]."

    @staticmethod
    def write_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        # TODO: support any type of field values (currently, only `str` exists):
        field_value: str,
    ) -> None:
        file_data[wizard_meta.field_name] = field_value

    @staticmethod
    def review_value_trivially(
        wizard_meta: FieldWizardMeta,
        state_node: StateNode,
        file_data: dict,
        field_value: str,
    ) -> str | None:
        return None

    field_primer_ref_root_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_primer_ref_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_primer_ref_root_dir_rel_path.value}` (or `{PathName.path_ref_root.value}` for short) leads to the client reference root "
            f"from the proto code script dir [{state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name)}]. "
            f"Subsequently, the client reference root `{PathName.path_ref_root.value}` is used as a base path for the most of the relative paths. "

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ),
        field_leap=ConfLeap.leap_primer,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        validate_value=lambda wizard_meta, state_node, file_data, field_value: WizardField.validate_rel_path_exists(
            wizard_meta,
            state_node,
            file_data,
            field_value,
            PathName.path_proto_dir.value,
            state_node.eval_parent_state(
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
            ),
        ),
        # TODO: consider wrapping it into a function - line is too long:
        review_value=lambda wizard_meta, state_node, file_data, field_value: (
            f"The base [{state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name)}] "
            f"and the relative [{field_value}] paths resolves into absolute "
            f"[{os.path.normpath(os.path.join(state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name), field_value))}]. "

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ),
        write_value=write_value_trivially,
    )

    field_primer_conf_client_file_rel_path = FieldWizardMeta(
        field_name=ConfField.field_primer_conf_client_file_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            f"Field `{ConfField.field_primer_conf_client_file_rel_path.value}` (or `{PathName.path_conf_client.value}` for short) leads to the client global configuration "
            f"from the client reference root `{PathName.path_ref_root.value}`. "
            f"Subsequently, the client global configuration `{PathName.path_conf_client.value}` (configuration not specific to the local environment) "
            f"is used by every deployment. "
        ),
        field_leap=ConfLeap.leap_primer,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # NOTE: The file is allowed not to exist:
        validate_value=validate_value_trivially,
        # TODO: consider wrapping it into a function - line is too long:
        review_value=lambda wizard_meta, state_node, file_data, field_value: (

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            f"The relative path [{field_value}] "
            f"resolves into absolute path "
            f"[{os.path.normpath(os.path.join(state_node.eval_parent_state(EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name), WizardField.field_primer_ref_root_dir_rel_path.value.read_value(WizardField.field_primer_ref_root_dir_rel_path.value, state_node, file_data), field_value))}]. "
        ),
        write_value=write_value_trivially,
    )

    field_client_link_name_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_client_link_name_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_client_link_name_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_client,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_client_default_target_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_client_default_target_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_client_default_target_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_client,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    field_env_local_python_file_abs_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_python_file_abs_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_local_python_file_abs_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_local_venv_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_local_venv_dir_rel_path.value,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_local_venv_dir_rel_path.value}` TODO"
        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=None,
        warn_if_not_wizard_able=lambda wizard_meta, state_node, file_data: None,
        read_value=read_value_trivially,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_value_trivially,
    )

    field_env_build_root_dir_rel_path = FieldWizardMeta(
        field_name=ConfField.field_env_build_root_dir_rel_path.value,
        field_help=lambda wizard_meta, state_node, file_data: (
            # TODO:
            f"Field `{ConfField.field_env_build_root_dir_rel_path.value}` TODO"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ),
        field_leap=ConfLeap.leap_env,
        root_ancestor_field=ConfField.field_env_project_descriptors.value,
        warn_if_not_wizard_able=warn_if_not_wizard_able_field_env_build_root_dir_rel_path,
        read_value=read_field_env_build_root_dir_rel_path,
        # TODO:
        validate_value=validate_value_trivially,
        # TODO:
        review_value=review_value_trivially,
        write_value=write_field_env_build_root_dir_rel_path,
    )


def init_arg_parser():

    suppress_internal_args: bool = True

    arg_parser = argparse.ArgumentParser(
        description="Prime the environment based on existing configuration.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    )

    mutex_group = arg_parser.add_mutually_exclusive_group()

    mutex_group.add_argument(
        ArgConst.arg_mode_prime,
        action="store_const",
        dest=CommandArg.name_run_mode.value,
        const=RunMode.mode_prime.value,
        help="Prime the environment to be ready to use.",
    )
    mutex_group.add_argument(
        ArgConst.arg_mode_check,
        action="store_const",
        dest=CommandArg.name_run_mode.value,
        const=RunMode.mode_check.value,
        help="Check the environment configuration.",
    )
    mutex_group.add_argument(
        ArgConst.arg_mode_wizard,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        action="store_const",
        dest=CommandArg.name_run_mode.value,
        const=RunMode.mode_wizard.value,
        help="Wizard through the environment configuration.",
    )
    mutex_group.add_argument(
        ArgConst.arg_mode_graph,
        action="store_const",
        dest=CommandArg.name_run_mode.value,
        const=RunMode.mode_graph.value,
        help="Render the graph of state dependencies.",
    )

    mutex_group.set_defaults(run_mode=RunMode.mode_prime.value)

    arg_parser.add_argument(
        # TODO: Make use of or clean up:
        ArgConst.arg_primer_runtime,
        type=str,
        choices=[context_phase.name for context_phase in PrimerRuntime],

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        default=PrimerRuntime.phase_proto.name,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: specifies `{PrimerRuntime.__name__}`."
        ),
    )
    # TODO: Use only -q and -v options in a simpler way:
    arg_parser.add_argument(
        ArgConst.arg_s,
        ArgConst.arg_silent,
        action="store_true",
        dest=ArgConst.dest_silent,
        # In the case of exceptions, stack traces are still printed:
        help="Do not log (set only non-zero exit code on error).",
    )
    arg_parser.add_argument(
        ArgConst.arg_q,
        ArgConst.arg_quiet,
        action="store_true",

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        dest=ArgConst.dest_quiet,
        help="Log errors messages only.",
    )
    arg_parser.add_argument(
        ArgConst.arg_v,
        ArgConst.arg_verbose,
        action="count",
        dest=ArgConst.dest_verbose,
        default=0,
        help="Increase log verbosity level.",
    )
    arg_parser.add_argument(
        ArgConst.arg_wizard_stage,
        type=str,
        choices=[wizard_stage.value for wizard_stage in WizardStage],
        default=WizardStage.wizard_started.value,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: specifies `{WizardStage.__name__}`."

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ),
    )
    arg_parser.add_argument(
        ArgConst.arg_target_state,
        type=str,
        # TODO: Decide to print choices or not (they look too excessive). Maybe print those in `TargetState` only?
        # choices=[state_name.name for state_name in EnvState],
        # Keep default `None` to indicate there was no user override (and select the actual default conditionally):
        default=None,
        # TODO: Compute universal sink:
        help=f"Select target `{EnvState.__name__}` name.",
    )
    arg_parser.add_argument(
        ArgConst.arg_proto_code_abs_file_path,
        type=str,
        default=None,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: path to `{ConfConstGeneral.name_proto_code}` identified before `{PythonExecutable.py_exec_venv.name}`."

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ),
    )
    arg_parser.add_argument(
        ArgConst.arg_py_exec,
        type=str,
        default=PythonExecutable.py_exec_unknown.name,
        help=(
            argparse.SUPPRESS
            if suppress_internal_args
            else f"Used internally: specifies known `{PythonExecutable.__name__}`."
        ),
    )
    return arg_parser


# TODO: This is not really a visitor anymore:
class AbstractNodeVisitor:
    """
    Visitor pattern to work with graph nodes.
    """

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def visit_node(
        self,
        state_node: StateNode,
    ) -> None:
        raise NotImplementedError()


class DefaultNodeVisitor(AbstractNodeVisitor):

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        super().__init__()
        self.env_ctx: EnvContext = env_ctx

    def visit_node(
        self,
        state_node: StateNode,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ) -> None:
        """
        This is a trivial implementation.

        No special DAG traversal because nodes traverse their own dependencies.
        But it may not reach all nodes because
        dependencies will be conditionally evaluated by the implementation of those nodes.
        """
        state_node.eval_own_state()


class SinkPrinterVisitor(AbstractNodeVisitor):
    """
    This class prints reduced DAG of `EnvState`-s.

    Full DAG for a target may involve the same dependency/parent multiple times.
    Printing each dependency multiple times (with all its transient dependencies) looks excessive.
    Instead, this class prints each dependency/parent only if any of its siblings have not been printed yet.
    Therefore, there is some duplication, but the result is both more concise and less confusing.
    """

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    rendered_no_parents: str = "[none]"

    def __init__(
        self,
        state_graph: StateGraph,
    ):
        super().__init__()
        self.state_graph: StateGraph = state_graph
        self.already_printed: set[str] = set()

    def visit_node(
        self,
        state_node: StateNode,
    ) -> None:
        self.print_node_parents(
            state_node,
            force_print=False,
            level=0,
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def print_node_parents(
        self,
        state_node,
        force_print: bool,
        level: int,
    ) -> None:
        if state_node.get_state_name() in self.already_printed and not force_print:
            return
        else:
            self.already_printed.add(state_node.get_state_name())

        # Indented name:
        print(
            f"{' ' * level * 4}{state_node.get_state_name()}",
            end="",
        )
        # Dependencies (parents):
        rendered_parent_states: str
        if len(state_node.get_parent_states()) > 0:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            rendered_parent_states = " ".join(state_node.get_parent_states())
        else:
            rendered_parent_states = self.rendered_no_parents
        print(
            f": {rendered_parent_states}",
            end="",
        )
        # new line:
        print()

        # Check ahead if any of the dependencies (parents) are not printed:
        any_parent_to_print: bool = False
        for state_parent in state_node.get_parent_states():
            if state_parent not in self.already_printed:
                any_parent_to_print = True
                break

        # Recurse:
        if any_parent_to_print:
            for state_parent in state_node.get_parent_states():

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                self.print_node_parents(
                    self.state_graph.state_nodes[state_parent],
                    # Even if this state was already printed, since we are printing siblings, print them all:
                    force_print=any_parent_to_print,
                    level=level + 1,
                )


class PythonExecutable(enum.IntEnum):
    """
    Python executables started during the bootstrap process - each replaces the executable program (via `os.execv`).

    See FT_72_45_12_06.python_executable.md
    """

    # `python` executable has not been categorized yet:
    py_exec_unknown = -1

    # To start `proto_code` by any `python`:
    py_exec_arbitrary = 1

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    # To run `python` of specific version (to create `venv`):
    py_exec_required = 2

    # To use `venv` (to install packages):
    py_exec_venv = 3

    # After making the latest `protoprimer` effective:
    py_exec_updated_protoprimer_package = 4

    # After making the updated `proto_code` effective:
    py_exec_updated_proto_code = 5

    # TODO: make "proto" clone of client extension effective:
    py_exec_updated_client_package = 6

    def __str__(self):
        return f"{self.name}[{self.value}]"



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

class StateNode(Generic[StateValueType]):
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

        # Ensure no duplicates:
        assert len(parent_states) == len(set(parent_states))

        # TODO: Actually bootstrap the additional states
        #       (beyond what is bootstrapped by code):
        self.parent_states: list[str] = parent_states

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        assert type(state_name) is str

        for state_parent in parent_states:
            assert type(state_parent) is str

    def accept_visitor(
        self,
        node_visitor: AbstractNodeVisitor,
    ) -> None:
        node_visitor.visit_node(self)

    def get_state_name(
        self,
    ) -> str:
        return self.state_name

    def get_parent_states(
        self,
    ) -> list[str]:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
    ) -> StateValueType:
        return self._eval_own_state()

    def _eval_own_state(
        self,
    ) -> StateValueType:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        raise NotImplementedError()


class AbstractCachingStateNode(StateNode[StateValueType]):

    def __init__(
        self,
        env_ctx: EnvContext,
        parent_states: list[str],
        state_name: str,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=parent_states,
            state_name=state_name,
        )
        self.is_cached: bool = False
        self.cached_value: StateValueType | None = None

    def _eval_own_state(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
    ) -> StateValueType:
        if not self.is_cached:
            # See FT_30_24_95_65.state_idempotency.md
            self.cached_value = self._eval_state_once()
            logger.debug(
                f"state [{self.state_name}] evaluated value [{self.cached_value}]"
            )
            self.is_cached = True

        return self.cached_value

    def _eval_state_once(
        self,
    ) -> StateValueType:
        raise NotImplementedError()


# noinspection PyPep8Naming
class Bootstrapper_state_process_status_initialized(AbstractCachingStateNode[int]):

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[],
            state_name=if_none(
                state_name, EnvState.state_process_status_initialized.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_process_status_initialized: int = 0
        return state_process_status_initialized


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


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
                state_name, EnvState.state_input_stderr_log_level_var_loaded.name
            ),
        )

    def _eval_state_once(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
    ) -> StateValueType:
        state_input_stderr_log_level_var_loaded: int = getattr(
            logging,
            os.getenv(
                EnvVar.env_var_PROTOPRIMER_DEFAULT_LOG_LEVEL.value,
                ConfConstInput.default_PROTOPRIMER_DEFAULT_LOG_LEVEL,
            ),
        )
        return state_input_stderr_log_level_var_loaded


# noinspection PyPep8Naming
class Bootstrapper_state_default_stderr_log_handler_configured(
    AbstractCachingStateNode[logging.Handler]
):

    def __init__(
        self,
        env_ctx: EnvContext,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_var_loaded.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_default_stderr_log_handler_configured.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        # Make all warnings be captured by the logging subsystem:
        logging.captureWarnings(True)

        state_input_stderr_log_level_var_loaded: int = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_var_loaded.name

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )
        assert state_input_stderr_log_level_var_loaded >= 0

        # Log everything (the filters are supposed to be set on output handlers instead):
        logger.setLevel(logging.NOTSET)

        stderr_handler: logging.Handler = logging.StreamHandler(sys.stderr)

        stderr_formatter = CustomFormatter()

        stderr_handler.setLevel(logging.NOTSET)
        stderr_handler.setFormatter(stderr_formatter)

        logger.addHandler(stderr_handler)

        stderr_handler.setLevel(state_input_stderr_log_level_var_loaded)

        return stderr_handler



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
            state_name=if_none(state_name, EnvState.state_args_parsed.name),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_args_parsed: argparse.Namespace = init_arg_parser().parse_args()
        return state_args_parsed


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


# noinspection PyPep8Naming
class Bootstrapper_state_input_wizard_stage_arg_loaded(
    AbstractCachingStateNode[WizardStage]
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
                state_name, EnvState.state_input_wizard_stage_arg_loaded.name
            ),
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def _eval_state_once(
        self,
    ) -> StateValueType:
        return WizardStage[
            getattr(
                self.eval_parent_state(EnvState.state_args_parsed.name),
                CommandArg.name_wizard_stage.value,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_input_stderr_log_level_eval_finalized_gconf(
    AbstractCachingStateNode[int]
):
    """
    There is a narrow window between the default log level is set and this state is evaluated.
    To control the default log level, see `EnvVar.env_var_PROTOPRIMER_DEFAULT_LOG_LEVEL`.
    """

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_default_stderr_log_handler_configured.name,
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_stderr_log_level_eval_finalized_gconf.name,
            ),
        )

    def _eval_state_once(
        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ) -> StateValueType:

        state_default_stderr_logger_configured: logging.Handler = (
            self.eval_parent_state(
                EnvState.state_default_stderr_log_handler_configured.name
            )
        )

        parsed_args = self.eval_parent_state(EnvState.state_args_parsed.name)
        stderr_log_level_silent = getattr(
            parsed_args,
            ArgConst.dest_silent,
        )
        stderr_log_level_quiet = getattr(
            parsed_args,
            ArgConst.dest_quiet,
        )
        stderr_log_level_verbose = getattr(
            parsed_args,
            ArgConst.dest_verbose,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )
        if stderr_log_level_silent:
            # disable logs = no output:
            state_default_stderr_logger_configured.setLevel(logging.CRITICAL + 1)
        elif stderr_log_level_quiet:
            state_default_stderr_logger_configured.setLevel(logging.ERROR)
        elif stderr_log_level_verbose:
            if stderr_log_level_verbose >= 2:
                state_default_stderr_logger_configured.setLevel(logging.NOTSET)
            elif stderr_log_level_verbose == 1:
                state_default_stderr_logger_configured.setLevel(logging.DEBUG)

        return state_default_stderr_logger_configured.level


# noinspection PyPep8Naming
class Bootstrapper_state_input_run_mode_arg_loaded_gconf(
    AbstractCachingStateNode[RunMode]
):


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
                state_name, EnvState.state_input_run_mode_arg_loaded_gconf.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_args_parsed: argparse.Namespace = self.eval_parent_state(
            EnvState.state_args_parsed.name

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )
        state_input_run_mode_arg_loaded_gconf: RunMode = RunMode(
            getattr(
                state_args_parsed,
                CommandArg.name_run_mode.value,
            )
        )
        return state_input_run_mode_arg_loaded_gconf


# noinspection PyPep8Naming
class Bootstrapper_state_input_target_state_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_args_parsed.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_input_target_state_eval_finalized.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_args_parsed = self.eval_parent_state(EnvState.state_args_parsed.name)
        state_input_target_state_eval_finalized = getattr(
            state_args_parsed,
            CommandArg.name_target_state.value,
        )

        if state_input_target_state_eval_finalized is None:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            # TODO: Fix duplicated logs: try default bootstrap - this line is printed repeatedly.
            #       Pass the arg after the start to subsequent `switch_python` calls.
            logger.info(
                f"selecting `default_target`[{self.env_ctx.default_target}] as no `{ArgConst.arg_target_state}` specified"
            )
            state_input_target_state_eval_finalized = self.env_ctx.default_target

        return state_input_target_state_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_run_mode_executed(AbstractCachingStateNode[bool]):
    """
    This is a special node - it traverses ALL nodes.

    BUT: It does not depend on ALL nodes - instead, it uses a visitor as a run mode strategy implementation.
    """

    def __init__(
        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_stderr_log_level_eval_finalized_gconf.name,
                EnvState.state_input_target_state_eval_finalized.name,
                EnvState.state_input_run_mode_arg_loaded_gconf.name,
            ],
            state_name=if_none(state_name, EnvState.state_run_mode_executed.name),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_input_stderr_log_level_eval_finalized_gconf = self.eval_parent_state(
            EnvState.state_input_stderr_log_level_eval_finalized_gconf.name
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        assert state_input_stderr_log_level_eval_finalized_gconf >= 0

        state_input_target_state_eval_finalized: str = self.eval_parent_state(
            EnvState.state_input_target_state_eval_finalized.name
        )

        state_input_run_mode_arg_loaded_gconf: RunMode = self.eval_parent_state(
            EnvState.state_input_run_mode_arg_loaded_gconf.name
        )

        state_node: StateNode = self.env_ctx.state_graph.state_nodes[
            state_input_target_state_eval_finalized
        ]

        selected_visitor: AbstractNodeVisitor
        if state_input_run_mode_arg_loaded_gconf is None:
            raise ValueError(f"run mode is not defined")
        elif state_input_run_mode_arg_loaded_gconf == RunMode.mode_graph:
            selected_visitor = SinkPrinterVisitor(self.env_ctx.state_graph)
        elif state_input_run_mode_arg_loaded_gconf == RunMode.mode_prime:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            selected_visitor = DefaultNodeVisitor(self.env_ctx)
        elif state_input_run_mode_arg_loaded_gconf == RunMode.mode_wizard:
            for wizard_state in WizardState:
                self.env_ctx.state_graph.register_node(
                    wizard_state.value(self.env_ctx),
                    replace_existing=True,
                )
            selected_visitor = DefaultNodeVisitor(self.env_ctx)
        else:
            raise ValueError(
                f"cannot handle run mode [{state_input_run_mode_arg_loaded_gconf}]"
            )

        selected_visitor.visit_node(state_node)

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_input_py_exec_arg_loaded(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    AbstractCachingStateNode[PythonExecutable]
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
                state_name, EnvState.state_input_py_exec_arg_loaded.name
            ),
        )

    def _eval_state_once(
        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ) -> StateValueType:
        return PythonExecutable[
            getattr(
                self.eval_parent_state(EnvState.state_args_parsed.name),
                CommandArg.name_py_exec.value,
            )
        ]


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_py_exec_arg_loaded.name,
                EnvState.state_args_parsed.name,
                EnvState.state_input_wizard_stage_arg_loaded.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_input_py_exec_arg_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_arg_loaded.name
        )


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_input_proto_code_file_abs_path_eval_finalized: str
        if (
            state_input_py_exec_arg_loaded.value
            == PythonExecutable.py_exec_unknown.value
        ):
            state_input_proto_code_file_abs_path_eval_finalized = os.path.abspath(
                __file__
            )
            if is_venv():
                # UC_90_98_17_93.run_under_venv.md
                # Switch out of the current `venv` (it might be arbitrary):
                path_to_curr_python = get_path_to_curr_python()
                path_to_next_python = get_path_to_base_python()
                switch_python(
                    curr_py_exec=state_input_py_exec_arg_loaded,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_arbitrary,
                    next_python_path=path_to_next_python,
                    proto_code_abs_file_path=None,
                    wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                        self,
                    ),
                )
        elif (
            state_input_py_exec_arg_loaded.value >= PythonExecutable.py_exec_venv.value
        ):
            state_args_parsed: argparse.Namespace = self.eval_parent_state(
                EnvState.state_args_parsed.name
            )

            arg_proto_code_abs_file_path = getattr(
                state_args_parsed,
                CommandArg.name_proto_code.value,
            )
            if arg_proto_code_abs_file_path is None:
                raise AssertionError(
                    f"`{ArgConst.arg_proto_code_abs_file_path}` is not specified at `{EnvState.state_input_py_exec_arg_loaded.name}` [{state_input_py_exec_arg_loaded}]"
                )
            # rely on the path given in args:
            state_input_proto_code_file_abs_path_eval_finalized = (

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                arg_proto_code_abs_file_path
            )
        else:
            assert not is_venv()
            state_input_proto_code_file_abs_path_eval_finalized = os.path.abspath(
                __file__
            )

        assert os.path.isabs(state_input_proto_code_file_abs_path_eval_finalized)
        return state_input_proto_code_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_input_proto_code_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_input_proto_code_dir_abs_path_eval_finalized = os.path.dirname(
            state_input_proto_code_file_abs_path_eval_finalized
        )

        assert os.path.isabs(state_input_proto_code_dir_abs_path_eval_finalized)
        return state_input_proto_code_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            parent_states=[
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_input_proto_code_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
        )

        # TODO: be able to configure path:
        return os.path.join(
            state_input_proto_code_dir_abs_path_eval_finalized,
            ConfConstInput.default_file_basename_conf_primer,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )


# noinspection PyPep8Naming
class Bootstrapper_state_proto_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_conf_file_data.name),
        )

    def _eval_state_once(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
    ) -> StateValueType:
        state_input_proto_conf_primer_file_abs_path_eval_finalized = (
            self.eval_parent_state(
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name
            )
        )

        file_data: dict
        if os.path.exists(state_input_proto_conf_primer_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_input_proto_conf_primer_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(
                error_on_missing_conf_file(
                    state_input_proto_conf_primer_file_abs_path_eval_finalized
                )
            )
        return file_data

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################



# noinspection PyPep8Naming
class Wizard_state_proto_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_proto_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_conf_file_data.name),
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_proto_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_input_proto_conf_primer_file_abs_path_eval_finalized = (
            self.eval_parent_state(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized.name
            )
        )

        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_primer,
            state_input_proto_conf_primer_file_abs_path_eval_finalized,
            default_file_data={
                ConfField.field_primer_ref_root_dir_rel_path.value: ".",
                ConfField.field_primer_conf_client_file_rel_path.value: ConfConstPrimer.default_client_conf_file_rel_path,
            },
        )

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_proto_conf_file_data.name,
                EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
    ) -> StateValueType:
        state_proto_conf_file_data = self.eval_parent_state(
            EnvState.state_proto_conf_file_data.name
        )

        field_client_dir_rel_path = state_proto_conf_file_data[
            ConfField.field_primer_ref_root_dir_rel_path.value
        ]

        state_input_proto_code_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_dir_abs_path_eval_finalized.name
        )

        state_primer_ref_root_dir_abs_path_eval_finalized = os.path.join(
            state_input_proto_code_dir_abs_path_eval_finalized,
            field_client_dir_rel_path,
        )

        state_primer_ref_root_dir_abs_path_eval_finalized = os.path.normpath(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            state_primer_ref_root_dir_abs_path_eval_finalized
        )

        assert os.path.isabs(state_primer_ref_root_dir_abs_path_eval_finalized)
        return state_primer_ref_root_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized(
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

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_client_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_client_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )
        state_client_local_env_dir_rel_path_eval_finalized = (
            state_client_conf_file_data.get(
                ConfField.field_client_default_target_dir_rel_path.value,
            )
        )
        if state_client_local_env_dir_rel_path_eval_finalized is None:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            raise AssertionError(
                f"Field `{ConfField.field_client_default_target_dir_rel_path.value}` is [{state_client_local_env_dir_rel_path_eval_finalized}] - re-run with [{ArgConst.arg_mode_wizard}] to set it."
            )
        return state_client_local_env_dir_rel_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized(
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
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_proto_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_proto_conf_file_data = self.eval_parent_state(
            EnvState.state_proto_conf_file_data.name
        )

        field_client_config_rel_path = state_proto_conf_file_data[

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            ConfField.field_primer_conf_client_file_rel_path.value
        ]

        state_primer_conf_client_file_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            field_client_config_rel_path,
        )

        return state_primer_conf_client_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_client_conf_file_data.name),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_primer_conf_client_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )
        if os.path.exists(state_primer_conf_client_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_primer_conf_client_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                error_on_missing_conf_file(
                    state_primer_conf_client_file_abs_path_eval_finalized
                )
            )
        return file_data


# noinspection PyPep8Naming
class Wizard_state_client_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_client_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:
                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_client_conf_file_data.name),
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_client_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ) -> StateValueType:

        state_primer_conf_client_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_primer_conf_client_file_abs_path_eval_finalized.name
        )

        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_client,
            state_primer_conf_client_file_abs_path_eval_finalized,
            default_file_data={
                # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
                #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
                #       Using default when value is missing in data does not work here.
                ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
                # TODO: This should not be part of the file - defaults should be configured, not generated (or generated by extensible code):
                # TODO: Prompt use in wizard and validate the value refers to an existing directory:
                ConfField.field_client_default_target_dir_rel_path.value: ConfConstClient.default_client_default_target_dir_rel_path,
            },
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized(
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
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_file_data.name,
            ],

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            state_name=if_none(
                state_name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )

        env_conf_dir_rel_path = file_data.get(
            ConfField.field_client_link_name_dir_rel_path.value,
            # TODO: Decide how to support (or avoid) evaluation of value if it does not exist.
            #       Maybe support few actions: check_if_exists and bootstrap_if_does_not_exists?
            #       Using default when value is missing in data does not work here.
            ConfConstClient.default_dir_rel_path_leap_env_link_name,
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        assert not os.path.isabs(env_conf_dir_rel_path)

        # Convert to absolute:
        state_client_conf_env_dir_abs_path_eval_finalized = os.path.join(
            self.eval_parent_state(
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
            ),
            env_conf_dir_rel_path,
        )

        return state_client_conf_env_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_local_env_dir_rel_path_eval_verified(
    AbstractCachingStateNode[bool]
):

    def __init__(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        """
        Raises exception if the target path of the `@/conf/` symlink is not allowed.

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        NOTE:
        At the moment, only target paths under `client_dir` (under `@/`) are allowed.
        This is not a strict requirement and can be relaxed in the future.
        """

        state_client_local_env_dir_rel_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
        )
        if os.path.isabs(state_client_local_env_dir_rel_path_eval_finalized):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must not be absolute path."
            )
        elif (
            ".."
            in pathlib.Path(state_client_local_env_dir_rel_path_eval_finalized).parts
        ):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must not contain `..` path segments."
            )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        elif not os.path.isdir(state_client_local_env_dir_rel_path_eval_finalized):
            raise AssertionError(
                f"Target for `@/conf/` symlink [{state_client_local_env_dir_rel_path_eval_finalized}] must lead to a directory."
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_env_dir_abs_path_eval_verified(
    AbstractCachingStateNode[bool]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            parent_states=[
                EnvState.state_client_local_env_dir_rel_path_eval_finalized.name,
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_conf_env_dir_abs_path_eval_verified.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_client_conf_env_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )

        state_client_local_env_dir_rel_path_eval_finalized = self.eval_parent_state(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            EnvState.state_client_local_env_dir_rel_path_eval_finalized.name
        )
        assert state_client_local_env_dir_rel_path_eval_finalized is not None

        if os.path.exists(state_client_conf_env_dir_abs_path_eval_finalized):
            if os.path.islink(state_client_conf_env_dir_abs_path_eval_finalized):
                if os.path.isdir(state_client_conf_env_dir_abs_path_eval_finalized):
                    if state_client_local_env_dir_rel_path_eval_finalized is None:
                        # TODO: Can we make it mandatory?
                        #       In cases when there is no env-specifics,
                        #       it can point to ref root (and entire link can be avoided if name is blank)?
                        # not configured or not specified => not required by user => nothing to do:
                        pass
                    else:
                        # Compare the existing link target and the configured one:
                        conf_dir_path = os.readlink(
                            state_client_conf_env_dir_abs_path_eval_finalized
                        )
                        if os.path.normpath(
                            state_client_local_env_dir_rel_path_eval_finalized

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                        ) == os.path.normpath(conf_dir_path):
                            pass
                        else:
                            raise AssertionError(
                                f"The `@/conf/` target [{conf_dir_path}] is not the same as the provided target [{state_client_local_env_dir_rel_path_eval_finalized}]."
                            )
                else:
                    raise AssertionError(
                        f"The `@/conf/` [{state_client_conf_env_dir_abs_path_eval_finalized}] target is not a directory.",
                    )
            else:
                raise AssertionError(
                    f"The `@/conf/` [{state_client_conf_env_dir_abs_path_eval_finalized}] is not a symlink.",
                )
        else:
            state_client_local_env_dir_rel_path_eval_verified = self.eval_parent_state(
                EnvState.state_client_local_env_dir_rel_path_eval_verified.name
            )
            assert state_client_local_env_dir_rel_path_eval_verified


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            os.symlink(
                os.path.normpath(state_client_local_env_dir_rel_path_eval_finalized),
                state_client_conf_env_dir_abs_path_eval_finalized,
            )

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized(
    AbstractCachingStateNode[str]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            parent_states=[
                EnvState.state_client_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_client_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_client_conf_file_data.name
        )
        state_client_link_name_dir_rel_path_eval_finalized = (
            state_client_conf_file_data.get(
                ConfField.field_client_link_name_dir_rel_path.value,
            )
        )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        if state_client_link_name_dir_rel_path_eval_finalized is None:
            raise AssertionError(
                f"Field `{ConfField.field_client_link_name_dir_rel_path.value}` is [{state_client_link_name_dir_rel_path_eval_finalized}] - re-run with [{ArgConst.arg_mode_wizard}] to set it."
            )
        return state_client_link_name_dir_rel_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized(
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

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_dir_abs_path_eval_verified.name,
                EnvState.state_client_link_name_dir_rel_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_client_conf_env_dir_abs_path_eval_verified = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_verified.name
        )
        assert state_client_conf_env_dir_abs_path_eval_verified

        state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_client_link_name_dir_rel_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_link_name_dir_rel_path_eval_finalized.name
        )

        state_client_conf_env_file_abs_path_eval_finalized = os.path.join(
            state_primer_ref_root_dir_abs_path_eval_finalized,
            state_client_link_name_dir_rel_path_eval_finalized,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstClient.default_file_basename_leap_env,
        )
        state_client_conf_env_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_dir_abs_path_eval_finalized.name
        )
        # TODO: Ensure the path is under with proper error message:
        if not is_sub_path(
            state_client_conf_env_file_abs_path_eval_finalized,
            state_client_conf_env_dir_abs_path_eval_finalized,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ):
            raise AssertionError(
                f"The `{state_client_conf_env_file_abs_path_eval_finalized}` path is not under `{state_client_conf_env_dir_abs_path_eval_finalized}`.",
            )
        return state_client_conf_env_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
            ],

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            state_name=if_none(state_name, EnvState.state_env_conf_file_data.name),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_client_conf_env_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
        )
        file_data: dict
        if os.path.exists(state_client_conf_env_file_abs_path_eval_finalized):
            file_data = read_json_file(
                state_client_conf_env_file_abs_path_eval_finalized
            )
        else:
            raise AssertionError(
                error_on_missing_conf_file(
                    state_client_conf_env_file_abs_path_eval_finalized
                )
            )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        return file_data


# noinspection PyPep8Naming
class Wizard_state_env_conf_file_data(AbstractCachingStateNode[dict]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        self.moved_state_name = rename_to_moved_state_name(
            EnvState.state_env_conf_file_data.name
        )
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
                # UC_27_40_17_59.replace_by_new_and_use_old.md:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                # Depend on the moved state:
                self.moved_state_name,
            ],
            state_name=if_none(state_name, EnvState.state_env_conf_file_data.name),
        )

        # UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Register the moved state implementation:
        self.moved_state_node = Bootstrapper_state_env_conf_file_data(
            env_ctx,
            self.moved_state_name,
        )
        self.env_ctx.state_graph.register_node(self.moved_state_node)

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_client_conf_env_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_client_conf_env_file_abs_path_eval_finalized.name

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )

        # TODO: This creates a directory with `ConfConstClient.default_dir_rel_path_leap_env_link_name` instead of symlink.
        #       But this happens only if dependency
        #       `state_client_conf_env_file_abs_path_eval_finalized` -> `state_client_conf_env_dir_abs_path_eval_verified`
        #       was not executed (which is not possible outside of tests).
        file_data = wizard_conf_file(
            self,
            ConfLeap.leap_env,
            state_client_conf_env_file_abs_path_eval_finalized,
            default_file_data={
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfField.field_env_local_python_file_abs_path.value: ConfConstEnv.default_file_abs_path_python,
                # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
                ConfField.field_env_local_venv_dir_rel_path.value: ConfConstEnv.default_dir_rel_path_venv,
                ConfField.field_env_project_descriptors.value: ConfConstEnv.default_project_descriptors,
            },
        )

        # Finish the wizard because this is the final wizard state:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.set_curr_value(
            WizardStage.wizard_finished
        )

        return file_data


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_python_file_abs_path_eval_finalized(
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

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_python_file_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_env_local_python_file_abs_path_eval_finalized = state_env_conf_file_data.get(
            ConfField.field_env_local_python_file_abs_path.value,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_file_abs_path_python,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )

        if not os.path.isabs(state_env_local_python_file_abs_path_eval_finalized):
            # TODO: Really? Do we really want to allow specifying `python` using rel path?
            #       Regardless, even if rel path, the `field_env_local_python_file_abs_path.value` should remove `abs` from the name then.
            state_env_local_python_file_abs_path_eval_finalized = os.path.join(
                self.eval_parent_state(
                    EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
                ),
                state_env_local_python_file_abs_path_eval_finalized,
            )

        return state_env_local_python_file_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized(
    AbstractCachingStateNode[str]
):


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        state_env_local_venv_dir_abs_path_eval_finalized = state_env_conf_file_data.get(
            ConfField.field_env_local_venv_dir_rel_path.value,
            # TODO: Do not use default values directly - resolve it differently at the prev|next step based on the need:
            ConfConstEnv.default_dir_rel_path_venv,
        )

        if not os.path.isabs(state_env_local_venv_dir_abs_path_eval_finalized):
            state_primer_ref_root_dir_abs_path_eval_finalized = self.eval_parent_state(
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
            )
            state_env_local_venv_dir_abs_path_eval_finalized = os.path.join(
                state_primer_ref_root_dir_abs_path_eval_finalized,
                state_env_local_venv_dir_abs_path_eval_finalized,
            )

        assert os.path.isabs(state_env_local_venv_dir_abs_path_eval_finalized)

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        return state_env_local_venv_dir_abs_path_eval_finalized


# noinspection PyPep8Naming
class Bootstrapper_state_env_project_descriptors_eval_finalized(
    AbstractCachingStateNode[list]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_env_conf_file_data.name,
            ],
            state_name=if_none(
                state_name,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                EnvState.state_env_project_descriptors_eval_finalized.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_env_conf_file_data: dict = self.eval_parent_state(
            EnvState.state_env_conf_file_data.name
        )

        project_descriptors: list[dict] = state_env_conf_file_data.get(
            ConfField.field_env_project_descriptors.value,
            ConfConstEnv.default_project_descriptors,
        )

        return project_descriptors


# noinspection PyPep8Naming

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

class Bootstrapper_state_py_exec_selected(AbstractCachingStateNode[PythonExecutable]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_arg_loaded.name,
                EnvState.state_env_local_python_file_abs_path_eval_finalized.name,
                EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name,
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_py_exec_selected.name),
        )


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    def _eval_state_once(
        self,
    ) -> StateValueType:
        """
        Recursively runs this script inside the `python` interpreter required by the user.

        The `python` interpreter required by the user is saved into `field_env_local_python_file_abs_path`.
        Otherwise, it matches the interpreter the main script is executed with at the moment.
        """

        state_py_exec_selected: PythonExecutable

        state_input_py_exec_arg_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_arg_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )

        state_env_local_python_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_python_file_abs_path_eval_finalized.name
        )
        state_env_local_venv_dir_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_env_local_venv_dir_abs_path_eval_finalized.name
        )

        # TODO: Make it separate validation state
        #       (not a dependency of this because, technically, we do not know where `EnvState.state_env_local_python_file_abs_path_eval_finalized` and `EnvState.state_env_local_venv_dir_abs_path_eval_finalized` came from):
        if is_sub_path(
            state_env_local_python_file_abs_path_eval_finalized,
            state_env_local_venv_dir_abs_path_eval_finalized,
        ):
            state_client_conf_env_file_abs_path_eval_finalized = self.eval_parent_state(
                EnvState.state_client_conf_env_file_abs_path_eval_finalized.name
            )
            raise AssertionError(
                f"The [{state_env_local_python_file_abs_path_eval_finalized}] is a sub-path of the [{state_env_local_venv_dir_abs_path_eval_finalized}]. "

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                f"This is not allowed because `path_to_python` is used to init `venv` and cannot rely on `venv` existance. "
                f"Specify different `{EnvState.state_env_local_python_file_abs_path_eval_finalized.name}` (e.g. `/usr/bin/python3`). "
                # TODO: compute path for `proto_code`:
                f"Alternatively, remove [{state_client_conf_env_file_abs_path_eval_finalized}] and re-run `@/cmd/proto_kernel.py` "
                f"to re-create it automatically. "
            )

        venv_path_to_python = os.path.join(
            state_env_local_venv_dir_abs_path_eval_finalized,
            ConfConstGeneral.file_rel_path_venv_python,
        )
        path_to_curr_python = get_path_to_curr_python()
        logger.debug(f"path_to_curr_python: {path_to_curr_python}")
        if is_sub_path(
            path_to_curr_python, state_env_local_venv_dir_abs_path_eval_finalized
        ):
            if path_to_curr_python != venv_path_to_python:
                assert (
                    state_input_py_exec_arg_loaded == PythonExecutable.py_exec_unknown
                )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                # Ensure `python` is from the correct `venv` path
                switch_python(
                    curr_py_exec=state_input_py_exec_arg_loaded,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_env_local_python_file_abs_path_eval_finalized,
                    proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                    wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                        self,
                    ),
                )
            else:
                # If already under `venv` with the expected path, nothing to do.
                assert (
                    state_input_py_exec_arg_loaded == PythonExecutable.py_exec_unknown
                    or state_input_py_exec_arg_loaded >= PythonExecutable.py_exec_venv
                )
                # Successfully reached the end goal:
                if state_input_py_exec_arg_loaded == PythonExecutable.py_exec_unknown:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                    state_py_exec_selected = PythonExecutable.py_exec_venv
                else:
                    state_py_exec_selected = state_input_py_exec_arg_loaded
        else:
            if (
                path_to_curr_python
                != state_env_local_python_file_abs_path_eval_finalized
            ):
                assert (
                    state_input_py_exec_arg_loaded == PythonExecutable.py_exec_unknown
                )
                state_py_exec_selected = PythonExecutable.py_exec_arbitrary
                switch_python(
                    curr_py_exec=state_input_py_exec_arg_loaded,
                    curr_python_path=path_to_curr_python,
                    next_py_exec=PythonExecutable.py_exec_required,
                    next_python_path=state_env_local_python_file_abs_path_eval_finalized,
                    proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                    wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                    ),
                )
            else:
                assert (
                    state_input_py_exec_arg_loaded <= PythonExecutable.py_exec_required
                )
                state_py_exec_selected = PythonExecutable.py_exec_required
                if not os.path.exists(state_env_local_venv_dir_abs_path_eval_finalized):
                    logger.info(
                        f"creating `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]"
                    )
                    venv.create(
                        state_env_local_venv_dir_abs_path_eval_finalized,
                        with_pip=True,
                    )
                else:
                    logger.info(
                        f"reusing existing `venv` [{state_env_local_venv_dir_abs_path_eval_finalized}]"
                    )
                switch_python(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                    curr_py_exec=state_input_py_exec_arg_loaded,
                    curr_python_path=state_env_local_python_file_abs_path_eval_finalized,
                    next_py_exec=PythonExecutable.py_exec_venv,
                    next_python_path=venv_path_to_python,
                    proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                    wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                        self,
                    ),
                )

        return state_py_exec_selected


# noinspection PyPep8Naming
class Bootstrapper_state_protoprimer_package_installed(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_py_exec_selected.name,
                EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name,
                EnvState.state_env_project_descriptors_eval_finalized.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_protoprimer_package_installed.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        state_py_exec_selected: PythonExecutable = self.eval_parent_state(
            EnvState.state_py_exec_selected.name
        )
        assert state_py_exec_selected >= PythonExecutable.py_exec_venv

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        state_primer_ref_root_dir_abs_path_eval_finalized: str = self.eval_parent_state(
            EnvState.state_primer_ref_root_dir_abs_path_eval_finalized.name
        )

        state_env_project_descriptors_eval_finalized: list[dict] = (
            self.eval_parent_state(
                EnvState.state_env_project_descriptors_eval_finalized.name
            )
        )

        if state_py_exec_selected == PythonExecutable.py_exec_venv:

            if len(state_env_project_descriptors_eval_finalized) == 0:
                logger.warning(
                    f"{ValueName.value_project_descriptors.value} is empty - nothing to install"
                )
                return True

            # pre-validate:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            for env_project_descriptor in state_env_project_descriptors_eval_finalized:
                # FT_46_37_27_11.editable_install.md

                field_env_build_root_dir_rel_path = os.path.join(
                    state_primer_ref_root_dir_abs_path_eval_finalized,
                    env_project_descriptor[
                        ConfField.field_env_build_root_dir_rel_path.value
                    ],
                )
                # TODO: Put "pyproject.toml" into constants:
                assert os.path.isfile(
                    os.path.join(field_env_build_root_dir_rel_path, "pyproject.toml")
                )

            # install:
            install_editable_project(
                state_primer_ref_root_dir_abs_path_eval_finalized,
                state_env_project_descriptors_eval_finalized,
            )


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_protoprimer_package_reached(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_arg_loaded.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
                EnvState.state_protoprimer_package_installed.name,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            ],
            state_name=if_none(
                state_name,
                EnvState.state_py_exec_updated_protoprimer_package_reached.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

        state_py_exec_updated_protoprimer_package_reached: PythonExecutable

        state_input_py_exec_arg_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_arg_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            )
        )

        state_protoprimer_package_installed: bool = self.eval_parent_state(
            EnvState.state_protoprimer_package_installed.name
        )
        assert state_protoprimer_package_installed

        if (
            state_input_py_exec_arg_loaded.value
            < PythonExecutable.py_exec_updated_protoprimer_package.value
        ):
            venv_path_to_python = get_path_to_curr_python()

            state_py_exec_updated_protoprimer_package_reached = (
                PythonExecutable.py_exec_updated_protoprimer_package
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_protoprimer_package_installed.name}] effective"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            )
            switch_python(
                curr_py_exec=state_input_py_exec_arg_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_protoprimer_package,
                next_python_path=venv_path_to_python,
                proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
            )
        else:
            # Successfully reached the end goal:
            state_py_exec_updated_protoprimer_package_reached = (
                state_input_py_exec_arg_loaded
            )

        return state_py_exec_updated_protoprimer_package_reached



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

# noinspection PyPep8Naming
class Bootstrapper_state_proto_code_updated(AbstractCachingStateNode[bool]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_py_exec_updated_protoprimer_package_reached.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(state_name, EnvState.state_proto_code_updated.name),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_py_exec_updated_protoprimer_package_reached: PythonExecutable = (
            self.eval_parent_state(
                EnvState.state_py_exec_updated_protoprimer_package_reached.name
            )
        )
        assert (
            state_py_exec_updated_protoprimer_package_reached
            >= PythonExecutable.py_exec_updated_protoprimer_package
        )

        # TODO: optimize: run this logic only when `PythonExecutable.py_exec_updated_protoprimer_package`

        state_input_proto_code_file_abs_path_eval_finalized = self.eval_parent_state(
            EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
        )
        assert os.path.isabs(state_input_proto_code_file_abs_path_eval_finalized)
        assert not os.path.islink(state_input_proto_code_file_abs_path_eval_finalized)
        assert os.path.isfile(state_input_proto_code_file_abs_path_eval_finalized)

        assert is_venv()

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        # TODO: This has to be changed for released names of the package:
        import protoprimer

        # Use generator from an immutable (source) `primer_kernel` to avoid
        # generated code inside generated code inside generated code ...
        # in local (target) `proto_code`:
        generated_content = protoprimer.primer_kernel.ConfConstGeneral.func_get_proto_code_generated_boilerplate(
            protoprimer.primer_kernel
        )

        primer_kernel_abs_path = os.path.abspath(protoprimer.primer_kernel.__file__)
        primer_kernel_text = read_text_file(primer_kernel_abs_path)
        assert primer_kernel_text.count(generated_content) < 10

        proto_code_text = insert_every_n_lines(
            input_text=primer_kernel_text,
            insert_text=generated_content,
            every_n=20,
        )


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        logger.debug(
            f"writing `primer_kernel_abs_path` [{primer_kernel_abs_path}] over `state_input_proto_code_file_abs_path_eval_finalized` [{state_input_proto_code_file_abs_path_eval_finalized}]"
        )
        write_text_file(
            file_path=state_input_proto_code_file_abs_path_eval_finalized,
            file_data=proto_code_text,
        )

        # TODO: optimize: return true if content changed:

        return True


# noinspection PyPep8Naming
class Bootstrapper_state_py_exec_updated_proto_code(
    AbstractCachingStateNode[PythonExecutable]
):

    def __init__(
        self,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_input_wizard_stage_arg_loaded.name,
                EnvState.state_input_py_exec_arg_loaded.name,
                EnvState.state_proto_code_updated.name,
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name,
            ],
            state_name=if_none(
                state_name, EnvState.state_py_exec_updated_proto_code.name
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        state_py_exec_updated_proto_code: PythonExecutable

        state_input_py_exec_arg_loaded: PythonExecutable = self.eval_parent_state(
            EnvState.state_input_py_exec_arg_loaded.name
        )

        state_input_proto_code_file_abs_path_eval_finalized: str = (
            self.eval_parent_state(
                EnvState.state_input_proto_code_file_abs_path_eval_finalized.name
            )
        )

        state_proto_code_updated: bool = self.eval_parent_state(
            EnvState.state_proto_code_updated.name
        )
        assert state_proto_code_updated

        venv_path_to_python = get_path_to_curr_python()

        if (

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            state_input_py_exec_arg_loaded.value
            < PythonExecutable.py_exec_updated_proto_code.value
        ):
            state_py_exec_updated_proto_code = (
                PythonExecutable.py_exec_updated_proto_code
            )
            # TODO: maybe add this reason to `switch_python` as an arg?
            logger.debug(
                f"restarting current `python` interpreter [{venv_path_to_python}] to make [{EnvState.state_proto_code_updated.name}] effective"
            )
            switch_python(
                curr_py_exec=state_input_py_exec_arg_loaded,
                curr_python_path=venv_path_to_python,
                next_py_exec=PythonExecutable.py_exec_updated_proto_code,
                next_python_path=venv_path_to_python,
                proto_code_abs_file_path=state_input_proto_code_file_abs_path_eval_finalized,
                wizard_stage=self.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
                    self,
                ),
            )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        else:
            # Successfully reached the end goal:
            state_py_exec_updated_proto_code = state_input_py_exec_arg_loaded

        return state_py_exec_updated_proto_code


# noinspection PyPep8Naming
class Bootstrapper_process_status_reported(AbstractCachingStateNode[int]):

    def __init__(
        self,
        env_ctx: EnvContext,
        state_name: str | None = None,
    ):
        super().__init__(
            env_ctx=env_ctx,
            parent_states=[
                EnvState.state_process_status_initialized.name,
                EnvState.state_default_stderr_log_handler_configured.name,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            ],
            state_name=if_none(
                state_name,
                EnvState.state_process_status_reported.name,
            ),
        )

    def _eval_state_once(
        self,
    ) -> StateValueType:
        """
        Print a color-coded status message to stderr.
        """

        color_success = "\033[42m\033[30m"
        color_failure = "\033[41m\033[97m"
        color_reset = "\033[0m"

        state_process_status_initialized = (
            self.env_ctx.mutable_state_process_status_initialized.get_curr_value(self)

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )

        target_stderr_log_handler: logging.Handler = self.eval_parent_state(
            EnvState.state_default_stderr_log_handler_configured.name
        )

        is_reportable: bool
        if state_process_status_initialized == 0:
            color_status = color_success
            status_name = "SUCCESS"
            is_reportable = target_stderr_log_handler.level <= logging.INFO
        else:
            color_status = color_failure
            status_name = "FAILURE"
            is_reportable = target_stderr_log_handler.level <= logging.CRITICAL

        if is_reportable:
            print(
                f"{color_status}{status_name}{color_reset}: {get_path_to_curr_python()} {get_script_command_line()}",
                file=sys.stderr,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                flush=True,
            )


class WizardState(enum.Enum):
    """
    These states replace some of the `EnvState` (named the same way) during `RunMode.mode_wizard`.
    """

    # TODO: Rename ALL to Bootstrapper -> Wizard (because we also have Primer):
    state_proto_conf_file_data = Wizard_state_proto_conf_file_data

    state_client_conf_file_data = Wizard_state_client_conf_file_data

    state_env_conf_file_data = Wizard_state_env_conf_file_data


class EnvState(enum.Enum):
    """
    Environment states to be reached during the bootstrap process.

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    NOTE: Only `str` names of the enum items are supposed to be used (any value is ignored).
    The value of `AbstractCachingStateNode` assigned is the default implementation for the state,
    and the only reason it is assigned is purely for the quick navigation across the source code in the IDE.

    FT_68_54_41_96.state_dependency.md
    """

    state_process_status_initialized = Bootstrapper_state_process_status_initialized

    state_input_stderr_log_level_var_loaded = (
        # TODO: Rename Bootstrapper -> Primer (because we also have Wizard):
        Bootstrapper_state_input_stderr_log_level_var_loaded
    )

    state_default_stderr_log_handler_configured = (
        Bootstrapper_state_default_stderr_log_handler_configured
    )

    state_args_parsed = Bootstrapper_state_args_parsed

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    state_input_wizard_stage_arg_loaded = (
        Bootstrapper_state_input_wizard_stage_arg_loaded
    )

    state_input_stderr_log_level_eval_finalized_gconf = (
        Bootstrapper_state_input_stderr_log_level_eval_finalized_gconf
    )

    state_input_run_mode_arg_loaded_gconf = (
        Bootstrapper_state_input_run_mode_arg_loaded_gconf
    )

    state_input_target_state_eval_finalized = (
        Bootstrapper_state_input_target_state_eval_finalized
    )

    # Special case: triggers everything:
    state_run_mode_executed = Bootstrapper_state_run_mode_executed


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    state_input_py_exec_arg_loaded = Bootstrapper_state_input_py_exec_arg_loaded

    state_input_proto_code_file_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_code_file_abs_path_eval_finalized
    )

    state_input_proto_code_dir_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_code_dir_abs_path_eval_finalized
    )

    state_input_proto_conf_primer_file_abs_path_eval_finalized = (
        Bootstrapper_state_input_proto_conf_primer_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_proto_conf_file_data`:
    state_proto_conf_file_data = Bootstrapper_state_proto_conf_file_data

    state_primer_ref_root_dir_abs_path_eval_finalized = (
        Bootstrapper_state_primer_ref_root_dir_abs_path_eval_finalized
    )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    state_primer_conf_client_file_abs_path_eval_finalized = (
        Bootstrapper_state_primer_conf_client_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_client_conf_file_data`:
    state_client_conf_file_data = Bootstrapper_state_client_conf_file_data

    # TODO: not env but global leap_client one:
    # state_client_path_to_python

    # TODO: not env but global leap_client one:
    # state_client_path_to_venv

    state_client_conf_env_dir_abs_path_eval_finalized = (
        Bootstrapper_state_client_conf_env_dir_abs_path_eval_finalized
    )

    state_client_local_env_dir_rel_path_eval_finalized = (
        Bootstrapper_state_client_local_env_dir_rel_path_eval_finalized

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    )

    state_client_local_env_dir_rel_path_eval_verified = (
        Bootstrapper_state_client_local_env_dir_rel_path_eval_verified
    )

    state_client_conf_env_dir_abs_path_eval_verified = (
        Bootstrapper_state_client_conf_env_dir_abs_path_eval_verified
    )

    state_client_link_name_dir_rel_path_eval_finalized = (
        Bootstrapper_state_client_link_name_dir_rel_path_eval_finalized
    )

    state_client_conf_env_file_abs_path_eval_finalized = (
        Bootstrapper_state_client_conf_env_file_abs_path_eval_finalized
    )

    # The state is wizard-able by `Wizard_state_env_conf_file_data`:
    state_env_conf_file_data = Bootstrapper_state_env_conf_file_data

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    # TODO: not env but global leap_client one:
    # state_env_log_level

    state_env_local_python_file_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_python_file_abs_path_eval_finalized
    )

    state_env_local_venv_dir_abs_path_eval_finalized = (
        Bootstrapper_state_env_local_venv_dir_abs_path_eval_finalized
    )

    state_env_project_descriptors_eval_finalized = (
        Bootstrapper_state_env_project_descriptors_eval_finalized
    )

    # TODO: rename to `py_exec_venv_reached`:
    state_py_exec_selected = Bootstrapper_state_py_exec_selected

    # TODO: rename to "client" (or "ref"?): `client_project_descriptors_installed`:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    state_protoprimer_package_installed = (
        Bootstrapper_state_protoprimer_package_installed
    )

    # TODO: rename - "reached" sounds weird (and makes no sense):
    state_py_exec_updated_protoprimer_package_reached = (
        Bootstrapper_state_py_exec_updated_protoprimer_package_reached
    )

    # TODO: rename according to the final name:
    state_proto_code_updated = Bootstrapper_state_proto_code_updated

    state_py_exec_updated_proto_code = Bootstrapper_state_py_exec_updated_proto_code

    state_process_status_reported = Bootstrapper_process_status_reported


class TargetState:
    """
    Special `EnvState`-s.

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    """

    target_full_proto_bootstrap: str = EnvState.state_py_exec_updated_proto_code.name

    target_run_mode_executed: str = EnvState.state_run_mode_executed.name

    target_stderr_log_handler: str = (
        EnvState.state_default_stderr_log_handler_configured.name
    )


class StateGraph:
    """
    It is a graph, which must be a DAG.
    """

    def __init__(
        self,
    ):
        self.state_nodes: dict[str, StateNode] = {}

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


    def register_node(
        self,
        state_node: StateNode,
        replace_existing: bool = False,
    ) -> StateNode | None:
        state_name: str = state_node.get_state_name()
        if state_name in self.state_nodes:
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


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    def get_state_node(
        self,
        state_name: str,
    ) -> StateNode | None:
        return self.state_nodes[state_name]

    def eval_state(
        self,
        state_name: str,
    ) -> Any:
        try:
            state_node = self.state_nodes[state_name]
        except KeyError:
            logger.error(f"`state_name` [{state_name}] is not registered.")
            raise
        return state_node.eval_own_state()


class MutableValue(Generic[StateValueType]):
    """

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    A mutable value which must be evaluated (initialized) via a `StateNode` before it can be used.

    Values accessible via `StateNode`-s cannot be changed - once evaluated, these values stay the same.
    Unlike `StateNode` values, `MutableValue` can evolve.

    NOTE: The issue with `MutableValue`-s is that the order of reading/writing them is important.
    To avoid defects, always read them last (after evaluation of all `StateNode`).
    """

    def __init__(
        self,
        state_name: str,
    ):
        self.state_name = state_name
        self.curr_value: StateValueType | None = None

    def get_curr_value(
        self,
        state_node: StateNode,
    ) -> StateValueType:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        # This ensures that the `StateNode` using that `MutableValue`
        # declares `state_name` as a dependency:
        init_value = state_node.eval_parent_state(self.state_name)

        if self.curr_value is None:
            self.curr_value = init_value

        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after get [{self.curr_value}]"
        )
        return self.curr_value

    def set_curr_value(
        self,
        curr_value: StateValueType,
    ) -> None:
        # TODO: Shell we also ensure that the `StateNode` using that `MutableValue` has necessary dependencies on write?

        if self.curr_value is None:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            raise AssertionError(
                f"`{MutableValue.__name__}` [{self.state_name}] cannot be set as it is not initialized yet."
            )
        self.curr_value = curr_value
        logger.debug(
            f"`{self.__class__.__name__}` [{self.state_name}] `curr_value` after set [{self.curr_value}]"
        )


class EnvContext:

    def __init__(
        self,
    ):
        self.state_graph: StateGraph = StateGraph()

        # TODO: Do not set it on Context - use bootstrap-able values:
        # TODO: Find "Universal Sink":
        self.default_target: str = TargetState.target_full_proto_bootstrap


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self.mutable_state_process_status_initialized: MutableValue[int] = MutableValue(
            EnvState.state_process_status_initialized.name,
        )

        self.mutable_state_input_wizard_stage_arg_loaded: MutableValue[WizardStage] = (
            MutableValue(
                EnvState.state_input_wizard_stage_arg_loaded.name,
            )
        )

        self._build_default_graph()

    def _build_default_graph(self):
        """
        Registers all defined `EnvState`-s.
        """
        for env_state in EnvState:
            self.state_graph.register_node(env_state.value(self))

    def report_success_status(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        self,
        new_status_code: int,
    ):
        """
        TODO: this looks awkward:
        """

        # Ensure `MutableValue` can be read:
        state_process_status_initialized = self.state_graph.eval_state(
            EnvState.state_process_status_initialized.name
        )

        # Use `StateNode` to work around the `MutableValue` defence
        # (which only allows reading it if `StateNode` declares the necessary dependency):
        node_state_process_status_reported = self.state_graph.get_state_node(
            EnvState.state_process_status_reported.name
        )

        # Avoid overriding non-zero `old_status_code`:
        old_status_code = self.mutable_state_process_status_initialized.get_curr_value(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            node_state_process_status_reported
        )
        if old_status_code == 0:
            self.mutable_state_process_status_initialized.set_curr_value(
                new_status_code
            )

        # Finally, report the current status:
        node_state_process_status_reported.eval_own_state()


class CustomFormatter(logging.Formatter):
    """
    Custom formatter with color and proper timestamp.
    """

    def __init__(
        self,
    ):
        # noinspection SpellCheckingInspection

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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


def rename_to_moved_state_name(state_name: str) -> str:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    """
    See UC_27_40_17_59.replace_by_new_and_use_old.md
    """
    return f"_{state_name}"


def error_on_missing_conf_file(
    file_abs_path: str,
) -> str:
    raise AssertionError(
        f"File [{file_abs_path}] does not exists - re-run with [{ArgConst.arg_mode_wizard}] to create it."
    )


def wizard_confirm_single_value(
    state_node: StateNode,
    wizard_meta: FieldWizardMeta,
    file_data: dict,
    sub_ordinal_n: int,
    sub_size: int,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    total_ordinal_n: int,
    total_size: int,
) -> None:
    """
    Wizard individual field provided by `FieldWizardMeta`.
    """

    while True:
        print("---")
        print(f"Total progress: {total_ordinal_n}/{total_size}")
        print(f"[{wizard_meta.field_leap.name}] progress: {sub_ordinal_n}/{sub_size}")
        print(
            f"{TermColor.field_name.value}Field: {wizard_meta.field_name}{TermColor.reset_style.value}"
        )
        print(
            f"{TermColor.field_description.value}Description: {wizard_meta.field_help(wizard_meta, state_node, file_data)}{TermColor.reset_style.value}"
        )

        field_warning: str | None = wizard_meta.warn_if_not_wizard_able(
            wizard_meta,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            state_node,
            file_data,
        )
        if field_warning is not None:
            print(field_warning)
            while True:
                user_confirmation = input(f"Acknowledge this (a) >").lower().strip()

                if user_confirmation == "a":
                    print(f"Continuing...")
                    # break the inner and the outer loops:
                    return
                else:
                    # continue the inner loop
                    continue

        curr_param_value = wizard_meta.read_value(
            wizard_meta,
            state_node,
            file_data,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        )

        print(
            f"Enter blank to keep the current value [{curr_param_value}] or provide a new value:"
        )
        new_param_value = input(f"[{curr_param_value}] >").strip()

        if new_param_value == "":
            # blank keeps the current value:
            new_param_value = curr_param_value

        review_text: str | None = wizard_meta.review_value(
            wizard_meta,
            state_node,
            file_data,
            new_param_value,
        )
        if review_text is not None:
            print(
                f"{TermColor.field_review.value}{review_text}{TermColor.reset_style.value}"

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            )

        validation_error = wizard_meta.validate_value(
            wizard_meta, state_node, file_data, new_param_value
        )
        if validation_error is not None:
            print(
                f"{TermColor.error_text.value}{validation_error}{TermColor.reset_style.value}"
            )
            print(f"Failing...")
            continue

        while True:

            user_confirmation = (
                input(
                    f"Confirm the value [{new_param_value}] (enter blank to skip, or y/n) >"
                )
                .lower()
                .strip()

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            )

            if user_confirmation == "y":
                print(f"Confirming...")
                curr_param_value = new_param_value
                # value has been changed - write `new_param_value`:
                wizard_meta.write_value(
                    wizard_meta,
                    state_node,
                    file_data,
                    new_param_value,
                )
                # break the inner and the outer loops:
                return
            elif user_confirmation == "":
                print(f"Skipping...")
                # TODO: It is not necessary to write.
                #       But at the moment, this is a workaround to in case like
                #       `WizardField.field_env_build_root_dir_rel_path` when the value read
                #       might be a synthesized default (and the file still requires to be rendered corerctly).

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

                # value is not changed - write `curr_param_value`:
                wizard_meta.write_value(
                    wizard_meta,
                    state_node,
                    file_data,
                    curr_param_value,
                )
                # break the inner and the outer loops:
                return
            elif user_confirmation == "n":
                print(f"Retrying...")
                # break the inner loop to retry the outer:
                break
            else:
                continue


def wizard_conf_file(
    state_node: StateNode,
    conf_leap: ConfLeap,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    conf_abs_path: str,
    # TODO: Instead of providing entire file, populate `FieldWizardMeta` how to compute default value:
    default_file_data: dict,
) -> dict:
    """
    A wrapper over `wizard_conf_leap` to persist the file data.
    """

    file_data: dict
    if os.path.exists(conf_abs_path):
        file_data = read_json_file(conf_abs_path)
    else:
        file_data = default_file_data

    wizard_stage: WizardStage = (
        state_node.env_ctx.mutable_state_input_wizard_stage_arg_loaded.get_curr_value(
            state_node,
        )
    )


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    if wizard_stage == WizardStage.wizard_started:
        wizard_conf_leap(
            state_node,
            conf_leap,
            conf_abs_path,
            file_data,
        )
        os.makedirs(
            os.path.dirname(conf_abs_path),
            exist_ok=True,
        )
        write_json_file(
            conf_abs_path,
            file_data,
        )

    return file_data


def wizard_conf_leap(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    state_node: StateNode,
    conf_leap: ConfLeap,
    conf_abs_path: str,
    file_data: dict,
) -> None:
    """
    Wizard through every field for the given `ConfLeap`.
    """

    enumerated_conf_leap_fields = WizardField.enumerate_conf_leap_fields(conf_leap)
    total_size = len(WizardField)
    sub_size = len(enumerated_conf_leap_fields)

    while True:

        print("===")
        print(f"File path: {conf_abs_path}")
        print(f"[{conf_leap.name}] summary before:")
        wizard_print_summary(file_data, conf_leap)


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        # Wizard fields:
        for sub_ordinal_i, (total_ordinal_i, wizard_field) in enumerate(
            enumerated_conf_leap_fields
        ):
            wizard_confirm_single_value(
                state_node,
                wizard_field.value,
                file_data,
                sub_ordinal_i + 1,
                sub_size,
                total_ordinal_i + 1,
                total_size,
            )

        print("===")
        print(f"File path: {conf_abs_path}")
        print(f"[{conf_leap.name}] summary after:")
        wizard_print_summary(file_data, conf_leap)

        # Confirm fields together:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        while True:
            user_confirmation = input(f"Confirm the values (y/n) >").lower().strip()

            if user_confirmation == "y":
                print(f"Confirming...")
                # break the inner and the outer loops:
                return
            elif user_confirmation == "":
                # continue the inner loop
                continue
            elif user_confirmation == "n":
                print(f"Retrying...")
                # break the inner loop to retry the outer:
                break
            else:
                continue


def wizard_print_summary(
    file_data,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

    conf_leap: ConfLeap,
) -> None:

    enumerated_conf_leap_fields = WizardField.enumerate_conf_leap_fields(conf_leap)

    # Construct data for specific `conf_leap` only:
    summary_data = {}
    for total_ordinal_i, wizard_field in enumerated_conf_leap_fields:
        wizard_meta = wizard_field.value
        if wizard_meta.root_ancestor_field not in file_data:
            raise AssertionError(
                f"missing field_name [{wizard_meta.field_name}] in field_data [{file_data}] with root_ancestor_field [{wizard_meta.root_ancestor_field}]"
            )
        summary_data[wizard_meta.root_ancestor_field] = file_data[
            wizard_meta.root_ancestor_field
        ]

    print(json.dumps(summary_data, indent=4))



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

def switch_python(
    curr_py_exec: PythonExecutable,
    curr_python_path: str,
    next_py_exec: PythonExecutable,
    next_python_path: str,
    proto_code_abs_file_path: str | None,
    wizard_stage: WizardStage,
):
    logger.info(
        f"switching from current `python` interpreter [{curr_python_path}][{curr_py_exec.name}] to [{next_python_path}][{next_py_exec.name}] with `{CommandArg.name_proto_code.value}`[{proto_code_abs_file_path}]"
    )
    exec_argv: list[str] = [
        next_python_path,
        *sys.argv,
        ArgConst.arg_py_exec,
        next_py_exec.name,
    ]

    # Once `ArgConst.arg_proto_code_abs_file_path` is specified, it is never changed (no need to override):
    if (proto_code_abs_file_path is not None) and (

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        ArgConst.arg_proto_code_abs_file_path not in exec_argv
    ):
        exec_argv.extend(
            [
                ArgConst.arg_proto_code_abs_file_path,
                proto_code_abs_file_path,
            ]
        )

    if wizard_stage != WizardStage.wizard_started:
        exec_argv.extend(
            [
                ArgConst.arg_wizard_stage,
                wizard_stage.value,
            ]
        )

    logger.debug(f"exec_argv: {exec_argv}")
    os.execv(
        next_python_path,

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        exec_argv,
    )


def create_temp_file():
    # TODO: avoid generating new temp file (use configured location):
    temp_file = tempfile.NamedTemporaryFile(mode="w+t", encoding="utf-8")
    return temp_file


def is_sub_path(
    abs_sub_path,
    abs_base_base,
):
    try:
        pathlib.PurePath(abs_sub_path).relative_to(pathlib.PurePath(abs_base_base))
        return True
    except ValueError:
        return False


################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


def get_path_to_curr_python():
    return sys.executable


def get_path_to_base_python():
    path_to_next_python = os.path.join(
        sys.base_prefix,
        ConfConstGeneral.file_rel_path_venv_python,
    )
    return path_to_next_python


def get_script_command_line():
    return " ".join(sys.argv)


def read_json_file(
    file_path: str,
) -> dict:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
        return file_obj.read()



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

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
    """
    input_lines: list[str] = input_text.splitlines()
    output_text = []

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


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
        # This fixes the issue of fighting `pre-commit` plugins
        # when the previous new line is trailing
        # (which is normally removed by pre-commit):
        "###"
        + "\n"
    )



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

def install_editable_project(
    ref_root_dir_abs_path: str,
    project_descriptors: list[dict],
):
    """
    Install each project from the `project_descriptors`.

    The assumption is that they use `pyproject.toml`.

    The result is equivalent of:
    ```sh
    path/to/python -m pip --editable path/to/project/a --editable path/to/project/b --editable path/to/project/c ...
    ```

    FT_46_37_27_11.editable_install.md
    """

    editable_project_install_args = []
    for project_descriptor in project_descriptors:
        project_build_root_dir_rel_path = project_descriptor[

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

            ConfField.field_env_build_root_dir_rel_path.value
        ]
        project_build_root_dir_abs_path = os.path.join(
            ref_root_dir_abs_path,
            project_build_root_dir_rel_path,
        )

        install_extras: list[str]
        if ConfField.field_env_install_extras.value in project_descriptor:
            install_extras = project_descriptor[
                ConfField.field_env_install_extras.value
            ]
        else:
            install_extras = []

        editable_project_install_args.append("--editable")
        if len(install_extras) > 0:
            editable_project_install_args.append(
                f"{project_build_root_dir_abs_path}[{','.join(install_extras)}]"
            )

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        else:
            editable_project_install_args.append(f"{project_build_root_dir_abs_path}")

    sub_proc_args = [
        get_path_to_curr_python(),
        "-m",
        "pip",
        "install",
        *editable_project_install_args,
    ]

    logger.info(f"installing projects: {' '.join(sub_proc_args)}")

    subprocess.check_call(sub_proc_args)


def install_package(
    package_name: str,
):
    subprocess.check_call(

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        [
            get_path_to_curr_python(),
            "-m",
            "pip",
            "install",
            package_name,
        ]
    )


def if_none(
    given_value: str,
    default_value: str,
) -> str:
    if given_value is None:
        return default_value
    else:
        return given_value



################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

def is_venv() -> bool:
    return sys.prefix != sys.base_prefix


def delegate_to_venv(
    ref_root_abs_path: str,
) -> bool:
    """
    This is a helper function to delegate script execution to a `python` from `venv`.

    It is supposed to be used in FT_75_87_82_46 entry scripts.
    The entry script must know how to compute the path to `ref_root_path`
    (e.g., it must know its path within the client dir structure).

    The function fails if `venv` is not created - the user must trigger the bootstrap manually.

    :return: `False` if already inside `venv`, otherwise start itself inside `venv`.
    """

    if not is_venv():

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################


        venv_bin = os.path.join(
            ref_root_abs_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        venv_python = os.path.join(
            ref_root_abs_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        if not os.path.exists(venv_python):
            raise AssertionError(
                f"`{venv_python}` does not exist - has `venv` been bootstrapped?"
            )

        # Equivalent of `./venv/bin/activate` to configure `PATH` env var:

################################################################################
# Generated content:
# This is a (proto) copy of `protoprimer.primer_kernel` updated automatically.
# It is supposed to be versioned (to be available in the "dst" repo on clone),
# but it should not be linted (as its content/style is owned by the "src" repo).
################################################################################

        os.environ[ConfConstInput.ext_env_var_PATH] = (
            venv_bin + os.pathsep + os.environ.get(ConfConstInput.ext_env_var_PATH, "")
        )

        # Throws or never returns:
        os.execv(
            venv_python,
            [
                venv_python,
                *sys.argv,
            ],
        )
    else:
        # Not delegated:
        return False


if __name__ == "__main__":
    main()
###
