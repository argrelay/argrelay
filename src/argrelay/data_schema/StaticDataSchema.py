from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.data_schema.DataObjectSchema import data_object_desc
from argrelay.meta_data.StaticData import StaticData
from argrelay.misc_helper.TypeDesc import TypeDesc

first_interp_factory_id_ = "first_interp_factory_id"
types_to_values_ = "types_to_values"
data_objects_ = "data_objects"


class StaticDataSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    first_interp_factory_id = fields.String(
        required = True,
    )
    types_to_values = fields.Dict(
        keys = fields.String(),
        values = fields.List(fields.String()),
        default = {},
        required = True,
    )
    data_objects = fields.List(
        fields.Nested(data_object_desc.object_schema),
        required = True,
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return StaticData(
            first_interp_factory_id = input_dict[first_interp_factory_id_],
            types_to_values = input_dict[types_to_values_],
        )


static_data_desc = TypeDesc(
    object_schema = StaticDataSchema(),
    ref_name = StaticDataSchema.__name__,
    dict_example = {
        first_interp_factory_id_: "SomeInterp",
        types_to_values_: {
            "SomeTypeA": [
                "A_value_1",
                "A_value_2",
            ],
            "SomeTypeB": [
                "B_value_1",
                "B_value_2",
            ],
        },
        data_objects_: [
            data_object_desc.dict_example,
        ]
    },
    default_file_path = "",
)
