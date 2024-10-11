from __future__ import annotations

from marshmallow import RAISE, fields, validates_schema, ValidationError

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.runtime_context.SearchControl import SearchControl

collection_name_ = "collection_name"

props_to_values_dict_ = "props_to_values_dict"
"""
Dict of `prop_name` assigned to their `prop_value`-s.
"""

keys_to_props_list_ = "keys_to_props_list"
"""
List of keys to use for named args during interpretation and arg types to use in query.
"""


class SearchControlSchema(ObjectSchema):
    """
    Implements:
    *   FS_46_96_59_05 `init_control`
    *   FS_31_70_49_15 `search_control`
    """

    class Meta:
        unknown = RAISE
        strict = True

    model_class = SearchControl

    collection_name = fields.String(
        required = True,
    )

    # Specifies:
    # *   FS_46_96_59_05 `init_control`: what `prop_value` should be set for `prop_name`.
    props_to_values_dict = fields.Dict(
        # `prop_name`:
        keys = fields.String(),
        # `prop_value`:
        values = fields.String(),
        required = True,
    )

    # Specifies:
    # *   What `prop_name`-s will be used in search of the `data_envelope`.
    # *   How they are mapped to named `arg_key`-s.
    #     FS_20_88_05_60: named args: maps `arg_name` (in command line) to `prop_name` (in `data_envelope`).
    # Each `list` item must contain singleton `dict` (single key-value pair).
    keys_to_props_list = fields.List(
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
        for key_to_type_entry in input_dict[keys_to_props_list_]:
            # ensure there is only one key per dict:
            if len(key_to_type_entry) != 1:
                raise ValidationError("only one key per dict is allowed")


search_control_desc = TypeDesc(
    dict_schema = SearchControlSchema(),
    ref_name = SearchControlSchema.__name__,
    dict_example = {
        collection_name_: ReservedEnvelopeClass.ClassFunction.name,
        props_to_values_dict_: {
            "prop_a": "value_a",
            "prop_b": "value_b",
        },
        keys_to_props_list_: [
            {
                "key_a": "prop_a",
            },
            {
                "key_b": "prop_b",
            },
        ],
    },
    default_file_path = "",
)


def populate_search_control(
    collection_name: str,
    props_to_values_dict: dict[str, str],
    keys_to_props_list: list[dict],
) -> dict:

    search_control: dict = {
        collection_name_: collection_name,
        props_to_values_dict_: props_to_values_dict,
        keys_to_props_list_: keys_to_props_list,
    }

    return search_control
