from __future__ import annotations

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.plugin_delegator.AbstractJumpDelegator import AbstractJumpDelegator
from argrelay.runtime_context.InterpContext import function_container_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

subsequent_function_container_ipos_ = function_container_ipos_ + 1


class QueryEnumDelegator(AbstractJumpDelegator):
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
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedPropName.help_hint.name: "Enumerate available arg options (based on existing arg values)",
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_query_enum_items.name,
        }]
        return func_envelopes

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        DescribeLineArgsClientResponseHandler.render_result(invocation_input)
