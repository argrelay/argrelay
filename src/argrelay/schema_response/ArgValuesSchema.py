from marshmallow import Schema, fields, RAISE, pre_dump, post_load

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_response.ArgValues import ArgValues

arg_values_ = "arg_values"

_arg_values_example = {
    arg_values_: [
        "arg_value_1",
        "arg_value_2",
        "arg_value_3",
    ],
}


# TODO_11_77_28_50: Make it possible to verify proposed arg_values in all `ServerAction`-s.
# Append space to the command line (for surrogate token delimiter) in case of `ServerAction.RelayLineArgs`
# to populate proposed arg_values to allow unconditionally assert proposed values in all tests
# (for all `ServerAction`-s).

class ArgValuesSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    model_class = ArgValues

    arg_values = fields.List(
        fields.String(default = ""),
        default = [],
        metadata = {
            "example": _arg_values_example[arg_values_],
        },
    )

    @pre_dump
    def make_dict(
        self,
        input_object: ArgValues,
        **kwargs,
    ):
        return {
            arg_values_: input_object.arg_values,
        }

    @post_load
    def make_object(
        self,
        input_dict,
        **kwargs,
    ):
        """
        Implements inheritance as described here:
        https://stackoverflow.com/a/65668854/441652
        """
        return type(self).model_class(
            **input_dict,
        )


arg_values_desc = TypeDesc(
    dict_schema = ArgValuesSchema(),
    ref_name = ArgValuesSchema.__name__,
    dict_example = _arg_values_example,
    default_file_path = "",
)
