from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InitControl:
    """
    Implements `init_control` (FS_46_96_59_05).
    """

    init_types_to_values: dict[str, str] = field()
