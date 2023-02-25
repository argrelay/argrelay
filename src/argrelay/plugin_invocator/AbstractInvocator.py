from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper.AbstractPlugin import AbstractPlugin
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_, init_control_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc


class AbstractInvocator(AbstractPlugin):
    """
    Invocator plugin implements two sides:
    *   server-side `invoke_control` prepares data in :class:`InvocationInput` (whatever is necessary)
    *   client-side `invoke_action` uses data in :class:`InvocationInput` to execute the action anyway it can

    To simplify reasoning, ensure that both server-side and client-side:
    *   have access to the same code (non-breaking differences are possible, but same code version ensures that)
    *   share data only via :class:`InvocationInput`
    """

    def run_search_control(
        self,
        function_data_envelope: dict,
    ) -> list[SearchControl]:
        return self.extract_search_control_from_function_data_envelope(function_data_envelope)

    def run_init_control(
        self,
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        self.init_envelope_class(
            envelope_containers,
            curr_container_ipos,
        )

        # Take from prev container:
        self.use_init_control_from_data_envelope(
            envelope_containers,
            curr_container_ipos,
        )

    def run_fill_control(
        self,
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        pass

    def run_invoke_control(
        self,
        server_config: ServerConfig,
        interp_ctx: InterpContext,
    ) -> InvocationInput:
        """
        Server-side entry point.
        The plugin instance is used by server after `AbstractPlugin.activate_plugin`.
        """
        pass

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        """
        Client-side (static) entry point.
        The plugin instance is used by client:
        *   without instantiating
        *   without providing `AbstractPlugin.config_dict`
        *   without calling `AbstractPlugin.activate_plugin`
        """
        pass

    @staticmethod
    def extract_search_control_from_function_data_envelope(function_data_envelope: dict):
        return [
            search_control_desc.dict_schema.load(search_control_dict)
            for search_control_dict in function_data_envelope[instance_data_][search_control_list_]
        ]

    @staticmethod
    def init_envelope_class(
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        curr_container = envelope_containers[curr_container_ipos]
        curr_container.assigned_types_to_values[
            ReservedArgType.EnvelopeClass.name
        ] = AssignedValue(
            curr_container.search_control.envelope_class,
            ArgSource.InitValue,
        )

    @staticmethod
    def use_init_control_from_data_envelope(
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ):
        """
        FS_46_96_59_05: default implementation of `init_control` (based on `init_control` in `data_envelope`)

        Copy arg value from prev `data_envelope` for arg types specified in `init_control` into next `args_context`.
        """

        curr_container = envelope_containers[curr_container_ipos]
        prev_envelope = envelope_containers[curr_container_ipos - 1]
        if init_control_ in prev_envelope.data_envelope:
            arg_type_list_to_push = prev_envelope.data_envelope[init_control_]
            for arg_type_to_push in arg_type_list_to_push:
                if arg_type_to_push in prev_envelope.data_envelope:
                    if arg_type_to_push in curr_container.assigned_types_to_values:
                        arg_value = curr_container.assigned_types_to_values[arg_type_to_push]
                        if arg_value.arg_source.value < ArgSource.InitValue.value:
                            # Override value with source of higher priority:
                            arg_value.arg_source = ArgSource.InitValue
                            arg_value.arg_value = prev_envelope.data_envelope[arg_type_to_push]
                    else:
                        curr_container.assigned_types_to_values[
                            arg_type_to_push
                        ] = AssignedValue(
                            prev_envelope.data_envelope[arg_type_to_push],
                            ArgSource.InitValue,
                        )
