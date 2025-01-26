from __future__ import annotations

from argrelay_api_plugin_server_abstract.AbstractPluginServer import AbstractPluginServer
from argrelay_app_server.relay_server.IndexModel import IndexModel
from argrelay_app_server.relay_server.QueryEngine import QueryEngine
from argrelay_lib_root.enum_desc.PluginType import PluginType
from argrelay_schema_config_server.runtime_data_server_app.EnvelopeCollection import EnvelopeCollection


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

    def list_index_models(
        self,
    ) -> list[IndexModel]:
        """
        Provides list of index models for FS_45_08_22_15 index model API.

        TODO: TODO_23_17_31_04: publish `index_model` by delegator plugins.
        """
        raise NotImplementedError

    def load_envelope_collections(
        self,
        query_engine: QueryEngine,
    ) -> list[EnvelopeCollection]:
        """
        Return loaded `envelope_collection`-s possibly joining them with
        data already stored in the backend accessible via `query_engine`.
        """
        return []
