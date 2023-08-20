from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint


@dataclass(frozen = True)
class CallContext:
    """
    Immutable input data from client to server
    """

    server_action: ServerAction = field()
    command_line: str = field()
    cursor_cpos: int = field()
    comp_scope: CompScope = field()
    is_debug_enabled: bool = field()

    # TODO: used on server side: to be changed into CallContext server-client-API class
    # TODO: call context should not be created from shell context on server side, it should simply be transferred from client
    @classmethod
    def from_shell_context(
        cls,
        shell_ctx: ShellContext,
    ) -> CallContext:
        server_action: ServerAction = cls.select_server_action(shell_ctx)
        return cls(
            server_action = server_action,
            command_line = shell_ctx.command_line,
            cursor_cpos = shell_ctx.cursor_cpos,
            comp_scope = CompScope.from_comp_type(shell_ctx.comp_type),
            is_debug_enabled = shell_ctx.is_debug_enabled,
        )

    @staticmethod
    def select_server_action(
        shell_ctx: ShellContext,
    ) -> ServerAction:
        if shell_ctx.comp_type == CompType.DescribeArgs:
            return ServerAction.DescribeLineArgs
        if shell_ctx.comp_type == CompType.InvokeAction:
            return ServerAction.RelayLineArgs

        return ServerAction.ProposeArgValues

    def print_debug(
        self,
        end_str: str = "\n",
    ) -> None:
        if not self.is_debug_enabled:
            return
        eprint(TermColor.DEBUG.value, end = "")
        eprint(f"server_action: {self.server_action}", end = " ")
        eprint(f"\"{self.command_line}\"", end = " ")
        eprint(f"cursor_cpos: {self.cursor_cpos}", end = " ")
        eprint(f"comp_scope: {self.comp_scope}", end = " ")
        eprint(TermColor.RESET.value, end = end_str)
