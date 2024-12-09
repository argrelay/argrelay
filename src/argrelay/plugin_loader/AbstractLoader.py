from __future__ import annotations

from argrelay.enum_desc.PluginType import PluginType
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_context.AbstractPluginServer import AbstractPluginServer
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.IndexModel import IndexModel


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
