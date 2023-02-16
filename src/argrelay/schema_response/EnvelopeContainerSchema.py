from marshmallow import Schema, RAISE, fields, post_load, validates_schema, ValidationError

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc, mongo_id_
from argrelay.schema_config_interp.SearchControlSchema import (
    search_control_desc,
)
from argrelay.schema_response.AssignedValueSchema import assigned_value_desc
from argrelay.schema_response.FilteredDict import FilteredDict

"""
Schema for :class:`EnvelopeContainer`
"""

search_control_ = "search_control"
data_envelope_ = "data_envelope"
found_count_ = "found_count"
assigned_types_to_values_ = "assigned_types_to_values"
remaining_types_to_values_ = "remaining_types_to_values"


class EnvelopeContainerSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    search_control = fields.Nested(
        search_control_desc.dict_schema,
        required = True,
    )

    data_envelope = FilteredDict(
        filtered_keys = [mongo_id_],
        required = True,
        allow_none = True,
    )

    found_count = fields.Integer(
        required = True,
    )

    assigned_types_to_values = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(assigned_value_desc.dict_schema),
        required = True,
    )

    remaining_types_to_values = fields.Dict(
        keys = fields.String(),
        values = fields.List(
            fields.String(),
        ),
        required = True,
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return EnvelopeContainer(
            search_control = input_dict[search_control_],
            data_envelope = input_dict[data_envelope_],
            found_count = input_dict[found_count_],
            assigned_types_to_values = input_dict[assigned_types_to_values_],
            remaining_types_to_values = input_dict[remaining_types_to_values_],
        )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        if input_dict[found_count_] > 0:
            if not input_dict[data_envelope_]:
                raise ValidationError(
                    f"`{found_count_}` is `{input_dict[found_count_]}`"
                    f"but `{data_envelope_}` is `{None}`"
                )


envelope_container_desc = TypeDesc(
    dict_schema = EnvelopeContainerSchema(),
    ref_name = EnvelopeContainerSchema.__name__,
    dict_example = {
        search_control_: search_control_desc.dict_example,
        data_envelope_: data_envelope_desc.dict_example,
        found_count_: 1,
        assigned_types_to_values_: {
            "SomeTypeA": assigned_value_desc.dict_example,
        },
        remaining_types_to_values_: {
            "SomeTypeB": [
                "B_value_1",
                "B_value_7",
            ],
            "SomeTypeC": [
                "C_value_3",
                "C_value_9",
            ],
        }
    },
    default_file_path = "",
)
