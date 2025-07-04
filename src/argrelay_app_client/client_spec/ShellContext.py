from __future__ import annotations

import os
from dataclasses import (
    dataclass,
    field,
)

import argrelay
from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_lib_root.enum_desc.CompScope import CompScope
from argrelay_lib_root.enum_desc.CompType import CompType
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_lib_root.enum_desc.TermColor import TermColor
from argrelay_lib_root.misc_helper_common import (
    eprint,
    get_argrelay_dir,
)

UNKNOWN_COMP_KEY: str = str(0)
"""
Constant used when client is called via `CallConv.CliArgsConv`
and there is no `COMP_KEY` env var to obtain the value
(unlike during `CallConv.EnvVarsConv`).
"""

COMP_LINE_env_var: str = "COMP_LINE"
COMP_POINT_env_var: str = "COMP_POINT"
COMP_TYPE_env_var: str = "COMP_TYPE"
COMP_KEY_env_var: str = "COMP_KEY"


@dataclass(frozen=True)
class ShellContext:
    """
    Immutable input data from a shell
    """

    command_line: str = field()
    cursor_cpos: int = field()
    comp_type: CompType = field()
    comp_key: str = field()
    is_debug_enabled: bool = field()
    input_data: str = field()

    def __post_init__(self):
        assert (
            0 <= self.cursor_cpos <= len(self.command_line)
        ), "Is this complex command line? See: https://github.com/argrelay/argrelay/issues/108"

    @classmethod
    def from_env(
        cls,
        argv: list[str],
    ) -> ShellContext:
        """
        See Bash docs on these env var:
        https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html
        """
        if COMP_LINE_env_var in os.environ:
            # See `CallConv.EnvVarsConv`:
            command_line = os.environ[COMP_LINE_env_var]
            cursor_cpos = int(os.environ[COMP_POINT_env_var])
            # If `COMP_LINE_env_var` exists, the call is definitely NOT for `CompType.InvokeAction`:
            comp_type = CompType(
                int(os.environ.get(COMP_TYPE_env_var, CompType.SubsequentHelp.value))
            )
            assert comp_type != CompType.InvokeAction
            comp_key = os.environ.get(COMP_KEY_env_var, UNKNOWN_COMP_KEY)
        else:
            # See `CallConv.CliArgsConv`:
            argv = [os.path.basename(argv[0])] + argv[1:]
            command_line = " ".join(argv)
            cursor_cpos = len(command_line)
            # If `COMP_LINE_env_var` is missing, the call is definitely for `CompType.InvokeAction`
            comp_type = CompType.InvokeAction
            comp_key = UNKNOWN_COMP_KEY

        is_debug_enabled = (
            "ARGRELAY_DEBUG" in os.environ and "p" in os.environ["ARGRELAY_DEBUG"]
        )

        return cls(
            command_line=command_line,
            cursor_cpos=cursor_cpos,
            comp_type=comp_type,
            comp_key=comp_key,
            is_debug_enabled=is_debug_enabled,
            input_data=None,
        )

    def print_debug(
        self,
        end_str: str = "\n",
    ) -> None:
        if not self.is_debug_enabled:
            return
        eprint(TermColor.debug_output.value, end="")
        eprint(f'"{self.command_line}"', end=" ")
        eprint(f"cursor_cpos: {self.cursor_cpos}", end=" ")
        eprint(f"comp_type: {self.comp_type}", end=" ")
        eprint(TermColor.reset_style.value, end=end_str)

    def create_call_context(
        self,
    ) -> CallContext:
        server_action: ServerAction = select_server_action(self.comp_type)
        return CallContext(
            client_version=argrelay.__version__,
            client_conf_target=get_client_conf_target(),
            server_action=server_action,
            command_line=self.command_line,
            cursor_cpos=self.cursor_cpos,
            comp_scope=CompScope.from_comp_type(self.comp_type),
            client_uid=get_user_name(),
            client_pid=os.getpid(),
            is_debug_enabled=self.is_debug_enabled,
            input_data=self.input_data,
        )


def select_server_action(
    comp_type,
) -> ServerAction:
    if comp_type is CompType.DescribeArgs:
        return ServerAction.DescribeLineArgs
    if comp_type is CompType.InvokeAction:
        return ServerAction.RelayLineArgs

    return ServerAction.ProposeArgValues


def get_user_name():
    try:
        return os.getlogin()
    except OSError:
        return ""


def get_client_conf_target():
    conf_path = f"{get_argrelay_dir()}/conf"
    if os.path.islink(conf_path):
        return os.readlink(conf_path)
    else:
        return ""
