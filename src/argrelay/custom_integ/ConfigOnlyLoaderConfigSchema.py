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

class_names_ = "class_names"
index_fields_ = "index_fields"
data_envelopes_ = "data_envelopes"


class ConfigOnlyLoaderConfigSchema(Schema):
    """
    Part of FS_49_96_50_77 config_only_loader implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    class_names = fields.List(
        fields.String,
        required = True,
    )

    index_fields = fields.List(
        fields.String,
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
        class_names_: [
            ReservedEnvelopeClass.ClassFunction.name
        ],
        index_fields_: [
            sample_field_type_A_,
            sample_field_type_B_,
            sample_field_type_C_,
        ],
        data_envelopes_: [
            data_envelope_desc,
        ],
    },
    default_file_path = "",
)
