from __future__ import annotations

from copy import deepcopy

from argrelay.custom_integ.ConfigOnlyLoaderConfigSchema import (
    config_only_loader_config_desc,
    data_envelopes_,
    collection_name_to_index_props_map_,
    envelope_class_to_collection_name_map_,
)
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.IndexModel import IndexModel
from argrelay.runtime_data.ServerConfig import ServerConfig

_primitive_types = (bool, str, int, float)


def convert_envelope_fields_to_string(
    data_envelope: dict,
):
    """
    Converts primitive types to `str`.

    See also:
    https://stackoverflow.com/a/6392016/441652
    """
    for prop_name, prop_value in data_envelope.items():
        if isinstance(prop_value, _primitive_types):
            data_envelope[prop_name] = str(prop_value)
    return data_envelope


class ConfigOnlyLoader(AbstractLoader):
    """
    Implements FS_49_96_50_77 config_only_loader.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )
        self.plugin_config_dict = config_only_loader_config_desc.obj_from_input_dict(self.plugin_config_dict)

    def list_index_models(
        self,
    ) -> list[IndexModel]:

        collection_name_to_index_props_map: dict[str, list[str]] = self.plugin_config_dict[
            collection_name_to_index_props_map_
        ]
        index_models: list[IndexModel] = []
        for collection_name, index_props in collection_name_to_index_props_map.items():
            index_models.append(IndexModel(
                collection_name = collection_name,
                index_props = index_props,
            ))

        return index_models

    def load_envelope_collections(
        self,
        query_engine: QueryEngine,
    ) -> list[EnvelopeCollection]:

        # FS_49_96_50_77 config_only_loader plugin:
        # *   `envelope_class_to_collection_name_map`:
        envelope_class_to_collection_name_map: dict[str, str] = self.plugin_config_dict[
            envelope_class_to_collection_name_map_
        ]
        # *   list of `data_envelope`-s (actual data):
        data_envelopes = [
            convert_envelope_fields_to_string(data_envelope)
            for data_envelope in deepcopy(self.plugin_config_dict[data_envelopes_])
        ]

        envelope_collections: dict[str, EnvelopeCollection] = {}

        for data_envelope in data_envelopes:
            class_name = data_envelope.get(
                ReservedPropName.envelope_class.name,
                ReservedEnvelopeClass.ClassUnknown.name,
            )
            collection_name = envelope_class_to_collection_name_map.get(class_name, class_name)

            envelope_collection = envelope_collections.setdefault(
                collection_name,
                EnvelopeCollection(
                    collection_name = collection_name,
                    data_envelopes = [],
                ),
            )

            envelope_collection.data_envelopes.append(data_envelope)

        return envelope_collections.values()
