from argrelay.composite_tree.CompositeForest import CompositeForest
from argrelay.composite_tree.CompositeNode import ZeroArgNode, TreePathNode, InterpTreeNode, FuncTreeNode
from argrelay.composite_tree.CompositeTreeWalker import CompositeTreeWalkerAbstract, TraverseDecision


def validate_composite_tree(
    composite_forest: CompositeForest,
):
    """
    Execute all validations for the composite forest.
    """

    for forest_validator in [
        _CompositeTreeValidator_zero_arg_node(composite_forest),
    ]:
        forest_validator.walk_tree_roots()


class CompositeTreeValidatorAbstract(CompositeTreeWalkerAbstract):
    """
    Base class to validate FS_33_76_82_84 composite tree.
    """

    def __init__(
        self,
        composite_forest: CompositeForest,
    ):
        # main input:
        super().__init__(
            composite_forest,
        )


# noinspection PyPep8Naming
class _CompositeTreeValidator_zero_arg_node(CompositeTreeValidatorAbstract):
    """
    Validate that all `CompositeNodeType.zero_arg_node` are only at tree roots within the composite forest.
    """

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        self._assert_is_root()

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self._assert_is_not_root()

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        self._assert_is_not_root()

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        self._assert_is_not_root()

    def _assert_is_root(self):
        assert len(self.curr_path) == 1
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _assert_is_not_root(self):
        assert len(self.curr_path) != 1
        self.visitor_decision = TraverseDecision.walk_sub_tree
