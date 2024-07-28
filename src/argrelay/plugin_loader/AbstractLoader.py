from argrelay.enum_desc.PluginType import PluginType
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer
from argrelay.runtime_data.StaticData import StaticData


class AbstractLoader(AbstractPluginServer):
    """
    `LoaderPlugin` implements loading of `data_envelope` (which are later selected on the CLI via args).

    This is a way to load data once on server start.

    The source of data can be anything (hence, it is a plugin).
    """

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
