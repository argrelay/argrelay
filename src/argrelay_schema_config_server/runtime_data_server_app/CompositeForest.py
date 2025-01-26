from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from argrelay_schema_config_server.runtime_data_server_app.CompositeNode import ZeroArgNode


@dataclass
class CompositeForest:
    """
    Top-level entry object to traverse FS_33_76_82_84 composite forest.

    See also :class:`CompositeForestSchema`.
    """

    tree_roots: dict[str, ZeroArgNode] = field()
