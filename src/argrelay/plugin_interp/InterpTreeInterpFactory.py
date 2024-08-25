from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import Union

from argrelay.composite_forest.CompositeForestExtractor import extract_interp_tree
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker, sequence_starts_with, fetch_subtree_node, \
    surrogate_node_id_
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.PluginType import PluginType
from argrelay.misc_helper_server import insert_unique_to_sorted_list
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory, AbstractInterp
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import (
    tree_path_interp_factory_config_desc,
)
from argrelay.plugin_interp.NoopInterpFactory import NoopInterpFactory
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig, assert_plugin_instance_id


class InterpTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_01_89_09_24 interp tree.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )
        self.is_recursive_func_load = False
        self.interp_selector_tree = extract_interp_tree(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_instance_id,
        )

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return tree_path_interp_factory_config_desc.dict_from_input_dict(plugin_config_dict)

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        # TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor:
        #       At the moment, `InterpTreeInterpFactory` is not plugged into main interp tree -
        #       instead, it is plugged by `FirstArgInterpFactory`.

        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.interp_tree,
            self.interp_selector_tree,
        )
        # Walk configured interp tree and call `load_interp_tree_abs_paths` with `interp_tree_abs_path` for each interp.
        all_interp_tree_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()
        for interp_factory_instance_id in all_interp_tree_abs_paths:
            assert_plugin_instance_id(
                self.server_config,
                interp_factory_instance_id,
                PluginType.InterpFactoryPlugin,
            )
            interp_factory: AbstractInterpFactory = self.server_config.interp_factories[interp_factory_instance_id]
            interp_factory.load_interp_tree_abs_paths([
                tuple(list_abs_path)
                for list_abs_path in all_interp_tree_abs_paths[interp_factory_instance_id]
            ])

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        with self._is_recursive_load() as is_recursive_load:
            # TODO: FS_33_76_82_84 composite forest: add validation that same interp tree interp is not loaded twice - is it required (given that plugin instances can be reused)?
            if is_recursive_load:
                return []
            return self._load_func_envelopes(
                interp_tree_abs_path,
                func_ids_to_func_envelopes,
            )

    @contextlib.contextmanager
    def _is_recursive_load(self):
        """
        Auto-reset flag `self.is_recursive_func_load` on exit from `with` section.
        """
        try:
            if not self.is_recursive_func_load:
                self.is_recursive_func_load = True
                is_recursive_load = False
            else:
                is_recursive_load = True
            yield is_recursive_load
        finally:
            self.is_recursive_func_load = False

    def _load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> list[str]:
        mapped_func_ids: list[str] = super().load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )
        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.interp_tree,
            self.interp_selector_tree,
        )
        # Walk configured interp tree and call `load_func_envelopes` with `interp_tree_abs_path` for each interp.
        all_interp_tree_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()
        for interp_factory_instance_id in all_interp_tree_abs_paths:
            for sub_interp_tree_abs_path in all_interp_tree_abs_paths[interp_factory_instance_id]:
                if not sequence_starts_with(sub_interp_tree_abs_path, interp_tree_abs_path):
                    # skip: other `interp_tree_abs_path`-s are going to be separate calls to this func:
                    continue
                assert_plugin_instance_id(
                    self.server_config,
                    interp_factory_instance_id,
                    PluginType.InterpFactoryPlugin,
                )
                interp_factory: AbstractInterpFactory = self.server_config.interp_factories[interp_factory_instance_id]

                mapped_func_ids.extend(interp_factory.load_func_envelopes(
                    tuple(sub_interp_tree_abs_path),
                    func_ids_to_func_envelopes,
                ))
        return mapped_func_ids

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> InterpTreeInterp:
        """
        Each `InterpTreeInterpFactory` serves a subtree,
        but it only stores config of per its plug points
        (interp tree abs paths where it was invoked on `load_func_envelopes`).
        If next interp with its plugin id is created, but the specified path is within its subtree,
        chop off the last step in the path until it matches path to its subtree to select one.
        For example:
        ```
        # Current path within interp tree:
        interp_ctx.interp_tree_abs_path = ('l1', 'l2', 'l3', 'l4', )
        # Plug point of this factory within the interp tree:
        self.interp_tree_abs_paths_to_node_configs = {
            ('l1', 'l2', ): {},
            ('x1', 'x2', 'x3', ): {},
        }
        # Keep trying to cut of the last step in the path until it matches one of the key:
        ('l1', 'l2', 'l3', 'l4', )
        ('l1', 'l2', 'l3', )
        ('l1', 'l2', )
        # Done.
        ```
        """
        orig_subtree_abs_path = interp_ctx.interp_tree_abs_path
        curr_subtree_abs_path = orig_subtree_abs_path
        while curr_subtree_abs_path not in self.interp_tree_abs_paths_to_node_configs:
            if len(curr_subtree_abs_path) == 0:
                raise ValueError(
                    f"path `{orig_subtree_abs_path}` is not subpath of `{self.interp_tree_abs_paths_to_node_configs.keys()}` paths"
                )
            curr_subtree_abs_path = curr_subtree_abs_path[:-1]
        return InterpTreeInterp(
            self.plugin_instance_id,
            self.interp_tree_abs_paths_to_node_configs[curr_subtree_abs_path],
            interp_ctx,
            self.interp_selector_tree,
        )


