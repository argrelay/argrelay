from __future__ import annotations

import json
from typing import Union

from argrelay.plugin_delegator.delegator_utils import redirect_to_no_func_error
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import (
    AbstractDelegator,
    get_func_id_from_invocation_input,
    get_func_id_from_interp_ctx,
)
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import index_props_
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
    envelope_payload_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control, search_control_desc
from argrelay.schema_response.InvocationInput import InvocationInput

collection_name_container_ipos_ = 1
data_envelope_container_ipos_ = 2


class MetadataDelegator(AbstractDelegator):
    """
    Implements FS_74_69_61_79 get set data envelope.
    """

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

        collection_search_control = populate_search_control(
            class_to_collection_map,
            ReservedEnvelopeClass.ClassCollectionMeta.name,
            [
                {"collection": ReservedPropName.collection_name.name},
            ],
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: SpecialFunc.func_id_get_data_envelopes.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    collection_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedPropName.help_hint.name: "Get `data_envelope`-s based on their `index_prop`-s.",
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_get_data_envelopes.name,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    def run_search_control(
        self,
        interp_ctx: InterpContext,
        function_data_envelope: dict,
        func_param_container_offset: int,
    ) -> Union[SearchControl, None]:
        """
        Provides `search_control` based on `index_prop` for FS_74_69_61_79 get set data envelope.
        """
        search_control_list: list[SearchControl] = self.extract_search_control_from_function_data_envelope(
            function_data_envelope,
        )
        if func_param_container_offset < len(search_control_list):
            return search_control_list[func_param_container_offset]
        elif func_param_container_offset == len(search_control_list):
            collection_name_container = interp_ctx.envelope_containers[collection_name_container_ipos_]
            collection_name_container.data_envelopes = (
                interp_ctx
                .query_engine
                .query_data_envelopes_for(collection_name_container)
            )
            if len(collection_name_container.data_envelopes) != 1:
                return None
            else:
                index_props: list[str] = collection_name_container.data_envelopes[0][envelope_payload_][index_props_]
                collection_name = collection_name_container.data_envelopes[0][ReservedPropName.collection_name.name]

                keys_to_types_list: list[dict] = []
                for index_prop in index_props:
                    # For metadata: arg name is the same as prop name:
                    keys_to_types_list.append({index_prop: index_prop})

                # Construct `search_control` dynamically:
                data_envelope_search_control_dict = populate_search_control(
                    self.server_config.class_to_collection_map,
                    # TODO: TODO_08_25_32_95: redesign `class_to_collection_map`:
                    #       We specify `collection_name` instead of `class_name` while assuming they always match.
                    collection_name,
                    keys_to_types_list,
                )
                data_envelope_search_control_obj = search_control_desc.dict_schema.load(
                    data_envelope_search_control_dict,
                )
                return data_envelope_search_control_obj

        else:
            return None

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)

        vararg_container_ipos = data_envelope_container_ipos_

        if func_id in [
            SpecialFunc.func_id_get_data_envelopes.name,
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
        else:
            # Plugin is given a function name it does not know:
            raise RuntimeError

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ):
        func_id = get_func_id_from_invocation_input(invocation_input)
        if func_id == SpecialFunc.func_id_get_data_envelopes.name:
            prohibit_unconsumed_args(invocation_input)
            for data_envelope in invocation_input.envelope_containers[data_envelope_container_ipos_].data_envelopes:
                print(json.dumps(data_envelope))
