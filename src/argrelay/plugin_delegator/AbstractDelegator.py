from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper.AbstractPlugin import AbstractPlugin
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import function_envelope_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
    envelope_id_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc


def get_data_envelopes(
    interp_ctx: "InterpContext",
):
    return [envelope_container.data_envelope for envelope_container in interp_ctx.envelope_containers]


def get_func_name_from_container(
    interp_ctx: "InterpContext",
):
    func_data_envelope = interp_ctx.envelope_containers[(
        interp_ctx.curr_interp.base_envelope_ipos + function_envelope_ipos_
    )].data_envelope
    func_name = func_data_envelope[envelope_id_]
    return func_name


def get_func_name_from_envelope(
    data_envelopes: list[dict],
):
    func_data_envelope = data_envelopes[(
        function_envelope_ipos_
    )]
    func_name = func_data_envelope[envelope_id_]
    return func_name


class AbstractDelegator(AbstractPlugin):
    """
    `DelegatorPlugin` implements two sides:
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

    def run_fill_control(
        self,
        interp_ctx: "InterpContext",
    ):
        pass

    def run_interp_control(
        self,
        curr_interp: "AbstractInterp",
    ):
        pass

    def run_invoke_control(
        self,
        interp_ctx: "InterpContext",
        local_server: "LocalServer",
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
