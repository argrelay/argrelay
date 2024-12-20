from __future__ import annotations

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.plugin_delegator.delegator_utils import set_default_to, redirect_to_not_disambiguated_error
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput


def get_access_search_control(
) -> dict:
    return populate_search_control(
        ServiceEnvelopeClass.class_access_type.name,
        {
            ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_access_type.name,
        },
        [
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            {"class": ReservedPropName.envelope_class.name},

            {"access": ServicePropName.access_type.name},
        ],
    )


class DelegatorServiceBase(DelegatorSingleFuncAbstract):

    def _fill_object_container(
        self,
        any_assignment,
        interp_ctx,
        object_container_ipos,
    ):
        if (
            # TODO: TODO_73_23_85_93: use helper to select container ipos:
            interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + object_container_ipos
        ):
            service_container = interp_ctx.envelope_containers[(
                # TODO: TODO_73_23_85_93: use helper to select container ipos:
                interp_ctx.curr_interp.base_container_ipos + object_container_ipos
            )]
            any_assignment = (
                set_default_to(ServicePropName.run_mode.name, "active", service_container)
                or
                any_assignment
            )
        return any_assignment

    def _fill_access_container(
        self,
        any_assignment,
        interp_ctx,
        object_container_ipos,
        access_container_ipos,
    ):
        # If we need to specify `access_type` `data_envelope`:
        # TODO: TODO_73_23_85_93: use helper to select container ipos:
        if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + access_container_ipos:
            # Take object found so far:
            data_envelope = interp_ctx.envelope_containers[(
                # TODO: TODO_73_23_85_93: use helper to select container ipos:
                interp_ctx.curr_interp.base_container_ipos + object_container_ipos
            )].data_envelopes[0]

            access_container = interp_ctx.envelope_containers[(
                # TODO: TODO_73_23_85_93: use helper to select container ipos:
                interp_ctx.curr_interp.base_container_ipos + access_container_ipos
            )]

            # Select default value to search `access_type` `data_envelope` based on `code_maturity`:
            code_prop_name = ServicePropName.code_maturity.name
            if code_prop_name in data_envelope:
                code_arg_val = data_envelope[code_prop_name]
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

        return any_assignment

    def _compose_invocation_input_for_list(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
        vararg_container_ipos,
        envelope_class,
    ):
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
                delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                    delegator_plugin_instance_id
                ],
                custom_plugin_data = {},
            )
            return invocation_input
        else:
            return redirect_to_not_disambiguated_error(
                interp_ctx,
                local_server.plugin_config,
                envelope_class,
            )
