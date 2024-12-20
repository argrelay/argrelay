from __future__ import annotations

from argrelay.custom_integ.NoDataPropName import NoDataPropName
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.IndexModel import IndexModel


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
