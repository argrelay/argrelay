from __future__ import annotations

from argrelay.composite_forest.CompositeForest import CompositeForest
from argrelay.composite_forest.CompositeForestWalker import CompositeForestWalkerAbstract, TraverseDecision
from argrelay.composite_forest.CompositeNode import ZeroArgNode, TreePathNode, InterpTreeNode, FuncTreeNode, BaseNode
from argrelay.composite_forest.CompositeNodeType import CompositeNodeType
from argrelay.enum_desc.PluginType import PluginType
from argrelay.plugin_interp.FuncTreeInterpFactory import FuncTreeInterpFactory
from argrelay.plugin_interp.InterpTreeInterpFactory import InterpTreeInterpFactory


def validate_composite_forest(
    composite_forest: CompositeForest,
    plugin_instances: dict[str, "AbstractPluginServer"],
):
    """
    Execute all validations for the composite forest.
    """

    for forest_validator_class in [
        _CompositeForestValidator_zero_arg_node_is_root,
        _CompositeForestValidator_func_tree_node_is_leaf,
        _CompositeForestValidator_zero_arg_node_with_interp_tree_node,
        _CompositeForestValidator_interp_tree_node_with_func_tree_node,
        _CompositeForestValidator_plugin_instance_id,
    ]:
        forest_validator_instance = forest_validator_class(
            composite_forest,
            plugin_instances,
        )
        forest_validator_instance.walk_tree_roots()


class CompositeForestValidatorAbstract(CompositeForestWalkerAbstract):
    """
    Base class to validate FS_33_76_82_84 composite forest.
    """

    def __init__(
        self,
        composite_forest: CompositeForest,
        plugin_instances: dict[str, "AbstractPluginServer"],
    ):
        # main input:
        super().__init__(
            composite_forest,
        )
        self.plugin_instances = plugin_instances


# noinspection PyPep8Naming
class _CompositeForestValidator_zero_arg_node_is_root(CompositeForestValidatorAbstract):
    """
    Validate that:
    *   all `CompositeNodeType.zero_arg_node` are only at tree roots within the composite forest
    *   all tree roots are `CompositeNodeType.zero_arg_node`
    """

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._assert_is_root()

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self._assert_is_not_root()

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._assert_is_not_root()

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._assert_is_not_root()

    def _assert_is_root(self):
        # TODO: replace silent asserts with message describing location of the problem:
        assert len(self.curr_path) == 1
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_is_not_root(self):
        assert len(self.curr_path) != 1
        self.visitor_decision = TraverseDecision.walk_sub_tree


# noinspection PyPep8Naming
class _CompositeForestValidator_func_tree_node_is_leaf(CompositeForestValidatorAbstract):
    """
    Validate that:
    *   all `CompositeNodeType.func_tree_node` are leaves only within the composite forest
    *   all tree leaves are `CompositeNodeType.func_tree_node`
    """

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._assert_is_not_leaf()

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self._assert_is_not_leaf()

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._assert_is_not_leaf()

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._assert_is_leaf()

    def _assert_is_leaf(self):
        assert self.curr_node.sub_tree is None
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_is_not_leaf(self):
        assert self.curr_node.sub_tree is not None
        self.visitor_decision = TraverseDecision.walk_sub_tree


