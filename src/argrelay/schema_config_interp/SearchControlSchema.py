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

arg_name_to_prop_name_map_ = "arg_name_to_prop_name_map"
"""
List of `arg_name`-s to use for `dictated_arg`-s during interpretation and `prop_name`-s to use in query.
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
    # *   How they are mapped to `arg_name`-s - see:
    #     *   FS_10_93_78_10: `arg_name_to_prop_name_map`
    #     *   FS_20_88_05_60: `dictated_arg`-s: maps `arg_name` (in command line) to `prop_name` (in `data_envelope`).
    # Each `list` item must contain singleton `dict` (single pair of mapping from `arg_name` to `prop_name`).
    arg_name_to_prop_name_map = fields.List(
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
        for arg_name_to_prop_name_entry in input_dict[arg_name_to_prop_name_map_]:
            # ensure there is only one `arg_name` per `arg_name_to_prop_name_entry`:
            if len(arg_name_to_prop_name_entry) != 1:
                raise ValidationError("only one key per dict is allowed")


search_control_desc = TypeDesc(
    dict_schema = SearchControlSchema(),
    ref_name = SearchControlSchema.__name__,
    dict_example = {
        collection_name_: ReservedEnvelopeClass.class_function.name,
        props_to_values_dict_: {
            "prop_name_a": "prop_value_a",
            "prop_name_b": "prop_value_b",
        },
        arg_name_to_prop_name_map_: [
            {
                "arg_name_a": "prop_name_a",
            },
            {
                "arg_name_b": "prop_name_b",
            },
        ],
    },
    default_file_path = "",
)


def populate_search_control(
    collection_name: str,
    props_to_values_dict: dict[str, str],
    arg_name_to_prop_name_map: list[dict],
) -> dict:
    search_control: dict = {
        collection_name_: collection_name,
        props_to_values_dict_: props_to_values_dict,
        arg_name_to_prop_name_map_: arg_name_to_prop_name_map,
    }

    return search_control
