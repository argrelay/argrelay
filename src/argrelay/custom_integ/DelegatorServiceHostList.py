from __future__ import annotations

import json

from argrelay.custom_integ.DelegatorServiceHostBase import DelegatorServiceHostBase, get_host_search_control
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

func_id_list_host_ = "func_id_list_host"

host_container_ipos_ = 1


class DelegatorServiceHostList(DelegatorServiceHostBase):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        host_search_control = get_host_search_control()

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_list_host_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "List remote hosts matching search query",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_list_host_,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == func_id_list_host_

        vararg_container_ipos = host_container_ipos_

        return self._compose_invocation_input_for_list(
            interp_ctx,
            local_server,
            vararg_container_ipos,
            ServiceEnvelopeClass.class_host.name,
        )

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        """
        Print `data_envelope`-s received from server on client side.
        """

        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == func_id_list_host_

        prohibit_unconsumed_args(invocation_input)

        for data_envelope in invocation_input.envelope_containers[host_container_ipos_].data_envelopes:
            print(json.dumps(data_envelope))