class InterpTreeInterp(AbstractInterp):
    """
    Implements FS_01_89_09_24 interp tree.
    """

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
        interp_selector_tree: dict,
    ):
        super().__init__(
            interp_factory_id,
            interp_tree_node_config_dict,
            interp_ctx,
        )
        self.interp_selector_tree: dict = interp_selector_tree
        self.next_interp_factory_id: Union[str, None] = None

        # TODO: Why hard-coded? Isn't it possible for this plugin to be plugged into any depth of the tree?
        # Token with ipos = 0 is the command name eaten by `FirstArgInterp` (FS_42_76_93_51 first interp):
        self.base_token_ipos: int = 1

    def consumes_args_at_once(self) -> bool:
        return True

    def consume_pos_args(self) -> bool:
        """
        Consumes heading args in `remaining_arg_buckets` according to the `interp_selector_tree`.

        Unlike normal guideline to consume one arg at time (FS_44_36_84_88),
        this func consumes all possible args
        because args are selected according to the `interp_selector_tree` (not via query)
        and do not become incompatible by consuming all (causing FS_51_67_38_37 impossible arg combinations).

        Also, FS_01_89_09_24 interp tree does not observe FS_97_64_39_94 `arg_bucket` boundaries
        and consumes all necessary args sequentially.
        """

        curr_sub_tree = fetch_subtree_node(
            self.interp_selector_tree,
            self.interp_tree_abs_path,
        )
        any_consumed = False
        while True:
            if isinstance(curr_sub_tree, str):
                # Tree leaf is reached - use it:
                self.next_interp_factory_id = curr_sub_tree
                return any_consumed

            # Always consume next remaining token:
            # TODO: Is this assumption valid/safe that next remaining `ipos` is in the order it appears on command line?
            #       Apparently, it is fine as we keep deleting head of `remaining_arg_buckets` below:
            curr_token_ipos = self.interp_ctx.next_remaining_token_ipos()

            if curr_token_ipos is None:
                self.set_default_factory_id(curr_sub_tree)
                return any_consumed

            curr_token_value = self.interp_ctx.parsed_ctx.all_tokens[curr_token_ipos]
            assert self.is_pos_arg(curr_token_ipos)

            if isinstance(curr_sub_tree, dict):
                if curr_token_value in curr_sub_tree:
                    # Consume one more arg into path:
                    self.interp_tree_abs_path.append(curr_token_value)

                    bucket_index = self.interp_ctx.token_ipos_to_arg_bucket_map[curr_token_ipos]
                    self.interp_ctx.consumed_arg_buckets[bucket_index].append(curr_token_ipos)
                    del self.interp_ctx.remaining_arg_buckets[bucket_index][0]

                    curr_sub_tree = curr_sub_tree[curr_token_value]
                    any_consumed = True
                    continue
                else:
                    self.set_default_factory_id(curr_sub_tree)
                    return any_consumed
            else:
                raise LookupError()

    def set_default_factory_id(
        self,
        curr_sub_tree,
    ):
        # Impossible to consume more arg - use default of the current sub-tree:
        if surrogate_node_id_ in curr_sub_tree:
            self.next_interp_factory_id = curr_sub_tree[surrogate_node_id_]
        else:
            # TODO: TODO_62_75_33_41: Do not hardcode plugin instance id (instance of `NoopInterpFactory`):
            self.next_interp_factory_id = f"{NoopInterpFactory.__name__}.default"

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp

    def next_interp(self) -> "AbstractInterp":
        # Selected `next_interp_factory_id` need to be given one of the paths in the FS_01_89_09_24 interp tree
        # (because each `next_interp_factory_id` can be plugged into multiple interp tree leaves).
        self.interp_ctx.interp_tree_abs_path = tuple(self.interp_tree_abs_path)
        return self.interp_ctx.create_next_interp(self.next_interp_factory_id)

    def propose_arg_completion(self) -> None:
        """
        Suggest based on current sub-tree from config.
        """

        if not self.is_eligible_for_suggestion():
            return

        curr_sub_tree = fetch_subtree_node(
            self.interp_selector_tree,
            self.interp_tree_abs_path,
        )
        if isinstance(curr_sub_tree, dict):
            for proposed_value in [
                x for x in curr_sub_tree
                if (
                    isinstance(x, str)
                    and
                    x != surrogate_node_id_
                    and
                    # FS_32_05_46_00: using `startswith`:
                    x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                )
            ]:
                insert_unique_to_sorted_list(self.interp_ctx.comp_suggestions, proposed_value)

    def is_eligible_for_suggestion(self):
        """
        Suggesting anything is possible only if there is no other tokens
        (after those recorded in `interp_tree_abs_path`) available for consumption by subsequent interpreters.
        """

        if self.interp_ctx.next_remaining_token_ipos() is None:
            return True
        else:
            return False

        # TODO: Clean up code below or take into account tangent token (ipos cursor position).
        #       Note that there is no ipos cursor position at the moment.
        #       It has to be computed with help of FS_23_62_89_43 tangent token
        #       (which might be a surrogate one if cursor does not touch non-whitespace chars).
        remaining_consumed_tokens = deepcopy(self.interp_ctx.consumed_token_ipos_list())

        # Remove everything until `base_token_ipos`:
        for token_ipos in range(0, self.base_token_ipos):
            assert token_ipos in remaining_consumed_tokens
            remaining_consumed_tokens.remove(token_ipos)

        # Remove everything eaten into `interp_tree_abs_path`:
        token_ipos = self.base_token_ipos
        for node_path_token in self.interp_tree_abs_path:
            assert token_ipos in remaining_consumed_tokens
            remaining_consumed_tokens.remove(token_ipos)
            token_ipos += 1

        # Is there anything else?
        return len(remaining_consumed_tokens) == 0
