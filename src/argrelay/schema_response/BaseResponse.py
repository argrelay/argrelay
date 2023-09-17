from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BaseResponse:
    """
    """

    all_tokens: list[str] = field()
    """
    Copy from `ParsedContext.all_tokens` - command line args.
    """

    consumed_tokens: list[int] = field()
    """
    Copy from `InterpContext.consumed_tokens` -
    indexes into `all_tokens` pointing to tokens consumed during interpretation.
    """
