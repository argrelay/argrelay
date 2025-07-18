from __future__ import annotations

from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialFunc import SpecialFunc
from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorNoopBase import (
    DelegatorNoopBase,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay_schema_config_server.schema_config_server_app.CompositeNodeSchema import (
    func_id_,
)


class DelegatorNoopUnpluggedFunc(DelegatorNoopBase):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [
            {
                instance_data_: {
                    func_id_: SpecialFunc.func_id_unplugged.name,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Function which does nothing and is not supposed to be plugged in",
                # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
                # Tagged as `FuncState.fs_ignorable` but, if unplugged, it becomes `FuncState.func_id_unplugged`:
                ReservedPropName.func_state.name: FuncState.fs_ignorable.name,
                ReservedPropName.func_id.name: SpecialFunc.func_id_unplugged.name,
            },
        ]
        return func_envelopes
