from __future__ import annotations

from marshmallow import (
    fields,
    RAISE,
)

from argrelay_api_server_cli.schema_response.EnvelopeContainerSchema import data_envelopes_
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_server.runtime_data_server_app.EnvelopeCollection import EnvelopeCollection
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import data_envelope_desc

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
