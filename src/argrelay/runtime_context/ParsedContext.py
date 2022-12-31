from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field

from argrelay.meta_data.SpecialChar import SpecialChar
from argrelay.runtime_context.InputContext import InputContext


@dataclass(frozen = True)
class ParsedContext(InputContext):
    """
    Internal immutable parsed view of :class:`InputContext`
    """

    all_tokens: list[str] = field(init = False)
    sel_token_ipos: int = field(init = False)
    sel_token_l_cpos: int = field(init = False)
    sel_token_r_cpos: int = field(init = False)
    sel_token: str = field(init = False)
    sel_token_l_part: str = field(init = False)
    sel_token_r_part: str = field(init = False)

    def __post_init__(self):
        (
            all_tokens,
            sel_token_ipos,
            sel_token_l_cpos,
            sel_token_r_cpos,
            sel_token,
            sel_token_l_part,
            sel_token_r_part,
        ) = self.parse_input(self)
        object.__setattr__(self, 'all_tokens', all_tokens)
        object.__setattr__(self, 'sel_token_ipos', sel_token_ipos)
        object.__setattr__(self, 'sel_token_l_cpos', sel_token_l_cpos)
        object.__setattr__(self, 'sel_token_r_cpos', sel_token_r_cpos)
        object.__setattr__(self, 'sel_token', sel_token)
        object.__setattr__(self, 'sel_token_l_part', sel_token_l_part)
        object.__setattr__(self, 'sel_token_r_part', sel_token_r_part)

    @classmethod
    def from_instance(cls, input_ctx: InputContext):
        return cls(**dataclasses.asdict(input_ctx))

    @staticmethod
    def parse_input(input_ctx: InputContext):
        """
        Given `|` is the cursor in this command line:
        ```
        some_command some_su|b_command some_arg
        ```
        ```
                            |                       # non-existing char placed to indicate cursor cpos
        0            1                 2            # token ipos
        01234567890123456789 01234567890123456789   # char cpos (the least significant digit)
        ```
        Then function returns:
        (
            [                               # list of all tokens
                "some_command",             # 0
                "some_sub_command",         # 1 (selected token = token pointed by cursor)
                "some_arg",                 # 2
            ],
            1                               # selected token item position (ipos)
            13                              # left-most char position (cpos) of selected token (including it)
            29                              # right-most char position (cpos) of selected token (excluding it)
            "some_sub_command",             # selected token string
            "some_su",                      # selected token left part substring (preceding cursor position)
            "b_command",                    # selected token right part substring (succeeding cursor position)
        )
        """
        # Wrap orig command line into delimiter for simplification:
        command_line = f" {input_ctx.command_line} "
        cursor_cpos = input_ctx.cursor_cpos + 1
        line_len = len(command_line)

        # Init with defaults:
        all_tokens = []
        sel_token_ipos = -1
        sel_token_l_cpos = -1
        sel_token_r_cpos = -1

        # Iterate through all delimiter spans to cut out tokens:
        prev_span_l = -1
        prev_span_r = -1
        token_ipos = 0
        for m in re.finditer(SpecialChar.TokenDelimiter.value, command_line):
            (span_l, span_r) = m.span(0)
            if prev_span_r != -1:
                # New token found between prev and curr delimiter span.
                if prev_span_r <= cursor_cpos <= span_l:
                    # Found selected token (touched by cursor):
                    sel_token_ipos = token_ipos
                    sel_token_l_cpos = prev_span_r
                    sel_token_r_cpos = span_l

                all_tokens.append(command_line[prev_span_r:span_l])
                token_ipos += 1

            prev_span_l = span_l
            prev_span_r = span_r

        if prev_span_r == -1:
            # No delimiter spans found => entire command line is the single token.
            sel_token_ipos = token_ipos
            sel_token_l_cpos = 0
            sel_token_r_cpos = line_len
            all_tokens.append(command_line)

        sel_token = command_line[sel_token_l_cpos:sel_token_r_cpos]
        sel_token_l_part = command_line[sel_token_l_cpos:cursor_cpos]
        sel_token_r_part = command_line[cursor_cpos:sel_token_r_cpos]

        # Adjust for wrapping command line into delimiters:
        if sel_token_l_cpos != -1:
            sel_token_l_cpos -= 1
        if sel_token_r_cpos != -1:
            sel_token_r_cpos -= 1

        return (
            all_tokens,
            sel_token_ipos,
            sel_token_l_cpos,
            sel_token_r_cpos,
            sel_token,
            sel_token_l_part,
            sel_token_r_part,
        )
