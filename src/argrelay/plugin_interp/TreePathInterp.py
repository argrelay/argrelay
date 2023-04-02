from __future__ import annotations

from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.NoopInterpFactory import NoopInterpFactory
from argrelay.plugin_interp.TreePathInterpFactoryConfigSchema import interp_selector_tree_
from argrelay.runtime_context.InterpContext import InterpContext

default_tree_leaf_ = ""


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


class TreePathInterp(AbstractInterp):
    """
    Implements FS_01_89_09_24.
    """

    interp_selector_tree: dict

    interp_factory_id: str

    # Token with ipos = 0 is the command name eaten by `FirstArgInterp`.
    base_token_ipos: int = 1

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
        )
        self.interp_selector_tree = config_dict[interp_selector_tree_]
        self.interp_factory_id = interp_factory_id
        self.node_path = []

    def consume_pos_args(self) -> None:
        """
        Consumes heading args in `unconsumed_tokens` according to the `interp_selector_tree`.
        """

        self.node_path = []
        curr_sub_tree = self.interp_selector_tree
        while True:
            if isinstance(curr_sub_tree, str):
                # Tree leaf is reached - use it:
                self.interp_factory_id = curr_sub_tree
                return

            if not self.interp_ctx.unconsumed_tokens:
                self.set_default_factory_id(curr_sub_tree)
                return

            # Always consume next unconsumed token:
            # TODO: Is this assumption valid/safe that next unconsumed `ipos` is in the order it appears on command line?
            curr_token_ipos = self.interp_ctx.unconsumed_tokens[0]
            curr_token_value = self.interp_ctx.parsed_ctx.all_tokens[curr_token_ipos]
            assert self.is_pos_arg(curr_token_ipos)

            if isinstance(curr_sub_tree, dict):
                if curr_token_value in curr_sub_tree:
                    # Consume one more arg into path:
                    self.node_path.append(curr_token_value)
                    self.interp_ctx.consumed_tokens.append(curr_token_ipos)
                    del self.interp_ctx.unconsumed_tokens[0]
                    curr_sub_tree = curr_sub_tree[curr_token_value]
                    continue
                else:
                    self.set_default_factory_id(curr_sub_tree)
                    return
            else:
                raise LookupError()

    def set_default_factory_id(self, curr_sub_tree):
        # Impossible to consume more arg - use default of the current sub-tree:
        if default_tree_leaf_ in curr_sub_tree:
            self.interp_factory_id = curr_sub_tree[default_tree_leaf_]
        else:
            self.interp_factory_id = NoopInterpFactory.__name__

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp

    def next_interp(self) -> "AbstractInterp":
        return self.interp_ctx.create_next_interp(self.interp_factory_id)

    def propose_arg_completion(self) -> None:
        """
        Suggest based on current sub-tree from config.
        """

        if not self.is_eligible_for_suggestion():
            return

        curr_sub_tree = fetch_tree_node(
            self.interp_selector_tree,
            self.node_path,
        )
        if isinstance(curr_sub_tree, dict):
            proposed_values = [
                x for x in curr_sub_tree.keys()
                if (
                    isinstance(x, str)
                    and
                    x != default_tree_leaf_
                    and
                    # FS_32_05_46_00: using `startwith`:
                    x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                )
            ]
            self.interp_ctx.comp_suggestions.extend(proposed_values)

    def is_eligible_for_suggestion(self):
        """
        Suggesting anything is possible only if there is no other tokens after those recorded in `node_path`
        are available for consumption by subsequent interpreters.
        """

        if len(self.interp_ctx.unconsumed_tokens) == 0:
            return True
        else:
            return False

        # TODO: Clean up code below or take into account tangent token (ipos cursor position).
        #       Note that there is no ipos cursor position at the moment.
        #       It has to be computed with help of FS_23_62_89_43 tangent token
        #       (which might be a surrogate one if cursor does nto touch non-whitespace chars).
        remaining_consumed_tokens = self.interp_ctx.consumed_tokens.copy()

        # Remove everything until `base_token_ipos`:
        for token_ipos in range(0, self.base_token_ipos):
            assert token_ipos in remaining_consumed_tokens
            remaining_consumed_tokens.remove(token_ipos)

        # Remove everything eaten into `node_path`:
        token_ipos = self.base_token_ipos
        for node_path_token in self.node_path:
            assert token_ipos in remaining_consumed_tokens
            remaining_consumed_tokens.remove(token_ipos)
            token_ipos += 1

        # Is there anything else?
        return len(remaining_consumed_tokens) == 0
