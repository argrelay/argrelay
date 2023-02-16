from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc, mongo_id_
from argrelay.schema_response.FilteredDict import FilteredDict

first_interp_factory_id_ = "first_interp_factory_id"
known_arg_types_ = "known_arg_types"
data_envelopes_ = "data_envelopes"


class StaticDataSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    first_interp_factory_id = fields.String(
        required = True,
    )

    known_arg_types = fields.List(
        fields.String(),
        required = True,
    )

    data_envelopes = fields.List(
        FilteredDict(
            filtered_keys = [mongo_id_]
        ),
        required = True,
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return StaticData(
            first_interp_factory_id = input_dict[first_interp_factory_id_],
            known_arg_types = input_dict[known_arg_types_],
            data_envelopes = input_dict[data_envelopes_],
        )


static_data_desc = TypeDesc(
    dict_schema = StaticDataSchema(),
    ref_name = StaticDataSchema.__name__,
    dict_example = {
        first_interp_factory_id_: "SomeInterp",
        known_arg_types_: [
            "SomeTypeA",
            "SomeTypeB",
        ],
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
    },
    default_file_path = "",
)
