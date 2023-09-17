from __future__ import annotations

from enum import Enum, auto

from argrelay.enum_desc.SpecialChar import SpecialChar


class TokenType(Enum):
    """
    Interpretation of tokens from command line into args (or their parts):
    *   `PosArg` = positional is specified by relative position in the command line (list of args).
    *   `KeyArg` + `ValArg` = named args are specified by pair of tokens: keyword arg token followed by value arg token.
    """

    """
    Positional arg
    """
    PosArg = auto()

    """
    Keyword arg - must have special format (e.g. ending with `:`).
    """
    KeyArg = auto()

    """
    Value arg - must be followed by `KeyArg`
    """
    ValArg = auto()


def get_token_type(all_tokens: list[str], token_ipos: int) -> TokenType:
    # TODO: POC: FS_20_88_05_60: Either remove it or implement properly: just testing named args:
    if all_tokens[token_ipos].endswith(SpecialChar.KeyValueDelimiter.value):
        return TokenType.KeyArg
    else:
        if token_ipos > 0:
            if not all_tokens[token_ipos - 1].endswith(SpecialChar.KeyValueDelimiter.value):
                return TokenType.PosArg
            else:
                return TokenType.ValArg
        else:
            return TokenType.PosArg
