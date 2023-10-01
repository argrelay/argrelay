from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_func_id_from_invocation_input
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

# TODO: Add config schema for both `InterceptDelegator` and `HelpDelegator`:
next_interp_plugin_instance_id_ = "next_interp_plugin_instance_id"


class InterceptDelegator(AbstractDelegator):

    def __init__(
        self,
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.intercept_invocation_func.name,
                delegator_plugin_instance_id_: InterceptDelegator.__name__,
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
    ) -> str:
        # TODO_10_72_28_05: support special funcs for all commands:
        #                   Delegator must select next interp_factory_id based on `interp_tree_abs_path` (not based on single `next_interp_plugin_instance_id`).
        #                   It is a double jump (first jump based on selected and specified func call from delegator to interp, second from interp via jump tree).
        return self.config_dict[next_interp_plugin_instance_id_]

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
