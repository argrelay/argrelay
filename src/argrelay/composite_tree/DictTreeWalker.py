from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Union

from argrelay.composite_tree.CompositeInfoType import CompositeInfoType

surrogate_node_id_ = ""
"""
Surrogate node id allows "planting" entire sub-tree in place of itself.

But the node that this surrogate node id identifies is not removed (the tree is not modified) -
functionally that node must be present. It is only excluded from the path to access its sub-tree.

Surrogate node id is skipped and does not affect (e.g.) command line
(as trees often used to construct path which would be used to select its nodes via command line).

Surrogate node id can also simplify representation of trees with leaf value only
(as replacement of `dict` type where leaf type is used directly), for example,
instead of:
```yaml
some_tree:
    "": leaf_value
```
use this (no `dict`):
```yaml
some_tree: leaf_value
```
"""

surrogate_tree_leaf_ = ""
"""
Surrogate tree leaf can be used as `dict` value to instruct to use `dict` key instead of `dict` value.

For example, this trees are equivalent:
```yaml
some_tree:
    "some_value": ""
```
use this (no `dict`):
```yaml
some_tree: "some_value"
```
"""

def normalize_tree(
    input_tree: Union[dict, str],
) -> dict:
    """
    Transform `input_tree` to some equivalent form which makes all trees comparable.

    *   If `input_tree` is not `dict`, make it `dict` by inserting using `surrogate_node_id_`.
    *   If `input_tree` has only one node with `surrogate_node_id_`, collapse that layer.
    *   Tree of 0 depth with (non-`dict`) is transformed to `dict` with `surrogate_tree_leaf_`.

    NOTE: `input_tree` of depth 0 with `str` leave equal to `surrogate_tree_leaf_` is invalid.

    NOTE: These two dicts are equivalent:
    *   with `surrogate_tree_leaf_`: { "some_value": "" }
    *   with `surrogate_node_id_`: { "": "some_value" }
    To resolve the ambiguity, "some_value" is transformed using `surrogate_node_id_`.
    """

    return _normalize_tree(input_tree, 0)

def _normalize_tree(
    input_tree: Union[dict, str],
    tree_depth: int,
) -> Union[dict, str]:

    output_tree: dict = {}

    if isinstance(input_tree, str):
        if input_tree == surrogate_tree_leaf_:
            if tree_depth != 0:
                return input_tree
            else:
                raise ValueError(f"`input_tree` with single leaf `{surrogate_node_id_}` is invalid.")
        else:
            if tree_depth != 0:
                return input_tree
            else:
                output_tree[surrogate_node_id_] = input_tree
    elif isinstance(input_tree, dict):
        if len(input_tree) == 1 and surrogate_node_id_ in input_tree:
            output_tree.update(_normalize_tree(input_tree[surrogate_node_id_], tree_depth + 1))
        else:
            for node_id in input_tree:
                output_tree[node_id] = _normalize_tree(input_tree[node_id], tree_depth + 1)
    else:
        raise ValueError(f"unexpected `input_tree` type: {type(input_tree)}")

    return output_tree


class DictTreeWalker:
    """
    This tree walker is used to build various data structures extracted from (simple) `dict` trees:
    *   FS_01_89_09_24 interp tree
    *   FS_26_43_73_72 func tree
    *   FS_91_88_07_23 jump tree

    As opposed to (complex) FS_33_76_82_84 `composite_tree` (with node types),
    the `dict` trees are specified in config via `dict` without node types -
    only node id names (as `dict` keys) and tree leaves (as `str` or `list`).

    These simple trees can also be extracted from FS_33_76_82_84 `composite_tree` via `CompositeWalker`
    (where each node has its type and additional info, not just path step name and value at tree leaves).
    """

    def __init__(
        self,
        info_type: CompositeInfoType,
        tree_dict: dict,
    ):
        self.info_type = info_type
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
                if node_id == surrogate_node_id_:
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
                if node_id == surrogate_node_id_:
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
        if leaf_node == surrogate_tree_leaf_:
            if len(curr_path) < 1:
                raise ValueError(
                    f"{self.info_type}: tree path `{curr_path}` must contain at least one step to use leaf `{surrogate_tree_leaf_}`"
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
                f"{self.info_type}: tree path `{curr_path}` leaf list must contain only `str`"
            )

    def _raise_on_wrong_type(
        self,
        curr_path: list[str],
        typed_value,
    ):
        raise ValueError(
            f"{self.info_type}: tree path `{curr_path}` leaf type `{typed_value.__class__.__name__}` is neither `{self.leaf_type.__name__}` nor `dict`"
        )
