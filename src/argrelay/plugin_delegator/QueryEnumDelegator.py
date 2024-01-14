from __future__ import annotations

from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.plugin_delegator.InterceptDelegator import InterceptDelegator
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.InterpContext import function_container_ipos_
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

subsequent_function_container_ipos_ = function_container_ipos_ + 1


# TODO: Currently, QueryEnumDelegator is implemented by deriving from InterceptDelegator - this is strange.
#       Use common base class instead, but don't make "QueryEnumDelegator is a InterceptDelegator".
class QueryEnumDelegator(InterceptDelegator):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.query_enum_items_func.name,
                delegator_plugin_instance_id_: QueryEnumDelegator.__name__,
                search_control_list_: [
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "Enumerate available arg options (based on existing arg values)",
            ReservedArgType.FuncId.name: SpecialFunc.query_enum_items_func.name,
        }]
        return func_envelopes

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> str:
        return super().run_interp_control(curr_interp)

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        DescribeLineArgsClientResponseHandler.render_result(invocation_input)
