from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Union

default_tree_leaf_ = ""


class TreeWalker:
    """
    Helper with logic to traverse tree - used to implement:
    *   FS_01_89_09_24 interp tree
    *   FS_26_43_73_72 func tree
    *   FS_91_88_07_23 jump tree
    *   FS_33_76_82_84 global tree

    The tree is specified as `dict` (normally, in config).
    """

    def __init__(
        self,
        tree_name: str,
        tree_dict: dict,
    ):
        self.tree_name = tree_name
        self.tree_dict = tree_dict
        self.leaf_type = None

    def build_str_leaves_paths(
        self,
    ) -> dict[str, list[list[str]]]:
        """
        For each named leaf (becomes key) provide its paths in the tree.

        Each named leaf can have several paths in the tree (leaves with the same name).

        Use case:
        *   We know `func_id`, we need to know which FS_26_43_73_72 func tree paths it is registered under.
        """
        tree_paths: dict[str, list[list[str]]] = {}
        self.leaf_type = str
        self._build_leaves_sub_paths(
            [],
            self.tree_dict,
            tree_paths,
            self._handle_str_leaf,
        )
        return tree_paths

    # TODO: Unused (and, apparently, it wasn't used in the past).
    def build_tuple_leaves_paths(
        self,
    ) -> dict[tuple[str, ...], list[list[str]]]:
        """
        For each leaf value (`list` in tree leaf becomes `tuple` key in the map) provide its paths in the tree.

        Each leaf (its `tuple` converted from `list`) can have several paths in the tree (leaves with the same value).

        In tree, leaf is a `list`.
        In map, leaf becomes `tuple` (as a key for `dict`).

        Use case:
        *   We know tree path (tuple) defined in the nodes, we need to know all tree paths where same path is defined.
            (not a real use case as it is unused TODO: clean up)
        """
        tree_paths: dict[tuple[str, ...], list[list[str]]] = {}
        self.leaf_type = list
        self._build_leaves_sub_paths(
            [],
            self.tree_dict,
            tree_paths,
            self._handle_list_leaf,
        )
        return tree_paths

    def build_paths_to_paths(
        self
    ) -> dict[tuple[str, ...], tuple[str, ...]]:
        """
        Map each path in the tree into path specified in the leaf (`list` in tree leaf becomes `tuple` key in the map).

        In tree, leaf is a `list`.
        In map, leaf becomes `tuple` (as a key for `dict`).

        Use case:
        *   We know curr tree path (tuple), we need to know next tree path where to jump (FS_91_88_07_23 jump tree).
        """

        paths_to_paths: dict[tuple[str, ...], tuple[str, ...]] = {}
        self.leaf_type = list
        self._build_paths_to_paths(
            [],
            self.tree_dict,
            paths_to_paths,
        )
        return paths_to_paths

    def _build_leaves_sub_paths(
        self,
        curr_path: list[str],
        sub_tree: Union[str, list, dict],
        output_leaves_paths: dict[Union[str, tuple[str, ...]], list[list[str]]],
        handle_leaf: Callable[
            [
                list[str],
                Union[str, list, dict],
                dict[Union[str, tuple[str, ...]],
                list[list[str]]],
            ],
            None,
        ],
    ):
        if isinstance(sub_tree, dict):
            for node_id in sub_tree:
                tree_node = sub_tree[node_id]
                if node_id == default_tree_leaf_:
                    self._build_leaves_sub_paths(
                        curr_path,
                        tree_node,
                        output_leaves_paths,
                        handle_leaf,
                    )
                else:
                    next_leaf_path = deepcopy(curr_path)
                    next_leaf_path.append(node_id)
                    self._build_leaves_sub_paths(
                        next_leaf_path,
                        tree_node,
                        output_leaves_paths,
                        handle_leaf,
                    )
        elif isinstance(sub_tree, self.leaf_type):
            handle_leaf(
                curr_path,
                sub_tree,
                output_leaves_paths,
            )
        else:
            self._raise_on_wrong_type(curr_path, sub_tree)

    def _build_paths_to_paths(
        self,
        curr_path: list[str],
        sub_tree: Union[list, dict],
        output_paths_to_paths: dict[tuple[str, ...], tuple[str, ...]],
    ):
        if isinstance(sub_tree, dict):
            for node_id in sub_tree:
                tree_node = sub_tree[node_id]
                if node_id == default_tree_leaf_:
                    self._build_paths_to_paths(
                        curr_path,
                        tree_node,
                        output_paths_to_paths,
                    )
                else:
                    next_leaf_path = deepcopy(curr_path)
                    next_leaf_path.append(node_id)
                    self._build_paths_to_paths(
                        next_leaf_path,
                        tree_node,
                        output_paths_to_paths,
                    )
        elif isinstance(sub_tree, self.leaf_type):
            self._verify_list_str(curr_path, sub_tree)
            output_paths_to_paths[tuple(curr_path)] = tuple(sub_tree)
        else:
            self._raise_on_wrong_type(curr_path, sub_tree)

    def _handle_str_leaf(
        self,
        curr_path: list[str],
        leaf_node: str,
        output_leaves_paths: dict[str, list[list[str]]],
    ) -> None:
        if leaf_node == default_tree_leaf_:
            if len(curr_path) < 1:
                raise ValueError(
                    f"{self.tree_name}: tree path `{curr_path}` must contain at least one step to use leaf `{default_tree_leaf_}`"
                )
            leaf_id = curr_path[-1]
            leaf_path = curr_path[:-1]
        else:
            leaf_id = leaf_node
            leaf_path = deepcopy(curr_path)

        if leaf_id in output_leaves_paths:
            output_leaves_paths[leaf_id].append(leaf_path)
        else:
            output_leaves_paths[leaf_id] = [leaf_path]

    def _handle_list_leaf(
        self,
        curr_path: list[str],
        leaf_node: list,
        output_leaves_paths: dict[tuple[str, ...], list[list[str]]],
    ) -> None:
        """
        Convert `list` leaf node to `tuple` to be used as key in `output_leaves_paths` `dict`.
        """
        self._verify_list_str(curr_path, leaf_node)

        leaf_id = tuple(leaf_node)
        leaf_path = deepcopy(curr_path)

        if leaf_id in output_leaves_paths:
            output_leaves_paths[leaf_id].append(leaf_path)
        else:
            output_leaves_paths[leaf_id] = [leaf_path]

    def _verify_list_str(
        self,
        curr_path: list[str],
        list_value: list,
    ):
        if not all(isinstance(leaf_list_item, str) for leaf_list_item in list_value):
            raise ValueError(
                f"{self.tree_name}: tree path `{curr_path}` leaf list must contain only `str`"
            )

    def _raise_on_wrong_type(
        self,
        curr_path: list[str],
        typed_value,
    ):
        raise ValueError(
            f"{self.tree_name}: tree path `{curr_path}` leaf type `{typed_value.__class__.__name__}` is neither `{self.leaf_type.__name__}` nor `dict`"
        )
