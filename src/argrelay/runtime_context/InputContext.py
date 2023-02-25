from __future__ import annotations

import os
from dataclasses import dataclass

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_context.RequestContext import RequestContext


@dataclass(frozen = True)
class InputContext(RequestContext):
    """
    Immutable input data
    """

    comp_key: str
    run_mode: RunMode

    @classmethod
    def from_request_context(
        cls,
        request_ctx: RequestContext,
        run_mode: RunMode,
        comp_key: str,
    ):
        return cls(
            command_line = request_ctx.command_line,
            cursor_cpos = request_ctx.cursor_cpos,
            comp_type = request_ctx.comp_type,
            is_debug_enabled = request_ctx.is_debug_enabled,
            run_mode = run_mode,
            comp_key = comp_key,
        )

    @classmethod
    def from_env(cls, argv: list[str]):
        """
        See Bash docs on these env var:
        https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html
        """
        if "COMP_LINE" in os.environ:
            # If "COMP_LINE" env var exists, the call is for CompletionMode:
            command_line = os.environ["COMP_LINE"]
            cursor_cpos = int(os.environ["COMP_POINT"])
            comp_type = CompType(int(os.environ["COMP_TYPE"]))
            comp_key = os.environ["COMP_KEY"]
            if comp_type == CompType.DescribeArgs:
                # FS_23_62_89_43:
                # To process tangent token in case of `CompType.DescribeArgs`, use `RunMode.InvocationMode`:
                run_mode = RunMode.InvocationMode
            else:
                run_mode = RunMode.CompletionMode
        else:
            # If no "COMP_LINE" env var, the call is for InvocationMode:
            run_mode = RunMode.InvocationMode
            argv = [os.path.basename(argv[0])] + argv[1:]
            command_line = " ".join(argv)
            cursor_cpos = len(command_line)
            comp_type = CompType.InvokeAction
            comp_key = str(0)

        is_debug_enabled = "ARGRELAY_DEBUG" in os.environ

        return cls(
            command_line = command_line,
            cursor_cpos = cursor_cpos,
            comp_type = comp_type,
            is_debug_enabled = is_debug_enabled,
            comp_key = comp_key,
            run_mode = run_mode,
        )

    def print_debug(self, end_str: str = "\n") -> None:
        if not self.is_debug_enabled:
            return
        eprint(TermColor.DEBUG.value, end = "")
        eprint(f"\"{self.command_line}\"", end = " ")
        eprint(f"cursor_cpos: {self.cursor_cpos}", end = " ")
        eprint(f"run_mode: {self.run_mode}", end = " ")
        eprint(TermColor.RESET.value, end = end_str)
