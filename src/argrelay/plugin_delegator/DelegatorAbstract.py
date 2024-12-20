from __future__ import annotations

from typing import Union

from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InterpContext import function_container_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc
from argrelay.schema_response.InvocationInput import InvocationInput


def get_func_id_from_interp_ctx(
    interp_ctx: "InterpContext",
):
    """
    Used on the server-side of the plugin.
    """

    func_data_envelope = interp_ctx.envelope_containers[(
        # TODO: TODO_73_23_85_93: use helper to select container ipos:
        interp_ctx.curr_interp.base_container_ipos + function_container_ipos_
    )].data_envelopes[0]
    return func_data_envelope[instance_data_][func_id_]


def get_func_id_from_invocation_input(
    invocation_input: InvocationInput,
):
    """
    Used on the client-side of the plugin.
    """

    func_data_envelope = invocation_input.envelope_containers[
        function_container_ipos_
    ].data_envelopes[0]
    return func_data_envelope[instance_data_][func_id_]


class DelegatorAbstract(AbstractPluginServer):
    """
    `DelegatorPlugin` implements two sides:
    *   server-side `invoke_control` prepares data in :class:`InvocationInput` (whatever is necessary)
    *   client-side `invoke_action` uses data in :class:`InvocationInput` to execute the action anyway it can

    To simplify reasoning, ensure that both server-side and client-side:
    *   have access to the same code (non-breaking differences are possible, but same code version ensures that)
    *   share data only via :class:`InvocationInput`
    """

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.DelegatorPlugin

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        """
        Provide `data_envelope`-s defining each func supported by this delegator.

        The best practice is use dedicated delegator for each function (1-to-1 relationship),
        but it is not strictly required. That is why this function returns a list with
        potentially more than one func.

        Part of FS_26_43_73_72 func tree implementation.
        """
        return []

    def run_init_control(
        self,
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ) -> None:
        """
        Implements FS_46_96_59_05 `init_control`.
        """
        self.init_envelope_props(
            envelope_containers,
            curr_container_ipos,
        )

    def run_search_control(
        self,
        interp_ctx: "InterpContext",
        function_data_envelope: dict,
        func_param_container_offset: int,
    ) -> Union[SearchControl, None]:
        """
        Implements FS_31_70_49_15 `search_control`.
        """
        search_control_list: list[SearchControl] = self.extract_search_control_from_function_data_envelope(
            function_data_envelope,
        )
        if func_param_container_offset < len(search_control_list):
            return search_control_list[func_param_container_offset]
        else:
            return None

    def has_fill_control(
        self,
    ) -> bool:
        """
        FS_72_53_55_13: Optimization for showing values hidden by defaults.

        *   If returns True, `run_fill_control` will be called subsequently
            (and one more query will be run with populated values).
        *   If returns False, `run_fill_control` will not be called
            (and extra query is not necessary since there were no change of values by `run_fill_control`).
        """
        return False

    def run_fill_control(
        self,
        interp_ctx: "InterpContext",
    ) -> bool:
        """
        Implements FS_72_40_53_00 `fill_control`.

        FS_72_53_55_13: Optimization for showing values hidden by defaults:
        *   If returns True, it means at least one value was populated = one more query is necessary.
        *   If returns False, no values were changed = extra query with populated values is not necessary.
        """
        return False

    def run_interp_control(
        self,
        curr_interp: "AbstractInterp",
    ) -> Union[None, str]:
        """
        Implements FS_78_91_27_22 `interp_control`.

        Selects `plugin_id` for the next interp.
        """
        pass

    def run_invoke_control(
        self,
        interp_ctx: "InterpContext",
        local_server: "LocalServer",
    ) -> InvocationInput:
        """
        Prepare data on server side for invocation on client side.

        Implements FS_98_55_40_77 `invoke_control` on server side.
        The plugin instance is used by server on `ServerAction.RelayLineArgs`.
        """
        pass

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        """
        Execute command on client side based on data received from server side.

        Implements FS_98_55_40_77 `invoke_control` on client side.
        There is no plugin instance on client side -
        instead, the class is used directly (statically) on `ServerAction.RelayLineArgs`:
        *   without instantiating a plugin instance (it is a `@staticmethod`)
        *   specifically, without calling `AbstractPlugin.activate_plugin` (as it is non-static)
        """
        pass

    @staticmethod
    def extract_search_control_from_function_data_envelope(
        function_data_envelope: dict,
    ) -> list[SearchControl]:
        return [
            search_control_desc.dict_schema.load(search_control_dict)
            for search_control_dict in function_data_envelope[instance_data_][search_control_list_]
        ]

    @staticmethod
    def init_envelope_props(
        envelope_containers: list[EnvelopeContainer],
        curr_container_ipos: int,
    ) -> None:
        """
        Sets `prop_value`-s according to `props_to_values_dict` for FS_46_96_59_05 `init_control`
        (within `search_control` structures shared with FS_31_70_49_15 `search_control`).
        """
        curr_container = envelope_containers[curr_container_ipos]
        for prop_name, prop_value in curr_container.search_control.props_to_values_dict.items():
            curr_container.assigned_prop_name_to_prop_value[
                prop_name
            ] = AssignedValue(
                prop_value,
                ValueSource.init_value,
            )
