from __future__ import annotations

from typing import Union

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.IndexModel import index_props_
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control, search_control_desc

collection_name_container_ipos_ = 1
data_envelope_container_ipos_ = 2


def get_collection_search_control(
) -> dict:
    return populate_search_control(
        ReservedEnvelopeClass.class_collection.name,
        {
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_collection.name,
        },
        [
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            {"class": ReservedPropName.envelope_class.name},

            {"collection": ReservedPropName.collection_name.name},
        ],
    )


class DelegatorDataBackendBase(DelegatorSingleFuncAbstract):
    """
    Implements base functionality for FS_74_69_61_79 get set data envelope.
    """

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
            # TODO: TODO_73_23_85_93: use helper to select container ipos:
            collection_name_container = interp_ctx.envelope_containers[
                interp_ctx.curr_interp.base_container_ipos + collection_name_container_ipos_
            ]
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

                arg_name_to_prop_name_map: list[dict] = []
                for index_prop in index_props:
                    # For metadata: `arg_name` is the same as prop name:
                    arg_name_to_prop_name_map.append({index_prop: index_prop})

                # Construct `search_control` dynamically:
                data_envelope_search_control_dict = populate_search_control(
                    collection_name,
                    {},
                    arg_name_to_prop_name_map,
                )
                data_envelope_search_control_obj = search_control_desc.dict_schema.load(
                    data_envelope_search_control_dict,
                )
                return data_envelope_search_control_obj

        else:
            return None
