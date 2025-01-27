from enum import (
    auto,
    Enum,
)


class CompositeNodeType(Enum):
    """
    FS_33_76_82_84 composite forest node types.
    """

    zero_arg_node = auto()
    """
    See FS_42_76_93_51 very first zero arg mapping interp.

    It is also related to FS_15_79_76_85 line processor
    (which may potentially be merged with FS_42_76_93_51 zero arg interp).

    TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor
    """

    interp_tree_node = auto()
    """
    See FS_01_89_09_24 interp tree.
    """

    func_tree_node = auto()
    """
    See FS_26_43_73_72 func tree.
    """

    tree_path_node = auto()
    """
    The function of this node is to group other nodes as children under the same tree path.
    """
