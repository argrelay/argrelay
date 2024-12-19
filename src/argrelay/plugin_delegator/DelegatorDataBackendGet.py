from __future__ import annotations

import json

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_invocation_input, get_func_id_from_interp_ctx
from argrelay.plugin_delegator.DelegatorDataBackendBase import get_collection_search_control, DelegatorDataBackendBase
from argrelay.plugin_delegator.delegator_utils import redirect_to_not_disambiguated_error
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

collection_name_container_ipos_ = 1
data_envelope_container_ipos_ = 2


class DelegatorDataBackendGet(DelegatorDataBackendBase):
    """
    Implements `SpecialFunc.func_id_get_data_envelopes` for FS_74_69_61_79 get set data envelope.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        collection_search_control = get_collection_search_control(
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: SpecialFunc.func_id_get_data_envelopes.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    collection_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "Get `data_envelope`-s based on their `index_prop`-s.",
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_get_data_envelopes.name,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == SpecialFunc.func_id_get_data_envelopes.name

        vararg_container_ipos = data_envelope_container_ipos_

        # Verify that func is selected:
        if interp_ctx.curr_container_ipos < vararg_container_ipos:
            return redirect_to_not_disambiguated_error(
                interp_ctx,
                local_server.plugin_config,
                ReservedEnvelopeClass.class_collection.name,
            )

        vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]

        # All what is left to do is to query objects.
        # Search `data_envelope`-s based on existing args on command line:
        vararg_container.data_envelopes = (
            local_server
            .get_query_engine()
            .query_data_envelopes_for(vararg_container)
        )

        # Plugin to invoke on client side:
        delegator_plugin_instance_id = self.plugin_instance_id
        # Package into `InvocationInput` payload object:
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
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == SpecialFunc.func_id_get_data_envelopes.name

        prohibit_unconsumed_args(invocation_input)

        for data_envelope in invocation_input.envelope_containers[data_envelope_container_ipos_].data_envelopes:
            print(json.dumps(data_envelope))
