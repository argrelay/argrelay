from __future__ import annotations

from enum import Enum, auto

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_invocation_input, get_func_id_from_interp_ctx
from argrelay.plugin_delegator.DelegatorJumpAbstract import DelegatorJumpAbstract
from argrelay.plugin_delegator.delegator_utils import set_default_to
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc

format_output_container_ipos_ = 1


class OutputFormat(Enum):
    """
    Output format values.
    """

    json_format = auto()
    repr_format = auto()
    text_format = auto()
    table_format = auto()


output_format_class_name = "class_output_format"
output_format_prop_name = "output_format"


class DelegatorIntercept(DelegatorJumpAbstract):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        output_format_search_control = populate_search_control(
            output_format_class_name,
            {
                ReservedPropName.envelope_class.name: output_format_class_name,
            },
            [
                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                {"class": ReservedPropName.envelope_class.name},

                {"output": output_format_prop_name},
            ],
        )

        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.func_id_intercept_invocation.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    output_format_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: (
                f"Intercept and print `{InvocationInput.__name__}` "
                "for specified function and its args"
            ),
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_intercept_invocation.name,
        }]
        return func_envelopes

    def has_fill_control(
        self,
    ) -> bool:
        return True

    def run_fill_control(
        self,
        interp_ctx: InterpContext,
    ) -> bool:
        func_id = get_func_id_from_interp_ctx(interp_ctx)
        any_assignment = False
        if func_id in [
            SpecialFunc.func_id_intercept_invocation.name,
        ]:
            # If we need to specify `output_format_class_name` `data_envelope`:
            # TODO: TODO_73_23_85_93: use helper to select container ipos:
            if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + format_output_container_ipos_:
                format_output_container = interp_ctx.envelope_containers[(
                    # TODO: TODO_73_23_85_93: use helper to select container ipos:
                    interp_ctx.curr_interp.base_container_ipos + format_output_container_ipos_
                )]
                any_assignment = (
                    set_default_to(output_format_prop_name, OutputFormat.json_format.name, format_output_container)
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
        # TODO: Print without first function `data_envelope` belonging to `intercept` function:
        func_id = get_func_id_from_invocation_input(invocation_input)
        if func_id == SpecialFunc.func_id_intercept_invocation.name:

            # NOTE: This function does not prohibit unrecognized args.

            output_format: output_format = OutputFormat[invocation_input.envelope_containers[
                format_output_container_ipos_
            ].data_envelopes[0][output_format_prop_name]]
            if not output_format:
                raise RuntimeError
            elif output_format == output_format.json_format:
                print(invocation_input_desc.dict_schema.dumps(invocation_input))
            elif output_format == output_format.repr_format:
                print(invocation_input)
            else:
                raise RuntimeError(f"not implemented: {output_format}")
        else:
            raise RuntimeError(f"unknown func_id: {func_id}")
