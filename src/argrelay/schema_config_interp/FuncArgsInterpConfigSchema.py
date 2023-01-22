from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import envelope_class_query_desc

function_query_ = "function_query"


class FuncArgsInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    function_query = fields.Nested(
        envelope_class_query_desc.dict_schema,
        required = True,
    )


func_args_interp_config_example = {
    function_query_: envelope_class_query_desc.dict_example,
}

func_args_interp_config_desc = TypeDesc(
    dict_schema = FuncArgsInterpConfigSchema(),
    ref_name = FuncArgsInterpConfigSchema.__name__,
    dict_example = func_args_interp_config_example,
    default_file_path = "",
)
