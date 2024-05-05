from __future__ import annotations

from typing import Union

from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.misc_helper_server import insert_unique_to_sorted_list
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.InterpTreeInterpFactoryConfigSchema import interp_selector_tree_
from argrelay.plugin_interp.NoopInterpFactory import NoopInterpFactory
from argrelay.composite_tree.DictTreeWalker import surrogate_node_id_
from argrelay.runtime_context.InterpContext import InterpContext


def fetch_tree_node(
    tree_dict: dict,
    node_path: list[str],
):
    """
    Fetches tree node by node path.
    """

    curr_node_value = tree_dict
    for node_path_part in node_path:
        if isinstance(curr_node_value, dict) and node_path_part in curr_node_value:
            curr_node_value = curr_node_value[node_path_part]
        else:
            return None
    return curr_node_value


class InterpTreeInterp(AbstractInterp):
    """
    Implements FS_01_89_09_24 interp tree.
    """

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            interp_tree_node_config_dict,
            interp_ctx,
        )
        self.interp_selector_tree: dict = interp_tree_node_config_dict[interp_selector_tree_]
        self.next_interp_factory_id: Union[str, None] = None
        self.interp_tree_rel_path: list[str] = []

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

        curr_sub_tree = self.interp_selector_tree
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
                    self.interp_tree_rel_path.append(curr_token_value)

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
            # TODO: Do not hardcode plugin id (instance of `NoopInterpFactory`):
            self.next_interp_factory_id = f"{NoopInterpFactory.__name__}.default"

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp

    def next_interp(self) -> "AbstractInterp":
        # Selected `next_interp_factory_id` need to be given one of the paths in the FS_01_89_09_24 interp tree
        # (because each `next_interp_factory_id` can be plugged into multiple interp tree leaves).
        # Compose next `interp_tree_abs_path` based on:
        # *   curr `interp_tree_abs_path` given at creation of curr interp
        # *   next selected `interp_tree_rel_path` to that `next_interp_factory_id` in the interp tree
        self.interp_ctx.interp_tree_abs_path = self.interp_ctx.interp_tree_abs_path + tuple(self.interp_tree_rel_path)
        return self.interp_ctx.create_next_interp(self.next_interp_factory_id)

    def propose_arg_completion(self) -> None:
        """
        Suggest based on current sub-tree from config.
        """

        if not self.is_eligible_for_suggestion():
            return

        curr_sub_tree = fetch_tree_node(
            self.interp_selector_tree,
            self.interp_tree_rel_path,
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
        (after those recorded in `interp_tree_rel_path`) available for consumption by subsequent interpreters.
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

        # Remove everything eaten into `interp_tree_rel_path`:
        token_ipos = self.base_token_ipos
        for node_path_token in self.interp_tree_rel_path:
            assert token_ipos in remaining_consumed_tokens
            remaining_consumed_tokens.remove(token_ipos)
            token_ipos += 1

        # Is there anything else?
        return len(remaining_consumed_tokens) == 0
