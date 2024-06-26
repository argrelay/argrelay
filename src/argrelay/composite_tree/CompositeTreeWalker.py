from __future__ import annotations

from enum import Enum, auto
from typing import Union

from argrelay.composite_tree.AbstractNodeVisitor import AbstractNodeVisitor
from argrelay.composite_tree.CompositeForest import CompositeForest
from argrelay.composite_tree.CompositeInfoType import CompositeInfoType
from argrelay.composite_tree.CompositeNode import (
    InterpTreeNode,
    TreePathNode,
    FuncTreeNode,
    ZeroArgNode,
    BaseNode,
)
from argrelay.composite_tree.DictTreeWalker import surrogate_node_id_


class TraverseDecision(Enum):
    walk_sub_tree = auto()
    skip_sub_tree = auto()


def _put_value_into_dict_path(
    given_value,
    given_path: list[str],
    target_dict: dict,
) -> None:
    curr_sub_dict: dict = target_dict

    assert len(given_path) > 0

    if len(given_path) > 1:
        for path_step in given_path[:-1]:
            if path_step not in curr_sub_dict:
                # create:
                curr_sub_dict[path_step] = {}
            curr_sub_dict = curr_sub_dict[path_step]

    curr_sub_dict[given_path[-1]] = given_value


class AbstractCompositeTreeWalker(AbstractNodeVisitor):
    """
    FS_33_76_82_84 composite tree walker

    It implements traversal algorithms which extract various `CompositeInfoType`-s
    (info in a form simplified for specific purpose).

    The original intention is to extract info in the form which `DictTreeWalker` can consume -
    an intermediate phase to migrate to composite tree config while still using existing code
    (existing code relied on data structures processed via `DictTreeWalker`).
    """

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
    ):
        # main input:
        self.tree_roots: dict[str, ZeroArgNode] = composite_forest.tree_roots
        self.info_type: CompositeInfoType = info_type
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
        traverse_decision = self._process_tree_node()
        if traverse_decision is TraverseDecision.walk_sub_tree:
            self._walk_sub_tree()
        elif traverse_decision is TraverseDecision.skip_sub_tree:
            pass

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
        Recursive DFS traversal of `composite_tree`.
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

    def _process_tree_node(
        self,
    ) -> TraverseDecision:
        self.visit_node(self.curr_node)
        return self.visitor_decision


