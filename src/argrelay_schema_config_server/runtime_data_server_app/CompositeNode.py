from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import Union

from argrelay_schema_config_server.runtime_data_server_app.CompositeNodeType import (
    CompositeNodeType,
)


@dataclass
class BaseNode:
    """
    Base class for all FS_33_76_82_84 composite forest node types.

    See also :class:`BaseNodeSchema`.
    """

    node_type: CompositeNodeType = field()
    """
    See `CompositeNodeType`.
    """

    sub_tree: Union[dict[str, BaseNode], None] = field()


@dataclass
class ZeroArgNode(BaseNode):
    """
    See FS_42_76_93_51 very first zero arg mapping interp.
    """

    plugin_instance_id: str = field()


@dataclass
class TreePathNode(BaseNode):
    """
    See `CompositeNodeType.tree_path_node`.
    """


@dataclass
class InterpTreeNode(BaseNode):
    """
    See FS_01_89_09_24 interp tree.
    """

    plugin_instance_id: str = field()


@dataclass
class FuncTreeNode(BaseNode):
    """
    See FS_26_43_73_72 func tree.
    """

    func_id: str = field()
