from marshmallow import Schema, fields, RAISE

from argrelay.misc_helper.TypeDesc import TypeDesc

arg_values_ = "arg_values"

_arg_values_example = {
    arg_values_: [
        "arg_value_1",
        "arg_value_2",
        "arg_value_3",
    ],
}


# TODO: Make it base for <- `InterpResults` <- `InvocationInput`?
#       Make it possible to verify proposed arg_values in all `ServerAction`-s.
#       Append space to the command line (for surrogate token delimiter) in case of `ServerAction.RelayLineArgs`
#       to populate proposed arg_values to allow unconditionally assert proposed values in all tests
#       (for all `ServerAction`-s).
class ArgValuesSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    arg_values = fields.List(
        fields.String(default = ""),
        default = [],
        metadata = {
            "example": _arg_values_example[arg_values_],
        },
    )


arg_values_desc = TypeDesc(
    dict_schema = ArgValuesSchema(),
    ref_name = ArgValuesSchema.__name__,
    dict_example = _arg_values_example,
    default_file_path = "",
)
