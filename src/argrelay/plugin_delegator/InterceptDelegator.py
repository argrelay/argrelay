from __future__ import annotations

from typing import Union

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_func_id_from_invocation_input
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.TreeWalker import TreeWalker
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

# TODO: Add config schema for both `InterceptDelegator` and `HelpDelegator`:
tree_abs_path_to_interp_id_ = "tree_abs_path_to_interp_id"


class InterceptDelegator(AbstractDelegator):

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

        func_tree_walker = TreeWalker(
            tree_abs_path_to_interp_id_,
            self.plugin_config_dict[tree_abs_path_to_interp_id_],
        )
        # Temporary (reversed) map which contains path per id (instead of id per path):
        temporary_id_to_paths: dict[str, list[list[str]]] = func_tree_walker.build_str_leaves_paths()

        # Reverse temporary path per id map into id per path map:
        self.tree_path_to_next_interp_plugin_instance_id: dict[tuple[str, ...], str] = {}
        for interp_plugin_id, tree_abs_paths in temporary_id_to_paths.items():
            for tree_abs_path in tree_abs_paths:
                self.tree_path_to_next_interp_plugin_instance_id[tuple(tree_abs_path)] = interp_plugin_id

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.intercept_invocation_func.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: (
                f"Intercept and print `{InvocationInput.__name__}` "
                "for specified function and its args"
            ),
            ReservedArgType.FuncId.name: SpecialFunc.intercept_invocation_func.name,
        }]
        return func_envelopes

    def run_init_control(
        self,
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        """
        `InterceptDelegator` searches its own func envelope.
        """
        super().run_init_control(
            envelope_containers,
            curr_container_ipos,
        )
        curr_container = envelope_containers[curr_container_ipos]
        curr_container.assigned_types_to_values[
            ReservedArgType.FuncId.name
        ] = AssignedValue(
            SpecialFunc.intercept_invocation_func.name,
            ArgSource.InitValue,
        )

    def run_search_control(
        self,
        function_data_envelope: dict,
    ) -> list[SearchControl]:
        # Nothing to search (only if next interpreter may need more, but this one is done):
        return []

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> Union[None, str]:
        # TODO_10_72_28_05: support special funcs for all commands:
        #                   Delegator must select next `interp_factory_id` based on `interp_tree_abs_path` via `tree_abs_path_to_interp_id` (not based on single plugin id specified)
        #                   because delegator can be accessible through multiple tree paths.
        #                   Delegator should map specific tree path using the tree path they are accessed through to specific `interp_plugin_instance_id`.
        #                   The next interp selection is a double jump:
        #                   *   the first jump here (in delegator) is based on selected func via its delegator to interp,
        #                   *   the second jump there (in jump tree interp) from jump interp via jump tree.
        # TODO: This must be special interpreter which is configured only to search functions (without their args).
        #       NEXT TODO: Why not support function args for special interp (e.g. `intercept` or `help` with format params)?
        #                  The interp_control is only run when func and all its args are selected and there should be next interp to continue.
        if curr_interp.interp_ctx.interp_tree_abs_path in self.tree_path_to_next_interp_plugin_instance_id:
            return self.tree_path_to_next_interp_plugin_instance_id[curr_interp.interp_ctx.interp_tree_abs_path]
        else:
            return None

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # TODO: Fail (send to ErrorDelegator) if next function is not specified -
        #       showing the payload in this case is misleading.
        function_envelope = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_envelope
            .data_envelopes[0]
            [instance_data_][delegator_plugin_instance_id_]
        )
        invocation_input = InvocationInput(
            arg_values = interp_ctx.comp_suggestions,
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
            delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if get_func_id_from_invocation_input(invocation_input) == SpecialFunc.intercept_invocation_func.name:
            # TODO: Print without first function `data_envelope` belonging to `intercept` function:
            print(invocation_input)
