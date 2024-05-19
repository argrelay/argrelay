from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint


@dataclass(frozen = True)
class CallContext:
    """
    Immutable input data from client to server
    """

    server_action: ServerAction = field()
    command_line: str = field()
    cursor_cpos: int = field()
    comp_scope: CompScope = field()
    client_pid: int = field()
    is_debug_enabled: bool = field()

    def print_debug(
        self,
        end_str: str = "\n",
    ) -> None:
        if not self.is_debug_enabled:
            return
        eprint(TermColor.debug_output.value, end = "")
        eprint(f"server_action: {self.server_action}", end = " ")
        eprint(f"\"{self.command_line}\"", end = " ")
        eprint(f"cursor_cpos: {self.cursor_cpos}", end = " ")
        eprint(f"comp_scope: {self.comp_scope}", end = " ")
        eprint(f"client_pid: {self.client_pid}", end = " ")
        eprint(TermColor.reset_style.value, end = end_str)
