from __future__ import annotations

import os
from dataclasses import dataclass, field

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.server_spec.CallContext import CallContext

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


@dataclass(frozen = True)
class ShellContext:
    """
    Immutable input data from a shell
    """

    command_line: str = field()
    cursor_cpos: int = field()
    comp_type: CompType = field()
    comp_key: str = field()
    is_debug_enabled: bool = field()

    def __post_init__(self):
        assert 0 <= self.cursor_cpos <= len(self.command_line)

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
            comp_type = CompType(int(os.environ[COMP_TYPE_env_var]))
            assert comp_type != CompType.InvokeAction
            comp_key = os.environ[COMP_KEY_env_var]
        else:
            # See `CallConv.CliArgsConv`:
            argv = [os.path.basename(argv[0])] + argv[1:]
            command_line = " ".join(argv)
            cursor_cpos = len(command_line)
            # If `COMP_LINE_env_var` is missing, the call is definitely for `CompType.InvokeAction`
            comp_type = CompType.InvokeAction
            comp_key = UNKNOWN_COMP_KEY

        is_debug_enabled = (
            "ARGRELAY_DEBUG" in os.environ
            and
            "p" in os.environ["ARGRELAY_DEBUG"]
        )

        return cls(
            command_line = command_line,
            cursor_cpos = cursor_cpos,
            comp_type = comp_type,
            comp_key = comp_key,
            is_debug_enabled = is_debug_enabled,
        )

    def print_debug(
        self,
        end_str: str = "\n",
    ) -> None:
        if not self.is_debug_enabled:
            return
        eprint(TermColor.debug_output.value, end = "")
        eprint(f"\"{self.command_line}\"", end = " ")
        eprint(f"cursor_cpos: {self.cursor_cpos}", end = " ")
        eprint(f"comp_type: {self.comp_type}", end = " ")
        eprint(TermColor.reset_style.value, end = end_str)

    def create_call_context(
        self,
    ) -> CallContext:
        server_action: ServerAction = self.select_server_action()
        return CallContext(
            server_action = server_action,
            command_line = self.command_line,
            cursor_cpos = self.cursor_cpos,
            comp_scope = CompScope.from_comp_type(self.comp_type),
            client_pid = os.getpid(),
            is_debug_enabled = self.is_debug_enabled,
        )

    def select_server_action(
        self,
    ) -> ServerAction:
        if self.comp_type is CompType.DescribeArgs:
            return ServerAction.DescribeLineArgs
        if self.comp_type is CompType.InvokeAction:
            return ServerAction.RelayLineArgs

        return ServerAction.ProposeArgValues
