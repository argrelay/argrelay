from __future__ import annotations

import json

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.value_constants import (
    goto_host_func_,
    goto_service_func_,
    list_host_func_,
    list_service_func_,
    desc_host_func_,
    desc_service_func_,
)
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
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
from argrelay.plugin_delegator.NoopDelegator import NoopDelegator
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.AssignedValue import AssignedValue
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


def set_default_to(arg_type, arg_val, envelope_container):
    if arg_type in envelope_container.search_control.types_to_keys_dict:
        if arg_type not in envelope_container.assigned_types_to_values:
            if arg_type in envelope_container.remaining_types_to_values:
                if arg_val in envelope_container.remaining_types_to_values[arg_type]:
                    del envelope_container.remaining_types_to_values[arg_type]
                    envelope_container.assigned_types_to_values[arg_type] = AssignedValue(
                        arg_val,
                        ArgSource.DefaultValue,
                    )
        else:
            # Setting `ArgSource.DefaultValue`: it cannot override any, right? No point to handle assigned case:
            pass


def redirect_to_no_func_error(
    interp_ctx,
    server_config,
):
    return redirect_to_error(
        interp_ctx,
        server_config,
        "ERROR: objects cannot be searched until function is fully qualified",
        1,
    )


def redirect_to_error(
    interp_ctx,
    server_config,
    error_message,
    error_code,
):
    # Redirect to `ErrorDelegator`:
    # TODO: Do not hardcode plugin id (instance of `ErrorDelegator`):
    delegator_plugin_instance_id = f"{ErrorDelegator.__name__}.default"
    custom_plugin_data = {
        error_message_: error_message,
        error_code_: error_code,
    }
    error_delegator_custom_data_desc.validate_dict(custom_plugin_data)
    invocation_input = InvocationInput(
        arg_values = interp_ctx.comp_suggestions,
        all_tokens = interp_ctx.parsed_ctx.all_tokens,
        consumed_tokens = interp_ctx.consumed_tokens,
        envelope_containers = interp_ctx.envelope_containers,
        tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
        tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
        delegator_plugin_entry = server_config.plugin_instance_entries[delegator_plugin_instance_id],
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
                {"code": ServiceArgType.CodeMaturity.name},
                {"stage": ServiceArgType.FlowStage.name},
                {"region": ServiceArgType.GeoRegion.name},
                {"cluster": ServiceArgType.ClusterName.name},
            ],
        )

        host_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassHost.name,
            [
                # ClassCluster:
                {"code": ServiceArgType.CodeMaturity.name},
                {"stage": ServiceArgType.FlowStage.name},
                {"region": ServiceArgType.GeoRegion.name},
                {"cluster": ServiceArgType.ClusterName.name},
                # ClassHost:
                {"host": ServiceArgType.HostName.name},
                # ---
                {"ip": ServiceArgType.IpAddress.name},
            ],
        )

        service_search_control = populate_search_control(
            class_to_collection_map,
            ServiceEnvelopeClass.ClassService.name,
            [
                # ClassCluster:
                {"code": ServiceArgType.CodeMaturity.name},
                {"stage": ServiceArgType.FlowStage.name},
                {"region": ServiceArgType.GeoRegion.name},
                {"cluster": ServiceArgType.ClusterName.name},
                # ClassService:
                {"group": ServiceArgType.GroupLabel.name},
                {"service": ServiceArgType.ServiceName.name},
                # ClassHost:
                {"host": ServiceArgType.HostName.name},
                # ---
                {"status": ServiceArgType.LiveStatus.name},
                {"dc": ServiceArgType.DataCenter.name},
                {"ip": ServiceArgType.IpAddress.name},
            ],
        )

        access_search_control = populate_search_control(
            class_to_collection_map,
            ServiceArgType.AccessType.name,
            [
                {"access": ServiceArgType.AccessType.name},
            ],
        )

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: goto_host_func_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                        access_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Go (log in) to remote host",
                ReservedArgType.FuncId.name: goto_host_func_,
            },
            {
                instance_data_: {
                    func_id_: goto_service_func_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                        access_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Go (log in) to remote host and dir path with specified service",
                ReservedArgType.FuncId.name: goto_service_func_,
            },
            {
                instance_data_: {
                    func_id_: desc_host_func_,
                    # TODO: Do not hardcode plugin id (instance of `NoopDelegator`):
                    delegator_plugin_instance_id_: f"{NoopDelegator.__name__}.default",
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Describe remote host",
                ReservedArgType.FuncId.name: desc_host_func_,
            },
            {
                instance_data_: {
                    func_id_: desc_service_func_,
                    # TODO: Do not hardcode plugin id (instance of `NoopDelegator`):
                    delegator_plugin_instance_id_: f"{NoopDelegator.__name__}.default",
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Describe service instance",
                ReservedArgType.FuncId.name: desc_service_func_,
            },
            {
                instance_data_: {
                    func_id_: list_host_func_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "List remote hosts matching search query",
                ReservedArgType.FuncId.name: list_host_func_,
            },
            {
                instance_data_: {
                    func_id_: list_service_func_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "List service instances matching search query",
                ReservedArgType.FuncId.name: list_service_func_,
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
        if func_id in [
            goto_host_func_,
            goto_service_func_,
        ]:
            assert host_container_ipos_ == service_container_ipos_
            object_container_ipos = host_container_ipos_

            # If need to specify `AccessType` `data_envelope`:
            if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + access_container_ipos_:
                # Take object found so far:
                data_envelope = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + object_container_ipos
                )].data_envelopes[0]

                access_container = interp_ctx.envelope_containers[(
                    interp_ctx.curr_interp.base_container_ipos + access_container_ipos_
                )]

                # Select default value to search `AccessType` `data_envelope` based on `CodeMaturity`:
                code_arg_type = ServiceArgType.CodeMaturity.name
                if code_arg_type in data_envelope:
                    code_arg_val = data_envelope[code_arg_type]
                    if code_arg_val == "prod":
                        set_default_to(ServiceArgType.AccessType.name, "ro", access_container)
                    else:
                        set_default_to(ServiceArgType.AccessType.name, "rw", access_container)
                    return True

        elif func_id in [
            list_host_func_,
            list_service_func_,
        ]:
            pass
        else:
            raise RuntimeError

        return False

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
            goto_host_func_,
            goto_service_func_,
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
                local_server.server_config,
                error_delegator_stub_custom_data_example[error_message_],
                error_delegator_stub_custom_data_example[error_code_],
            )
        elif func_id in [
            list_host_func_,
            list_service_func_,
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
            else:
                return redirect_to_no_func_error(
                    interp_ctx,
                    local_server.server_config,
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
        if func_id == list_host_func_:
            for data_envelope in invocation_input.envelope_containers[host_container_ipos_].data_envelopes:
                print(json.dumps(data_envelope))
        elif func_id == list_service_func_:
            for data_envelope in invocation_input.envelope_containers[service_container_ipos_].data_envelopes:
                print(json.dumps(data_envelope))
        else:
            raise RuntimeError
