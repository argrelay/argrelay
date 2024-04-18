from __future__ import annotations

from enum import Enum, auto

from argrelay.custom_integ.ServiceDelegator import set_default_to
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import get_func_id_from_invocation_input, get_func_id_from_interp_ctx
from argrelay.plugin_delegator.AbstractJumpDelegator import AbstractJumpDelegator
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

output_format_class_name = "OutputFormat"
output_format_prop_name = "output_format"

format_output_container_ipos_ = 1


class OutputFormat(Enum):
    """
    Output format values.
    """

    json_format = auto()
    repr_format = auto()
    text_format = auto()
    table_format = auto()


class InterceptDelegator(AbstractJumpDelegator):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        output_format_search_control = populate_search_control(
            class_to_collection_map,
            output_format_class_name,
            [
                {"output": output_format_prop_name},
            ],
        )

        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.intercept_invocation_func.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    output_format_search_control,
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: (
                f"Intercept and print `{InvocationInput.__name__}` "
                "for specified function and its args"
            ),
            ReservedArgType.FuncId.name: SpecialFunc.intercept_invocation_func.name,
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
            SpecialFunc.intercept_invocation_func.name,
        ]:
            # If we need to specify `output_format_class_name` `data_envelope`:
            if interp_ctx.curr_container_ipos == interp_ctx.curr_interp.base_container_ipos + format_output_container_ipos_:
                format_output_container = interp_ctx.envelope_containers[(
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

        # TODO: Fail (send to ErrorDelegator) if next function is not specified -
        #       showing the payload in this case is misleading.
        delegator_plugin_instance_id = self.plugin_instance_id
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        # TODO: Print without first function `data_envelope` belonging to `intercept` function:
        func_id = get_func_id_from_invocation_input(invocation_input)
        if func_id == SpecialFunc.intercept_invocation_func.name:
            output_format: OutputFormat = OutputFormat[invocation_input.envelope_containers[
                format_output_container_ipos_
            ].data_envelopes[0][output_format_prop_name]]
            if not output_format:
                raise RuntimeError
            elif output_format == OutputFormat.json_format:
                print(invocation_input_desc.dict_schema.dumps(invocation_input))
            elif output_format == OutputFormat.repr_format:
                print(invocation_input)
            else:
                raise RuntimeError(f"not implemented: {output_format}")
        else:
            raise RuntimeError(f"unknown func_id: {func_id}")
