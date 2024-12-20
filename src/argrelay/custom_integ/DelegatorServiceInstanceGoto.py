from __future__ import annotations

from argrelay.custom_integ.DelegatorServiceBase import get_access_search_control
from argrelay.custom_integ.DelegatorServiceInstanceBase import DelegatorServiceInstanceBase, get_service_search_control
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_delegator.SchemaCustomDataDelegatorError import (
    error_message_,
    error_code_,
    error_delegator_stub_custom_data_example,
)
from argrelay.plugin_delegator.delegator_utils import redirect_to_error
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

func_id_goto_service_ = "func_id_goto_service"

service_container_ipos_ = 1
access_container_ipos_ = 2


class DelegatorServiceInstanceGoto(DelegatorServiceInstanceBase):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        service_search_control = get_service_search_control()

        access_search_control = get_access_search_control()

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_goto_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                        access_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Go (log in) to remote host and dir path with specified service",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_goto_service_,
            },
        ]
        return func_envelopes

    def has_fill_control(
        self,
    ) -> bool:
        return True

    def run_fill_control(
        self,
        interp_ctx: "InterpContext",
    ) -> bool:
        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == func_id_goto_service_

        object_container_ipos = service_container_ipos_

        any_assignment = False

        any_assignment = self._fill_object_container(
            any_assignment,
            interp_ctx,
            object_container_ipos,
        )

        any_assignment = self._fill_access_container(
            any_assignment,
            interp_ctx,
            object_container_ipos,
            access_container_ipos_,
        )

        return any_assignment

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == func_id_goto_service_

        vararg_container_ipos = service_container_ipos_

        # Even if these functions do not support varargs, when `redirect_to_error`, query all:
        vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]
        vararg_container.data_envelopes = (
            local_server
            .get_query_engine()
            .query_data_envelopes_for(vararg_container)
        )

        # Actual implementation is not defined for demo:
        return redirect_to_error(
            interp_ctx,
            local_server.plugin_config,
            error_delegator_stub_custom_data_example[error_message_],
            error_delegator_stub_custom_data_example[error_code_],
        )

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == func_id_goto_service_

        raise RuntimeError("ERROR: not implemented for demo")
