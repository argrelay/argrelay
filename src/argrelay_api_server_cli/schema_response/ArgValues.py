from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ArgValues:
    """
    See also :class:`ArgValuesSchema`.
    """

    arg_values: list[str] = field()
    """
    Values suggested by `ServerAction.ProposeArgValues`.
    """
