from __future__ import annotations

from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError, post_load

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_context.SearchControl import SearchControl

collection_name_ = "collection_name"

envelope_class_ = "envelope_class"
"""
Specifies `ReservedArgType.EnvelopeClass` to search.
"""

keys_to_types_list_ = "keys_to_types_list"
"""
List of keys to use for named args during interpretation and arg types to use in query.
"""


class SearchControlSchema(ObjectSchema):
    """
    Implements FS_31_70_49_15 # search_control

    Schema for search_control which specifies what arg types will be used in search of the `data_envelope`
    (and how they are mapped to named arg keys).
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = SearchControl

    collection_name = fields.String(
        required = True,
    )

    envelope_class = fields.String(
        required = True,
    )

    # FS_20_88_05_60: named args: maps `arg_name` (in command line) to `prop_name` (in `data_envelope`).
    # Each `list` item must contain singleton `dict` (single key-value pair).
    keys_to_types_list = fields.List(
        fields.Dict(
            # `arg_name`:
            keys = fields.String(),
            # `prop_name`:
            values = fields.String(),
            required = True,
        ),
        required = True,
    )

    @validates_schema
    def validate_known(
        self,
        input_dict: dict,
        **kwargs,
    ):
        for key_to_type_entry in input_dict[keys_to_types_list_]:
            # ensure there is only one key per dict:
            if len(key_to_type_entry) != 1:
                raise ValidationError("only one key per dict is allowed")


search_control_desc = TypeDesc(
    dict_schema = SearchControlSchema(),
    ref_name = SearchControlSchema.__name__,
    dict_example = {
        collection_name_: ReservedEnvelopeClass.ClassFunction.name,
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


def populate_search_control(
    class_to_collection_map: dict,
    class_name: str,
    keys_to_types_list: list[dict],
) -> dict:
    # If not overridden, each class name uses collection by its own name:
    class_to_collection_map.setdefault(
        class_name,
        class_name,
    )

    search_control: dict = {
        collection_name_: class_to_collection_map[class_name],
        envelope_class_: class_name,
        keys_to_types_list_: keys_to_types_list,
    }

    return search_control
