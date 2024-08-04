from __future__ import annotations

from argrelay.composite_forest.CompositeNode import BaseNode, ZeroArgNode, InterpTreeNode, FuncTreeNode, TreePathNode


class AbstractNodeVisitor:

    def visit_node(
        self,
        base_node: BaseNode,
    ):
        """
        It is called for the given `base_node` _before_ traversing `sub_tree`.
        """
        if isinstance(base_node, ZeroArgNode):
            self._visit_zero_arg_node(base_node)
        elif isinstance(base_node, TreePathNode):
            self._visit_tree_path_node(base_node)
        elif isinstance(base_node, InterpTreeNode):
            self._visit_interp_tree_node(base_node)
        elif isinstance(base_node, FuncTreeNode):
            self._visit_func_tree_node(base_node)
        else:
            raise NotImplementedError(base_node.node_type.name)

    def leave_node(
        self,
        base_node: BaseNode,
    ):
        """
        It is called for the given `base_node` _after_ traversing `sub_tree`.

        It can be called to recover some state which was altered for the duration of `sub_tree` traversal.
        """
        if isinstance(base_node, ZeroArgNode):
            self._leave_zero_arg_node(base_node)
        elif isinstance(base_node, TreePathNode):
            self._leave_tree_path_node(base_node)
        elif isinstance(base_node, InterpTreeNode):
            self._leave_interp_tree_node(base_node)
        elif isinstance(base_node, FuncTreeNode):
            self._leave_func_tree_node(base_node)
        else:
            raise NotImplementedError(base_node.node_type.name)

    ####################################################################################################################

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        raise NotImplementedError()

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        raise NotImplementedError()

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        raise NotImplementedError()

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        raise NotImplementedError()

    ####################################################################################################################

    def _leave_zero_arg_node(self, node: ZeroArgNode) -> None:
        pass

    def _leave_tree_path_node(self, node: TreePathNode) -> None:
        pass

    def _leave_interp_tree_node(self, node: InterpTreeNode) -> None:
        pass

    def _leave_func_tree_node(self, node: FuncTreeNode) -> None:
        pass

    ####################################################################################################################
