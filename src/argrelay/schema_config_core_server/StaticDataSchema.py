from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc, mongo_id_
from argrelay.schema_response.FilteredDict import FilteredDict

known_arg_types_ = "known_arg_types"
data_envelopes_ = "data_envelopes"


# TODO_00_79_72_55: remove in the future:
class StaticDataSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    known_arg_types = fields.List(
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
        return StaticData(
            known_arg_types = input_dict[known_arg_types_],
            data_envelopes = input_dict[data_envelopes_],
        )


static_data_desc = TypeDesc(
    dict_schema = StaticDataSchema(),
    ref_name = StaticDataSchema.__name__,
    dict_example = {
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
