from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InterpTreeContext:
    """
    Provides context to interp (`AbstractInterp`) about FS_01_89_09_24 interp tree.

    Takes part in implementation of FS_01_89_09_24 interp tree.
    """

    # TODO: Get rid of the `InterpTreeContext` wrapper and put into `InterpContext` directly?
    interp_tree_path: tuple[str, ...] = field()
