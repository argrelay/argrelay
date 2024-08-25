from __future__ import annotations

import json

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.custom_integ.value_constants import (
    func_id_goto_host_,
    func_id_goto_service_,
    func_id_list_host_,
    func_id_list_service_,
    func_id_diff_service_,
    func_id_desc_host_,
    func_id_desc_service_,
)
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.AbstractDelegator import (
    AbstractDelegator,
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_delegator.ErrorDelegator import ErrorDelegator
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import (
    error_message_,
    error_code_,
    error_delegator_custom_data_desc,
    error_delegator_stub_custom_data_example,
)
from argrelay.plugin_delegator.delegator_utils import set_default_to
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import (
    populate_search_control,
)
from argrelay.schema_response.InvocationInput import InvocationInput

host_container_ipos_ = 1
service_container_ipos_ = 1
access_container_ipos_ = 2

diff_service_container_left_ipos_ = 1
diff_service_container_right_ipos_ = 2


def redirect_to_no_func_error(
    interp_ctx,
    plugin_config,
):
    return redirect_to_error(
        interp_ctx,
        plugin_config,
        "ERROR: objects cannot be searched until function is fully qualified",
        1,
    )


def redirect_to_error(
    interp_ctx,
    plugin_config: PluginConfig,
    error_message,
    error_code,
):
    # Redirect to `ErrorDelegator`:
    # TODO: TODO_62_75_33_41: Do not hardcode plugin instance id (instance of `ErrorDelegator`):
    delegator_plugin_instance_id = f"{ErrorDelegator.__name__}.default"
    custom_plugin_data = {
        error_message_: error_message,
        error_code_: error_code,
    }
    error_delegator_custom_data_desc.validate_dict(custom_plugin_data)
    invocation_input = InvocationInput.with_interp_context(
        interp_ctx,
        delegator_plugin_entry = plugin_config.plugin_instance_entries[delegator_plugin_instance_id],
        custom_plugin_data = custom_plugin_data,
    )
    return invocation_input


class ServiceDelegator(AbstractDelegator):

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

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        cluster_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassCluster.name,
            [
                {"code": ServicePropName.code_maturity.name},
                {"stage": ServicePropName.flow_stage.name},
                {"region": ServicePropName.geo_region.name},
                {"cluster": ServicePropName.cluster_name.name},
            ],
        )

        host_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassHost.name,
            [
                # ClassCluster:
                {"code": ServicePropName.code_maturity.name},
                {"stage": ServicePropName.flow_stage.name},
                {"region": ServicePropName.geo_region.name},
                {"cluster": ServicePropName.cluster_name.name},
                # ClassHost:
                {"host": ServicePropName.host_name.name},
                # ---
                {"status": ServicePropName.live_status.name},
                {"ip": ServicePropName.ip_address.name},
            ],
        )

        service_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassService.name,
            [
                # ClassCluster:
                {"code": ServicePropName.code_maturity.name},
                {"stage": ServicePropName.flow_stage.name},
                {"region": ServicePropName.geo_region.name},
                {"cluster": ServicePropName.cluster_name.name},
                # ClassService:
                {"group": ServicePropName.group_label.name},
                {"service": ServicePropName.service_name.name},
                {"mode": ServicePropName.run_mode.name},
                # ClassHost:
                {"host": ServicePropName.host_name.name},
                # ---
                {"status": ServicePropName.live_status.name},
                {"dc": ServicePropName.data_center.name},
                {"ip": ServicePropName.ip_address.name},
            ],
        )

        access_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassAccessType.name,
            [
                {"access": ServicePropName.access_type.name},
            ],
        )

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_goto_host_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                        access_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Go (log in) to remote host",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_goto_host_,
            },
            {
                instance_data_: {
                    func_id_: func_id_goto_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                        access_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Go (log in) to remote host and dir path with specified service",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_goto_service_,
            },
            {
                instance_data_: {
                    func_id_: func_id_desc_host_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Describe remote host",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_desc_host_,
            },
            {
                instance_data_: {
                    func_id_: func_id_desc_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Describe service instance",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_desc_service_,
            },
            {
                instance_data_: {
                    func_id_: func_id_list_host_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "List remote hosts matching search query",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_list_host_,
            },
            {
                instance_data_: {
                    func_id_: func_id_list_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "List service instances matching search query",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_list_service_,
            },
            {
                instance_data_: {
                    func_id_: func_id_diff_service_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        # This function was created to demo FS_97_64_39_94 `arg_bucket`-s:
                        # it intentionally uses two services as to specify in its args:
                        service_search_control,
                        service_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
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
        any_assignment = False

        if func_id in [
            func_id_goto_host_,
            func_id_goto_service_,
        ]:
            assert host_container_ipos_ == service_container_ipos_
            object_container_ipos = host_container_ipos_

            if func_id == func_id_goto_service_:
                any_assignment = self._fill_service_container(
                    any_assignment,
                    interp_ctx,
                    object_container_ipos,
                )

            # If we need to specify `access_type` `data_envelope`:
            if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + access_container_ipos_:
                # Take object found so far:
                data_envelope = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + object_container_ipos
                )].data_envelopes[0]

                access_container = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + access_container_ipos_
                )]

                # Select default value to search `access_type` `data_envelope` based on `code_maturity`:
                code_arg_type = ServicePropName.code_maturity.name
                if code_arg_type in data_envelope:
                    code_arg_val = data_envelope[code_arg_type]
                    if code_arg_val == "prod":
                        any_assignment = (
                            set_default_to(ServicePropName.access_type.name, "ro", access_container)
                            or
                            any_assignment
                        )
                    else:
                        any_assignment = (
                            set_default_to(ServicePropName.access_type.name, "rw", access_container)
                            or
                            any_assignment
                        )
        elif func_id in [
            func_id_diff_service_,
        ]:
            any_assignment = self._fill_service_container(
                any_assignment,
                interp_ctx,
                diff_service_container_left_ipos_,
            )
            any_assignment = self._fill_service_container(
                any_assignment,
                interp_ctx,
                diff_service_container_right_ipos_,
            )
        elif func_id in [
            func_id_list_host_,
            func_id_list_service_,
        ]:
            pass
        elif func_id in [
            func_id_desc_host_,
            func_id_desc_service_,
        ]:
            pass
        else:
            raise RuntimeError

        return any_assignment

    def _fill_service_container(
        self,
        any_assignment,
        interp_ctx,
        object_container_ipos,
    ):
        if (
            interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + object_container_ipos
        ):
            service_container = interp_ctx.envelope_containers[(
                interp_ctx.curr_interp.base_container_ipos + object_container_ipos
            )]
            any_assignment = (
                set_default_to(ServicePropName.run_mode.name, "active", service_container)
                or
                any_assignment
            )
        return any_assignment

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)

        vararg_container_ipos = host_container_ipos_
        assert vararg_container_ipos == host_container_ipos_ == service_container_ipos_

        if func_id in [
            func_id_goto_host_,
            func_id_goto_service_,
        ]:
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
        elif func_id in [
            func_id_diff_service_,
        ]:
            # TODO_75_52_01_67: `arg_bucket`-s to support multiple var args:
            #                   query both service lists and compare them.

            # Actual implementation is not defined for demo:
            return redirect_to_error(
                interp_ctx,
                local_server.plugin_config,
                error_delegator_stub_custom_data_example[error_message_],
                error_delegator_stub_custom_data_example[error_code_],
            )
        elif func_id in [
            func_id_list_host_,
            func_id_list_service_,
        ]:
            # Verify that func is selected and all what is left to do is to query 0...N objects:
            if interp_ctx.curr_container_ipos >= vararg_container_ipos:
                # Search `data_envelope`-s based on existing args on command line:
                vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]
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
                    delegator_plugin_entry = local_server.plugin_config.plugin_instance_entries[
                        delegator_plugin_instance_id
                    ],
                    custom_plugin_data = {},
                )
                return invocation_input
            else:
                return redirect_to_no_func_error(
                    interp_ctx,
                    local_server.server_config,
                )
        elif func_id in [
            func_id_desc_host_,
            func_id_desc_service_,
        ]:
            # Actual implementation is not defined for demo:
            return redirect_to_error(
                interp_ctx,
                local_server.plugin_config,
                error_delegator_stub_custom_data_example[error_message_],
                error_delegator_stub_custom_data_example[error_code_],
            )
        else:
            # Plugin is given a function name it does not know:
            raise RuntimeError

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        """
        Print `data_envelope`-s received from server on client side.
        """

        func_id = get_func_id_from_invocation_input(invocation_input)
        if func_id == func_id_list_host_:
            prohibit_unconsumed_args(invocation_input)
            for data_envelope in invocation_input.envelope_containers[host_container_ipos_].data_envelopes:
                print(json.dumps(data_envelope))
        elif func_id == func_id_list_service_:
            prohibit_unconsumed_args(invocation_input)
            for data_envelope in invocation_input.envelope_containers[service_container_ipos_].data_envelopes:
                print(json.dumps(data_envelope))
        else:
            raise RuntimeError("ERROR: not implemented for demo")
