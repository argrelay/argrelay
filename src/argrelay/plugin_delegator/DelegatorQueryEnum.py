from __future__ import annotations

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.handler_response.ClientResponseHandlerDescribeLineArgs import ClientResponseHandlerDescribeLineArgs
from argrelay.plugin_delegator.DelegatorJumpAbstract import DelegatorJumpAbstract
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import function_container_ipos_, InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

subsequent_function_container_ipos_ = function_container_ipos_ + 1


class DelegatorQueryEnum(DelegatorJumpAbstract):
    """
    FS_02_25_41_81: Implements `func_id_query_enum_items`.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.func_id_query_enum_items.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "Enumerate available arg options (based on existing `prop_value`-s)",
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_query_enum_items.name,
        }]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # TODO: Fail (send to DelegatorError) if next function is not specified -
        #       showing the payload in this case is misleading.
        delegator_plugin_instance_id = self.plugin_instance_id
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        ClientResponseHandlerDescribeLineArgs.render_result(invocation_input)