# noinspection PyPep8Naming
class _CompositeTreeWalker_tree_abs_path_to_interp_id(AbstractCompositeTreeWalker):

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
        func_id: Union[str, None],
    ):
        # main input:
        super().__init__(
            composite_forest,
            info_type,
        )

        # `info_type`-specific input:
        self.func_id: Union[str, None] = func_id

        # internal trackers:
        self.last_next_interp: Union[InterpTreeNode.NextInterp, None] = None

        # results:
        self.tree_abs_path_to_interp_id: dict = {}

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        self.last_next_interp = self.curr_node.next_interp
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        if self.curr_node.func_id == self.func_id:
            assert self.last_next_interp is not None
            assert self.curr_path[-1] == surrogate_node_id_
            assert self.curr_node.sub_tree is None
            _put_value_into_dict_path(
                self.last_next_interp.plugin_instance_id,
                self.curr_path[:-1],
                self.tree_abs_path_to_interp_id,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeTreeWalker_zero_arg_interp_tree(AbstractCompositeTreeWalker):

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
    ):
        # main input:
        super().__init__(
            composite_forest,
            info_type,
        )

        # results:
        self.zero_arg_interp_tree: dict = {}

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        assert len(self.curr_path) == 1
        _put_value_into_dict_path(
            # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor:
            #       There could be multiple `zero_arg_node`-s each with its own interp,
            #       but now, there is only one interp selected by `first_interp_factory_id`.
            #       In fact, `first_interp_factory_id` must be per zero arg - see FS_15_79_76_85 line processor.
            self.curr_node.plugin_instance_id,
            self.curr_path,
            self.zero_arg_interp_tree,
        )
        self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeTreeWalker_jump_tree(AbstractCompositeTreeWalker):

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
    ):
        # main input:
        super().__init__(
            composite_forest,
            info_type,
        )

        # results:
        self.jump_tree: dict = {}

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        assert len(self.curr_path) > 0
        _put_value_into_dict_path(
            self.curr_node.next_interp.jump_path,
            self.curr_path,
            self.jump_tree,
        )
        self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeTreeWalker_interp_tree(AbstractCompositeTreeWalker):

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
        plugin_instance_id: Union[str, None],
    ):
        # main input:
        super().__init__(
            composite_forest,
            info_type,
        )

        # `info_type`-specific input:
        self.plugin_instance_id: Union[str, None] = plugin_instance_id

        # internal trackers:
        self.curr_parent_plugin_instance_id: Union[str, None] = None

        # results:
        self.interp_tree: dict = {}

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        if self.curr_node.plugin_instance_id == self.plugin_instance_id:
            self.curr_parent_plugin_instance_id = self.plugin_instance_id
            self.visitor_decision = TraverseDecision.walk_sub_tree
        else:
            self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        if self.curr_parent_plugin_instance_id == self.plugin_instance_id:
            _put_value_into_dict_path(
                self.curr_node.plugin_instance_id,
                self.curr_path,
                self.interp_tree,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeTreeWalker_func_tree(AbstractCompositeTreeWalker):

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
        plugin_instance_id: Union[str, None],
    ):
        # main input:
        super().__init__(
            composite_forest,
            info_type,
        )

        # `info_type`-specific input:
        self.plugin_instance_id: Union[str, None] = plugin_instance_id

        # internal trackers:
        self.curr_parent_plugin_instance_id: Union[str, None] = None

        # results:
        self.func_tree: dict = {}

    # noinspection PyPep8Naming
    def _visit_ZeroArgNode(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_TreePathNode(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    # noinspection PyPep8Naming
    def _visit_InterpTreeNode(self, node: InterpTreeNode) -> None:
        if self.curr_node.plugin_instance_id == self.plugin_instance_id:
            self.curr_parent_plugin_instance_id = self.plugin_instance_id
            self.visitor_decision = TraverseDecision.walk_sub_tree
        else:
            self.visitor_decision = TraverseDecision.skip_sub_tree

    # noinspection PyPep8Naming
    def _visit_FuncTreeNode(self, node: FuncTreeNode) -> None:
        if self.curr_parent_plugin_instance_id == self.plugin_instance_id:
            _put_value_into_dict_path(
                self.curr_node.func_id,
                self.curr_path,
                self.func_tree,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree


def extract_tree_abs_path_to_interp_id(
    composite_forest: CompositeForest,
    func_id: str,
) -> dict:
    """
    Extracts `CompositeInfoType.tree_abs_path_to_interp_id`.
    """

    tree_walker = _CompositeTreeWalker_tree_abs_path_to_interp_id(
        composite_forest,
        CompositeInfoType.tree_abs_path_to_interp_id,
        func_id,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.tree_abs_path_to_interp_id


def extract_zero_arg_interp_tree(
    composite_forest: CompositeForest,
) -> dict:
    """
    Extracts `CompositeInfoType.zero_arg_interp_tree`.
    """

    tree_walker = _CompositeTreeWalker_zero_arg_interp_tree(
        composite_forest,
        CompositeInfoType.zero_arg_interp_tree,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.zero_arg_interp_tree


def extract_jump_tree(
    composite_forest: CompositeForest,
) -> dict:
    """
    Extracts `CompositeInfoType.jump_tree`.
    """

    tree_walker = _CompositeTreeWalker_jump_tree(
        composite_forest,
        CompositeInfoType.jump_tree,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.jump_tree


def extract_interp_tree(
    composite_forest: CompositeForest,
    plugin_instance_id: str,
) -> dict:
    """
    Extracts `CompositeInfoType.interp_tree`.
    """

    tree_walker = _CompositeTreeWalker_interp_tree(
        composite_forest,
        CompositeInfoType.interp_tree,
        plugin_instance_id,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.interp_tree


def extract_func_tree(
    composite_forest: CompositeForest,
    plugin_instance_id: str,
) -> dict:
    """
    Extracts `CompositeInfoType.func_tree`.
    """

    tree_walker = _CompositeTreeWalker_func_tree(
        composite_forest,
        CompositeInfoType.func_tree,
        plugin_instance_id,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.func_tree
