from __future__ import annotations

from argrelay_api_plugin_server_abstract.AbstractLoader import AbstractLoader
from argrelay_app_server.relay_server.IndexModel import IndexModel
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_server_plugin_core.enum_desc.NoDataPropName import NoDataPropName


class NoopLoader(AbstractLoader):

    def list_index_models(
        self,
    ) -> list[IndexModel]:
        return [
            IndexModel(
                collection_name = ReservedEnvelopeClass.class_no_data.name,
                index_props = (
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    [ReservedPropName.envelope_class.name] +
                    [e.name for e in NoDataPropName]
                )
            ),
        ]
