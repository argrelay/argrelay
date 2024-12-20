from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    data_envelope_desc,
    sample_prop_name_a_,
    sample_prop_name_b_,
    sample_prop_name_c_,
)
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_

envelope_class_to_collection_name_map_ = "envelope_class_to_collection_name_map"
collection_name_to_index_props_map_ = "collection_name_to_index_props_map"


class ConfigOnlyLoaderConfigSchema(Schema):
    """
    Part of FS_49_96_50_77 config_only_loader implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    # Specifies `collection_name` for each `envelope_class` to load.
    # By default, if mapping for `envelope_class` is not specified,
    # the same `collection_name` is used as `envelope_class`.
    envelope_class_to_collection_name_map = fields.Dict(
        keys = fields.String(),
        values = fields.String(),
        required = False,
        load_default = {},
    )

    collection_name_to_index_props_map = fields.Dict(
        keys = fields.String(),
        values = fields.List(
            fields.String(),
            required = True,
        ),
        required = True,
    )

    data_envelopes = fields.List(
        fields.Nested(data_envelope_desc.dict_schema),
        required = True,
    )


config_only_loader_config_desc = TypeDesc(
    dict_schema = ConfigOnlyLoaderConfigSchema(),
    ref_name = ConfigOnlyLoaderConfigSchema.__name__,
    dict_example = {
        envelope_class_to_collection_name_map_: {
            ReservedEnvelopeClass.class_function.name: ReservedEnvelopeClass.class_function.name,
        },
        collection_name_to_index_props_map_: {
            ReservedEnvelopeClass.class_function.name: [
                sample_prop_name_a_,
                sample_prop_name_b_,
                sample_prop_name_c_,
            ],
        },
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)
