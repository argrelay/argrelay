from argrelay.enum_desc.PluginType import PluginType
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_context.AbstractPlugin import AbstractPlugin
from argrelay.runtime_data.StaticData import StaticData


class AbstractLoader(AbstractPlugin):

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.LoaderPlugin

    def update_static_data(
        self,
        static_data: StaticData,
        query_engine: QueryEngine,
    ) -> StaticData:
        pass
