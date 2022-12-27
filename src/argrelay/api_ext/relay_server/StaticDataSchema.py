from __future__ import annotations

from marshmallow import Schema, RAISE, fields, post_load

from argrelay.api_ext.relay_server.StaticData import StaticData
from argrelay.misc_helper.TypeDesc import TypeDesc


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

    @post_load
    def make_object(self, input_dict, **kwargs):
        return StaticData(
            first_interp_factory_id = input_dict["first_interp_factory_id"],
            types_to_values = input_dict["types_to_values"],
        )


_default_test_static_data_yaml_str = {
    "first_interp_factory_id": "SomeInterp",
    "types_to_values": {
        "SomeTypeA": [
            "A_value_1",
            "A_value_2",
        ],
        "SomeTypeB": [
            "B_value_1",
            "B_value_2",
        ],
    },
}

static_data_desc = TypeDesc(
    object_schema = StaticDataSchema(),
    ref_name = StaticDataSchema.__name__,
    dict_example = _default_test_static_data_yaml_str,
    default_file_path = "",
)
