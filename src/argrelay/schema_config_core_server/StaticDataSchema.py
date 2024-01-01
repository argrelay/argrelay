from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import envelope_collection_desc

envelope_collections_ = "envelope_collections"


# TODO_00_79_72_55: remove in the future:
class StaticDataSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    envelope_collections = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(envelope_collection_desc.dict_schema),
        required = True,
    )

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        return StaticData(
            envelope_collections = input_dict[envelope_collections_],
        )


static_data_desc = TypeDesc(
    dict_schema = StaticDataSchema(),
    ref_name = StaticDataSchema.__name__,
    dict_example = {
        envelope_collections_: {
            ReservedEnvelopeClass.ClassFunction.name: envelope_collection_desc.dict_example,
        },
    },
    default_file_path = "",
)
