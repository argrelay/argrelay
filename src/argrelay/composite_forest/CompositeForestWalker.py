from __future__ import annotations

from enum import Enum, auto
from typing import Union

from argrelay.composite_forest.AbstractNodeVisitor import AbstractNodeVisitor
from argrelay.composite_forest.CompositeForest import CompositeForest
from argrelay.composite_forest.CompositeNode import (
    InterpTreeNode,
    TreePathNode,
    FuncTreeNode,
    ZeroArgNode,
    BaseNode,
)


class TraverseDecision(Enum):
    walk_sub_tree = auto()
    skip_sub_tree = auto()


class CompositeForestWalkerAbstract(AbstractNodeVisitor):
    """
    FS_33_76_82_84 composite forest walker

    It implements traversal algorithms which extract various `CompositeInfoType`-s
    (info in a form simplified for specific purpose).

    The original intention is to extract info in the form which `DictTreeWalker` can consume -
    an intermediate phase to migrate to composite forest config while still using existing code
    (existing code relied on data structures processed via `DictTreeWalker`).
    """

    def __init__(
        self,
        composite_forest: CompositeForest,
    ):
        # main input:
        self.tree_roots: dict[str, ZeroArgNode] = composite_forest.tree_roots
        self.curr_node_id: Union[str, None] = None
        self.curr_node: Union[ZeroArgNode, InterpTreeNode, FuncTreeNode, TreePathNode, None] = None
        self.curr_path: list[str] = []

        # internal trackers:
        self.visitor_decision: TraverseDecision = TraverseDecision.walk_sub_tree

    def walk_tree_roots(
        self,
    ) -> None:
        for tree_root_id in self.tree_roots.keys():
            self._descend_and_ascend(
                self.tree_roots,
                tree_root_id,
            )

    def _walk_tree_node(
        self,
    ) -> None:
        self.visit_node(self.curr_node)
        if self.visitor_decision is TraverseDecision.walk_sub_tree:
            self._walk_sub_tree()
        elif self.visitor_decision is TraverseDecision.skip_sub_tree:
            pass
        self.leave_node(self.curr_node)

    def _walk_sub_tree(
        self,
    ):
        if self.curr_node.sub_tree is not None:
            for sub_tree_node_id in self.curr_node.sub_tree.keys():
                self._descend_and_ascend(
                    self.curr_node.sub_tree,
                    sub_tree_node_id,
                )

    def _descend_and_ascend(
        self,
        node_dict: dict[str, BaseNode],
        node_id: str,
    ) -> None:
        """
        Recursive DFS traversal of `composite_forest`.
        """
        # prepare:
        self.curr_path.append(node_id)
        prev_node = self.curr_node
        prev_node_id = self.curr_node_id
        self.curr_node_id = node_id
        # dive:
        self.curr_node = node_dict[node_id]
        self._walk_tree_node()
        # recover:
        del self.curr_path[-1]
        self.curr_node = prev_node
        self.curr_node_id = prev_node_id


class CompositeForestWalkerPrinter(CompositeForestWalkerAbstract):
    """
    Basic composite forest walker which prints node path and node type.
    """

    def __init__(
        self,
        composite_forest: CompositeForest,

    ):
        super().__init__(
            composite_forest,
        )

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._print_info()

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self._print_info()

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._print_info()

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._print_info()

    def _print_info(self):
        print(" / ".join(self.curr_path), end = ": ")
        print(self.curr_node.node_type.name)
        print()
        self.visitor_decision = TraverseDecision.walk_sub_tree
