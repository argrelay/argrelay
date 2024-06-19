from __future__ import annotations

from argrelay.composite_tree.CompositeNode import BaseNode, ZeroArgNode, InterpTreeNode, FuncTreeNode, TreePathNode


class AbstractNodeVisitor:

    def visit_node(
        self,
        node: BaseNode,
    ):
        if False:
            pass
        elif isinstance(node, ZeroArgNode):
            self._visit_ZeroArgNode(node)
        elif isinstance(node, TreePathNode):
            self._visit_TreePathNode(node)
        elif isinstance(node, InterpTreeNode):
            self._visit_InterpTreeNode(node)
        elif isinstance(node, FuncTreeNode):
            self._visit_FuncTreeNode(node)
        else:
            raise NotImplementedError(node.node_type.name)

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        raise NotImplementedError()

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        raise NotImplementedError()

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        raise NotImplementedError()

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        raise NotImplementedError()
