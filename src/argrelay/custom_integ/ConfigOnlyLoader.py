from copy import deepcopy

from argrelay.custom_integ.ConfigOnlyLoaderConfigSchema import (
    config_only_loader_config_desc,
    data_envelopes_,
    collection_name_to_index_fields_map_,
)
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections

_primitive_types = (bool, str, int, float)


def convert_envelope_fields_to_string(
    data_envelope: dict,
):
    """
    Converts primitive types to `str`.

    See also:
    https://stackoverflow.com/a/6392016/441652
    """
    for field_name, field_value in data_envelope.items():
        if isinstance(field_value, _primitive_types):
            data_envelope[field_name] = str(field_value)
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

    def update_static_data(
        self,
        static_data: StaticData,
    ) -> StaticData:

        # Config for FS_56_43_05_79 different collections:
        class_to_collection_map: dict = self.server_config.class_to_collection_map

        # FS_49_96_50_77 config_only_loader plugin:
        # *   `collection_name_to_index_fields_map`:
        collection_name_to_index_fields_map: dict[str, list[str]] = self.plugin_config_dict[
            collection_name_to_index_fields_map_
        ]
        # *   list of `data_envelope`-s (actual data):
        data_envelopes = [
            convert_envelope_fields_to_string(data_envelope)
            for data_envelope in deepcopy(self.plugin_config_dict[data_envelopes_])
        ]

        class_names: list[str] = [
            data_envelope.get(ReservedArgType.EnvelopeClass.name, ReservedEnvelopeClass.ClassUnknown.name)
            for data_envelope in data_envelopes
        ]

        init_envelop_collections(
            self.server_config,
            class_names,
            lambda _collection_name, _class_name: collection_name_to_index_fields_map[_collection_name],
        )

        for class_name in class_names:

            class_data_envelopes = static_data.envelope_collections[
                class_to_collection_map[class_name]
            ].data_envelopes

            # Keep removing `data_envelope`-s after inserting them into specific collections based on class:
            filtered_data_envelopes = list([
                data_envelope for data_envelope in data_envelopes
                if data_envelope.get(ReservedArgType.EnvelopeClass.name, None) == class_name
            ])
            class_data_envelopes.extend(filtered_data_envelopes)
            for data_envelope in filtered_data_envelopes:
                data_envelopes.remove(data_envelope)

        if len(data_envelopes) != 0:
            raise RuntimeError(f"ERROR: not all `data_envelope`-s have class assigned: {data_envelopes}")

        return static_data
