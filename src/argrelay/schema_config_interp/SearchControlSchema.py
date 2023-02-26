from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError, post_load

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.runtime_context.SearchControl import SearchControl

envelope_class_ = "envelope_class"
"""
Specifies `ReservedArgType.EnvelopeClass` to search.
"""

keys_to_types_list_ = "keys_to_types_list"
"""
List of keys to use for named args during interpretation and arg types to use in query.
"""


class SearchControlSchema(Schema):
    """
    Implements FS_31_70_49_15 # search_control

    Schema for search_control which specifies what arg types will be used in search of the `data_envelope`
    (and how they are mapped to named arg keys).
    """

    class Meta:
        unknown = RAISE
        strict = True

    envelope_class = fields.String()

    keys_to_types_list = fields.List(
        fields.Dict(
            keys = fields.String(),
            values = fields.String(),
            required = True,
        ),
        required = True,
    )

    @post_load
    def make_object(self, input_dict, **kwargs):
        return SearchControl(
            envelope_class = input_dict[envelope_class_],
            keys_to_types_list = input_dict[keys_to_types_list_],
        )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        for key_to_type_entry in input_dict[keys_to_types_list_]:
            # ensure there is only one key per dict:
            if len(key_to_type_entry.keys()) != 1:
                raise ValidationError("only one key per dict is allowed")


search_control_desc = TypeDesc(
    dict_schema = SearchControlSchema(),
    ref_name = SearchControlSchema.__name__,
    dict_example = {
        envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
        keys_to_types_list_: [
            {
                "type_a": "TypeA",
            },
            {
                "type_b": "TypeB",
            },
        ],
    },
    default_file_path = "",
)