# noinspection PyPep8Naming
class _CompositeForestValidator_zero_arg_node_with_interp_tree_node(CompositeForestValidatorAbstract):
    """
    Validate that:
    *   Descendants of `CompositeNodeType.zero_arg_node` are `CompositeNodeType.interp_tree_node`
        (separated by 0 or N depths of only `CompositeNodeType.tree_path_node`-s)
    *   Ancestor of `CompositeNodeType.interp_tree_node` is `CompositeNodeType.zero_arg_node`
        (separated by 0 or N depths of only `CompositeNodeType.tree_path_node`-s)
    """

    def walk_tree_roots(
        self,
    ) -> None:
        # noinspection PyAttributeOutsideInit
        self.non_tree_path_ancestor_nodes_stack: [BaseNode] = []
        super().walk_tree_roots()

    ####################################################################################################################
    # zero_arg_node

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._push_non_tree_path_node_ancestor()
        self._assert_children_are_interp_tree_node_or_tree_path_node()

    def _leave_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################
    # tree_path_node

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        if self.non_tree_path_ancestor_nodes_stack:
            if self.non_tree_path_ancestor_nodes_stack[-1].node_type is CompositeNodeType.zero_arg_node:
                self._assert_children_are_interp_tree_node_or_tree_path_node()

    ####################################################################################################################
    # interp_tree_node

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._assert_non_tree_path_node_ancestor_is_zero_arg_node()
        self._push_non_tree_path_node_ancestor()

    def _leave_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################
    # func_tree_node

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._push_non_tree_path_node_ancestor()

    def _leave_func_tree_node(self, node: FuncTreeNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################

    def _assert_is_leaf(self):
        assert self.curr_node.sub_tree is None
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_children_are_interp_tree_node_or_tree_path_node(self):
        assert self.curr_node.sub_tree is not None
        for child_node in self.curr_node.sub_tree.values():
            assert (
                child_node.node_type is CompositeNodeType.interp_tree_node
                or
                child_node.node_type is CompositeNodeType.tree_path_node
            )
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_non_tree_path_node_ancestor_is_zero_arg_node(self):
        assert self.non_tree_path_ancestor_nodes_stack[-1].node_type is CompositeNodeType.zero_arg_node
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _push_non_tree_path_node_ancestor(self):
        assert self.curr_node.node_type is not CompositeNodeType.tree_path_node
        self.non_tree_path_ancestor_nodes_stack.append(self.curr_node)
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _pop_non_tree_path_node_ancestor(self):
        self.non_tree_path_ancestor_nodes_stack.pop()
        self.visitor_decision = TraverseDecision.walk_sub_tree


# noinspection PyPep8Naming
class _CompositeForestValidator_interp_tree_node_with_func_tree_node(CompositeForestValidatorAbstract):
    """
    Validate that:
    *   Descendants of `CompositeNodeType.interp_tree_node` are `CompositeNodeType.func_tree_node`
        (separated by 0 or N depths of only `CompositeNodeType.tree_path_node`-s)
    *   Ancestor of `CompositeNodeType.func_tree_node` is `CompositeNodeType.interp_tree_node`
        (separated by 0 or N depths of only `CompositeNodeType.tree_path_node`-s)
    """

    def walk_tree_roots(
        self,
    ) -> None:
        # noinspection PyAttributeOutsideInit
        self.non_tree_path_ancestor_nodes_stack: [BaseNode] = []
        super().walk_tree_roots()

    ####################################################################################################################
    # zero_arg_node

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._push_non_tree_path_node_ancestor()

    def _leave_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################
    # tree_path_node

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        if self.non_tree_path_ancestor_nodes_stack:
            if self.non_tree_path_ancestor_nodes_stack[-1].node_type is CompositeNodeType.interp_tree_node:
                self._assert_children_are_func_tree_node_or_tree_path_node()

    ####################################################################################################################
    # interp_tree_node

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._push_non_tree_path_node_ancestor()
        self._assert_children_are_func_tree_node_or_tree_path_node()

    def _leave_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################
    # func_tree_node

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._assert_non_tree_path_node_ancestor_is_interp_tree_node()
        self._push_non_tree_path_node_ancestor()

    def _leave_func_tree_node(self, node: FuncTreeNode) -> None:
        self._pop_non_tree_path_node_ancestor()

    ####################################################################################################################

    def _assert_is_leaf(self):
        assert self.curr_node.sub_tree is None
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_children_are_func_tree_node_or_tree_path_node(self):
        assert self.curr_node.sub_tree is not None
        for child_node in self.curr_node.sub_tree.values():
            assert (
                child_node.node_type is CompositeNodeType.func_tree_node
                or
                child_node.node_type is CompositeNodeType.tree_path_node
            )
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_non_tree_path_node_ancestor_is_interp_tree_node(self):
        assert self.non_tree_path_ancestor_nodes_stack[-1].node_type is CompositeNodeType.interp_tree_node
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _push_non_tree_path_node_ancestor(self):
        assert self.curr_node.node_type is not CompositeNodeType.tree_path_node
        self.non_tree_path_ancestor_nodes_stack.append(self.curr_node)
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _pop_non_tree_path_node_ancestor(self):
        self.non_tree_path_ancestor_nodes_stack.pop()
        self.visitor_decision = TraverseDecision.walk_sub_tree


# noinspection PyPep8Naming
class _CompositeForestValidator_plugin_instance_id(CompositeForestValidatorAbstract):
    """
    Validate that:
    *   all `CompositeNodeType.zero_arg_node`-s use `PluginType.InterpFactoryPlugin`
    *   all `CompositeNodeType.interp_tree_node`-s use `PluginType.InterpFactoryPlugin`
    """

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self._assert_interp_factory_plugin(InterpTreeInterpFactory)

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self._assert_nothing()

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self._assert_interp_factory_plugin(FuncTreeInterpFactory)

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self._assert_nothing()

    def _assert_nothing(self):
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_interp_factory_plugin(self, base_class):
        assert self.curr_node.plugin_instance_id is not None

        plugin_instance = self.plugin_instances[self.curr_node.plugin_instance_id]

        assert plugin_instance.get_plugin_type() is PluginType.InterpFactoryPlugin

        # This validation may be relaxed, but now it is how working composite forests are built:
        assert issubclass(type(plugin_instance), base_class)

        self.visitor_decision = TraverseDecision.walk_sub_tree
