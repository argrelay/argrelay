from __future__ import annotations

import os
from dataclasses import dataclass

from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
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
            run_mode = RunMode.CompletionMode
            command_line = os.environ["COMP_LINE"]
            cursor_cpos = int(os.environ["COMP_POINT"])
            comp_type = CompType(int(os.environ["COMP_TYPE"]))
            comp_key = os.environ["COMP_KEY"]
        else:
            # If no "COMP_LINE" env var, the call is for InvocationMode:
            run_mode = RunMode.InvocationMode
            # Ignore argv[0] - it is how python called this.
            # Take arg[1] - it must be command name.
            argv = [os.path.basename(argv[1])] + argv[2:]
            command_line = " ".join(argv)
            cursor_cpos = len(command_line)
            comp_type = CompType.InvokeAction
            comp_key = str(0)

        is_debug_enabled = "ENABLE_DEBUG" in os.environ

        return cls(
            command_line = command_line,
            cursor_cpos = cursor_cpos,
            comp_type = comp_type,
            is_debug_enabled = is_debug_enabled,
            comp_key = comp_key,
            run_mode = run_mode,
        )