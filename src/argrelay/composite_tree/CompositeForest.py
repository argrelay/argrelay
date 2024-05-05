from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.composite_tree.CompositeNode import ZeroArgNode


@dataclass
class CompositeForest:
    """
    FS_33_76_82_84 composite tree combined into forest.

    See also :class:`CompositeForestSchema`.
    """

    tree_roots: dict[str, ZeroArgNode] = field()
