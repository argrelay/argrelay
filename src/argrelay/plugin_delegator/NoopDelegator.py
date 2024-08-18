from __future__ import annotations

from argrelay.composite_forest.CompositeNodeSchema import func_id_
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput


class NoopDelegator(AbstractDelegator):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        class_to_collection_map: dict = self.server_config.class_to_collection_map

        no_data_search_control = populate_search_control(
            class_to_collection_map,
            "no_data_class",
            [
                {"no_data_key_one": "no_data_prop_one"},
                {"no_data_key_two": "no_data_prop_two"},
            ],
        )

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: SpecialFunc.func_id_unplugged.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Function which does nothing and is not supposed to be plugged in",
                # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
                # Tagged as `FuncState.fs_ignorable` but, if unplugged, it becomes `FuncState.func_id_unplugged`:
                ReservedPropName.func_state.name: FuncState.fs_ignorable.name,
                ReservedPropName.func_id.name: SpecialFunc.func_id_unplugged.name,
            },
            {
                instance_data_: {
                    func_id_: SpecialFunc.func_id_no_data.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        no_data_search_control,
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedPropName.help_hint.name: "Function which has no data it searches for and does nothing",
                ReservedPropName.func_state.name: FuncState.fs_ignorable.name,
                ReservedPropName.func_id.name: SpecialFunc.func_id_no_data.name,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.plugin_instance_entries[
                self.plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        # Do nothing:
        pass
