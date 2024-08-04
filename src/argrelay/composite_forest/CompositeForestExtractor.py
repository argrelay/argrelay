from __future__ import annotations

from typing import Union

from argrelay.composite_forest.CompositeForest import CompositeForest
from argrelay.composite_forest.CompositeForestWalker import CompositeForestWalkerAbstract, TraverseDecision
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.CompositeNode import InterpTreeNode, ZeroArgNode, TreePathNode, FuncTreeNode
from argrelay.composite_forest.DictTreeWalker import surrogate_node_id_


def extract_tree_abs_path_to_interp_id(
    composite_forest: CompositeForest,
    func_id: str,
) -> dict:
    """
    Extracts `CompositeInfoType.tree_abs_path_to_interp_id`.
    """

    tree_walker = _CompositeForestWalker_tree_abs_path_to_interp_id(
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

    tree_walker = _CompositeForestWalker_zero_arg_interp_tree(
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

    tree_walker = _CompositeForestWalker_jump_tree(
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

    tree_walker = _CompositeForestWalker_interp_tree(
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

    tree_walker = _CompositeForestWalker_func_tree(
        composite_forest,
        CompositeInfoType.func_tree,
        plugin_instance_id,
    )
    tree_walker.walk_tree_roots()

    return tree_walker.func_tree


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


class CompositeForestExtractorAbstract(CompositeForestWalkerAbstract):
    """
    Base class for extractor which takes specific `CompositeInfoType` from the FS_33_76_82_84 composite forest.
    """

    def __init__(
        self,
        composite_forest: CompositeForest,
        info_type: CompositeInfoType,
    ):
        # main input:
        super().__init__(
            composite_forest,
        )

        self.info_type = info_type


# noinspection PyPep8Naming
class _CompositeForestWalker_tree_abs_path_to_interp_id(CompositeForestExtractorAbstract):

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

        # results:
        self.tree_abs_path_to_interp_id: dict = {}

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree
        # FS_91_88_07_23: jump tree:
        # Similar to `jump_path`-s, next `plugin_instance_id` configuration was drop in favour of
        # deriving such plugin automatically:
        self.next_jump_plugin_instance_id = self.curr_node.plugin_instance_id

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        if self.curr_node.func_id == self.func_id:
            assert self.curr_path[-1] == surrogate_node_id_
            assert self.curr_node.sub_tree is None
            _put_value_into_dict_path(
                self.next_jump_plugin_instance_id,
                self.curr_path[:-1],
                self.tree_abs_path_to_interp_id,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeForestWalker_zero_arg_interp_tree(CompositeForestExtractorAbstract):

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

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
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

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeForestWalker_jump_tree(CompositeForestExtractorAbstract):

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

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        assert len(self.curr_path) > 0
        # FS_91_88_07_23: jump tree:
        # So far, all `jump_path`-s are the paths leading to `curr_node` excluding that last `curr_node` step.
        # Therefore, their configuration was drop in favour of deriving `jump_path` automatically:
        jump_path = self.curr_path[:-1]
        _put_value_into_dict_path(
            jump_path,
            self.curr_path,
            self.jump_tree,
        )
        self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeForestWalker_interp_tree(CompositeForestExtractorAbstract):

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

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        if self.curr_node.plugin_instance_id == self.plugin_instance_id:
            self.curr_parent_plugin_instance_id = self.plugin_instance_id
            self.visitor_decision = TraverseDecision.walk_sub_tree
        else:
            self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        if self.curr_parent_plugin_instance_id == self.plugin_instance_id:
            _put_value_into_dict_path(
                self.curr_node.plugin_instance_id,
                self.curr_path,
                self.interp_tree,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        self.visitor_decision = TraverseDecision.skip_sub_tree


# noinspection PyPep8Naming
class _CompositeForestWalker_func_tree(CompositeForestExtractorAbstract):

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

    def _visit_zero_arg_node(self, node: ZeroArgNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_tree_path_node(self, node: TreePathNode) -> None:
        self.visitor_decision = TraverseDecision.walk_sub_tree

    def _visit_interp_tree_node(self, node: InterpTreeNode) -> None:
        if self.curr_node.plugin_instance_id == self.plugin_instance_id:
            self.curr_parent_plugin_instance_id = self.plugin_instance_id
            self.visitor_decision = TraverseDecision.walk_sub_tree
        else:
            self.visitor_decision = TraverseDecision.skip_sub_tree

    def _visit_func_tree_node(self, node: FuncTreeNode) -> None:
        if self.curr_parent_plugin_instance_id == self.plugin_instance_id:
            _put_value_into_dict_path(
                self.curr_node.func_id,
                self.curr_path,
                self.func_tree,
            )
        self.visitor_decision = TraverseDecision.skip_sub_tree
