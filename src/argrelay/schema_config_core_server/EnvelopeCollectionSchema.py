from __future__ import annotations

from marshmallow import RAISE, fields

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_response.EnvelopeContainerSchema import data_envelopes_

collection_name_ = "collection_name"


class EnvelopeCollectionSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = EnvelopeCollection

    collection_name = fields.String(
        required = True,
    )

    data_envelopes = fields.List(
        fields.Nested(data_envelope_desc.dict_schema),
        required = False,
        load_default = [],
    )


envelope_collection_desc = TypeDesc(
    dict_schema = EnvelopeCollectionSchema(),
    ref_name = EnvelopeCollectionSchema.__name__,
    dict_example = {
        collection_name_: ReservedEnvelopeClass.class_function.name,
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)
