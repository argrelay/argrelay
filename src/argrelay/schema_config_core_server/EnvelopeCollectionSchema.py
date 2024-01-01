from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc, mongo_id_
from argrelay.schema_response.FilteredDict import FilteredDict

index_fields_ = "index_fields"
data_envelopes_ = "data_envelopes"


class EnvelopeCollectionSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    index_fields = fields.List(
        fields.String(),
        required = False,
        load_default = [],
    )

    # TODO_00_79_72_55: do not store `data_envelopes`
    data_envelopes = fields.List(
        FilteredDict(
            filtered_keys = [mongo_id_]
        ),
        required = False,
        load_default = [],
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return EnvelopeCollection(
            index_fields = input_dict[index_fields_],
            data_envelopes = input_dict[data_envelopes_],
        )


envelope_collection_desc = TypeDesc(
    dict_schema = EnvelopeCollectionSchema(),
    ref_name = EnvelopeCollectionSchema.__name__,
    dict_example = {
        index_fields_: [
            "SomeTypeA",
            "SomeTypeB",
        ],
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)
