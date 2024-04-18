from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field

from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.server_spec.CallContext import CallContext


@dataclass(frozen = True)
class ParsedContext(CallContext):
    """
    Internal immutable parsed view of :class:`InputContext`

    Implements `FS_27_16_67_19` line syntax.

    `tan_token_*` = `tangent_token`, see FS_23_62_89_43.
    """

    all_tokens: list[str] = field(init = False)
    tan_token_ipos: int = field(init = False)
    tan_token_l_cpos: int = field(init = False)
    tan_token_r_cpos: int = field(init = False)
    tan_token: str = field(init = False)
    tan_token_l_part: str = field(init = False)
    tan_token_r_part: str = field(init = False)

    def __post_init__(self):
        (
            all_tokens,
            tan_token_ipos,
            tan_token_l_cpos,
            tan_token_r_cpos,
            tan_token,
            tan_token_l_part,
            tan_token_r_part,
        ) = self.parse_input(self)
        object.__setattr__(self, 'all_tokens', all_tokens)
        object.__setattr__(self, 'tan_token_ipos', tan_token_ipos)
        object.__setattr__(self, 'tan_token_l_cpos', tan_token_l_cpos)
        object.__setattr__(self, 'tan_token_r_cpos', tan_token_r_cpos)
        object.__setattr__(self, 'tan_token', tan_token)
        object.__setattr__(self, 'tan_token_l_part', tan_token_l_part)
        object.__setattr__(self, 'tan_token_r_part', tan_token_r_part)

    @classmethod
    def from_instance(
        cls,
        call_ctx: CallContext,
    ):
        return cls(**dataclasses.asdict(call_ctx))

    @staticmethod
    def parse_input(
        call_ctx: CallContext,
    ) -> tuple[
        list[str],
        int,
        int,
        int,
        str,
        str,
        str,
    ]:
        """
        Given `|` is the cursor in this command line:
        ```
        some_command some_su|b_command some_arg % next_arg   last_arg
        ```
        ```
                            |                                         # non-existing char placed to indicate cursor cpos
                                                %                     # arg bucket separator
        0            1                 2        3 4          5        # token ipos
        01234567890123456789 0123456789012345678901234567890123456789 # char cpos (the least significant digit)
        ```
        Then function returns:
        (
            [                               # list of all tokens
                "some_command",             # 0
                "some_sub_command",         # 1 (tangent token = token "touched" by the cursor)
                "some_arg",                 # 2
                "%",                        # 3 arg bucket separator
                "next_arg",                 # 4
                "last_arg"                  # 5
            ],
            1                               # tangent token item position (ipos)
            13                              # left-most char position (cpos) of tangent token (including it)
            29                              # right-most char position (cpos) of tangent token (excluding it)
            "some_sub_command",             # tangent token string
            "some_su",                      # tangent token left part substring (preceding cursor position)
            "b_command",                    # tangent token right part substring (succeeding cursor position)
        )
        """
        # Wrap orig command line into delimiter for simplification:
        command_line = f" {call_ctx.command_line} "
        cursor_cpos = call_ctx.cursor_cpos + 1
        line_len = len(command_line)

        # Init with defaults:
        # TODO: FS_23_62_89_43: Tangent token ipos should always be above zero and point to
        #                       (possibly surrogate missing empty) token ipos within command line.
        all_tokens = []
        tan_token_ipos = -1
        tan_token_l_cpos = -1
        tan_token_r_cpos = -1

        # Iterate through all delimiter spans to cut out tokens:
        prev_span_l = -1
        prev_span_r = -1
        token_ipos = 0
        for m in re.finditer(SpecialChar.TokenDelimiter.value, command_line):
            (span_l, span_r) = m.span(0)
            if prev_span_r != -1:
                # New token found between prev and curr delimiter span.
                if prev_span_r <= cursor_cpos <= span_l:
                    # Found tangent token (touched by the cursor):
                    tan_token_ipos = token_ipos
                    tan_token_l_cpos = prev_span_r
                    tan_token_r_cpos = span_l

                all_tokens.append(command_line[prev_span_r:span_l])
                token_ipos += 1

            prev_span_l = span_l
            prev_span_r = span_r

        if prev_span_r == -1:
            # No delimiter spans found => entire command line is the single token.
            tan_token_ipos = token_ipos
            tan_token_l_cpos = 0
            tan_token_r_cpos = line_len
            all_tokens.append(command_line)

        tan_token = command_line[tan_token_l_cpos:tan_token_r_cpos]
        tan_token_l_part = command_line[tan_token_l_cpos:cursor_cpos]
        tan_token_r_part = command_line[cursor_cpos:tan_token_r_cpos]

        # Adjust for wrapping command line into delimiters:
        if tan_token_l_cpos != -1:
            tan_token_l_cpos -= 1
        if tan_token_r_cpos != -1:
            tan_token_r_cpos -= 1

        return (
            all_tokens,
            tan_token_ipos,
            tan_token_l_cpos,
            tan_token_r_cpos,
            tan_token,
            tan_token_l_part,
            tan_token_r_part,
        )

    def print_debug(self, end_str: str = "\n") -> None:
        if not self.is_debug_enabled:
            return
        super().print_debug("")
        eprint(TermColor.debug_output.value, end = "")
        eprint(f"tan_token_l_part: \"{self.tan_token_l_part}\"", end = " ")
        eprint(f"tan_token_r_part: \"{self.tan_token_r_part}\"", end = " ")
        eprint(f"comp_scope: {self.comp_scope.name}", end = " ")
        eprint(TermColor.reset_style.value, end = end_str)
