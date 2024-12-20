from __future__ import annotations

from argrelay.composite_forest.CompositeNodeSchema import func_id_
from argrelay.custom_integ.NoDataPropName import NoDataPropName
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.DelegatorNoopBase import DelegatorNoopBase
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control


class DelegatorNoopNoDataFunc(DelegatorNoopBase):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        no_data_search_control = populate_search_control(
            ReservedEnvelopeClass.class_no_data.name,
            {
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_no_data.name,
            },
            [
                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                {"class": ReservedPropName.envelope_class.name},

                {"no_data_arg_name_one": NoDataPropName.no_data_prop_name_one.name},
                {"no_data_arg_name_two": NoDataPropName.no_data_prop_name_two.name},
            ],
        )

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: SpecialFunc.func_id_no_data.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        no_data_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Function which has no data it searches for and does nothing",
                ReservedPropName.func_state.name: FuncState.fs_ignorable.name,
                ReservedPropName.func_id.name: SpecialFunc.func_id_no_data.name,
            },
        ]
        return func_envelopes
