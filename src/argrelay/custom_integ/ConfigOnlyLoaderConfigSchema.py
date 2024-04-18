from __future__ import annotations

from marshmallow import Schema, RAISE, fields

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    data_envelope_desc,
    sample_field_type_A_,
    sample_field_type_B_,
    sample_field_type_C_,
)
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_

collection_name_to_index_fields_map_ = "collection_name_to_index_fields_map"


class ConfigOnlyLoaderConfigSchema(Schema):
    """
    Part of FS_49_96_50_77 config_only_loader implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    collection_name_to_index_fields_map = fields.Dict(
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
        collection_name_to_index_fields_map_: {
            ReservedEnvelopeClass.ClassFunction.name: [
                sample_field_type_A_,
                sample_field_type_B_,
                sample_field_type_C_,
            ],
        },
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)
