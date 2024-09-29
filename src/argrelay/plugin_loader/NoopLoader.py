from __future__ import annotations

from argrelay.custom_integ.NoDataPropName import NoDataPropName
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_data.DataModel import DataModel
from argrelay.runtime_data.StaticData import StaticData


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

    def update_static_data(
        self,
        static_data: StaticData,
        query_engine: QueryEngine,
    ) -> StaticData:
        return static_data
