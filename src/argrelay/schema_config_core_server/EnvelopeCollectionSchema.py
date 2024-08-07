from __future__ import annotations

from typing import Callable, Collection

from marshmallow import RAISE, fields

from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_

index_props_ = "index_props"


class EnvelopeCollectionSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = EnvelopeCollection

    index_props = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )

    # TODO_00_79_72_55: do not store `data_envelopes`
    data_envelopes = fields.List(
        fields.Nested(data_envelope_desc.dict_schema),
        required = False,
        load_default = [],
    )


envelope_collection_desc = TypeDesc(
    dict_schema = EnvelopeCollectionSchema(),
    ref_name = EnvelopeCollectionSchema.__name__,
    dict_example = {
        index_props_: [
            "SomeTypeA",
            "SomeTypeB",
        ],
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)


def init_envelop_collections(
    server_config: ServerConfig,
    class_names: Collection[str],
    get_index_props: Callable[[str, str], list[str]],
):
    """
    FS_56_43_05_79: Part of "search diff collection" implementation.

    Init:
    *   mapping from `class_name` to `collection_name`
    *   association of `collection_name` with its data as `EnvelopeCollection` (default = new and empty)
    *   list of `index_prop`-s for each `EnvelopeCollection` via `get_index_props`

    By default, class_name is mapped into collection_name which matches as string that class_name.
    """
    class_to_collection_map: dict = server_config.class_to_collection_map

    for class_name in class_names:
        # Default collection_name == class_name (unless overridden = specified in config explicitly):
        class_to_collection_map.setdefault(
            class_name,
            class_name,
        )
        collection_name = class_to_collection_map[class_name]
        envelope_collection = server_config.static_data.envelope_collections.setdefault(
            collection_name,
            EnvelopeCollection(
                index_props = [],
                data_envelopes = [],
            ),
        )

        index_props = envelope_collection.index_props
        for index_prop in get_index_props(collection_name, class_name):
            if index_prop not in index_props:
                index_props.append(index_prop)
