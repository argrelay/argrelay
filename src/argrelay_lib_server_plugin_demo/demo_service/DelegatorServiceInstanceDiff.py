from __future__ import annotations

from argrelay_api_plugin_server_abstract.delegator_utils import redirect_to_error
from argrelay_api_plugin_server_abstract.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_server_plugin_core.plugin_delegator.SchemaCustomDataDelegatorError import (
    error_code_,
    error_delegator_stub_custom_data_example,
    error_message_,
)
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceInstanceBase import (
    DelegatorServiceInstanceBase,
    get_service_search_control,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
    search_control_list_,
)

func_id_diff_service_ = "func_id_diff_service"

diff_service_container_left_ipos_ = 1
diff_service_container_right_ipos_ = 2


class DelegatorServiceInstanceDiff(DelegatorServiceInstanceBase):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        service_search_control = get_service_search_control()

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_diff_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        # This function was created to demo FS_97_64_39_94 `token_bucket`-s:
                        # it intentionally uses two services as to specify in its args:
                        service_search_control,
                        service_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Diff two service instances",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_diff_service_,
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
        assert func_id == func_id_diff_service_

        any_assignment = False

        any_assignment = self._fill_object_container(
            any_assignment,
            interp_ctx,
            diff_service_container_left_ipos_,
        )
        any_assignment = self._fill_object_container(
            any_assignment,
            interp_ctx,
            diff_service_container_right_ipos_,
        )

        return any_assignment

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == func_id_diff_service_

        # TODO: TODO_75_52_01_67: `token_bucket`-s to support multiple var args:
        #       query both service lists and compare them.

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
        assert func_id == func_id_diff_service_

        raise RuntimeError("ERROR: not implemented for demo")
