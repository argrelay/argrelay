from __future__ import annotations

from argrelay.custom_integ.NoDataPropName import NoDataPropName
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.DataModel import DataModel


class NoopLoader(AbstractLoader):

    def list_data_models(
        self,
    ) -> list[DataModel]:
        return [
            DataModel(
                collection_name = ReservedEnvelopeClass.ClassNoData.name,
                class_name = ReservedEnvelopeClass.ClassNoData.name,
                index_props = [e.name for e in NoDataPropName],
            ),
        ]
