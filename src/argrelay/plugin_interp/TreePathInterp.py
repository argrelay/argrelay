from __future__ import annotations

from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
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

    def consume_pos_args(self) -> None:
        """
        Consumes heading args in `unconsumed_tokens` according to the `interp_selector_tree`.
        """

        # Start with 1st arg (the very first 0th is command):
        node_path = []
        curr_sub_tree = self.interp_selector_tree
        while True:
            if isinstance(curr_sub_tree, str):
                # Tree leaf is reached - use it:
                self.interp_factory_id = curr_sub_tree
                return

            if not self.interp_ctx.unconsumed_tokens:
                # Impossible to consume more arg - use default of the current sub-tree:
                self.interp_factory_id = curr_sub_tree[default_tree_leaf_]
                return

            curr_token_ipos = self.interp_ctx.unconsumed_tokens[0]
            curr_token_value = self.interp_ctx.parsed_ctx.all_tokens[curr_token_ipos]
            assert self.is_pos_arg(curr_token_ipos)

            if isinstance(curr_sub_tree, dict):
                if curr_token_value in curr_sub_tree:
                    # Consume one more arg into path:
                    node_path.append(curr_token_value)
                    self.interp_ctx.consumed_tokens.append(curr_token_ipos)
                    del self.interp_ctx.unconsumed_tokens[0]
                    curr_sub_tree = curr_sub_tree[curr_token_value]
                    continue
                else:
                    # Impossible to consume more arg - use default of the current sub-tree:
                    self.interp_factory_id = curr_sub_tree[default_tree_leaf_]
                    return
            else:
                raise LookupError()

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp

    def next_interp(self) -> "AbstractInterp":
        return self.interp_ctx.create_next_interp(self.interp_factory_id)
