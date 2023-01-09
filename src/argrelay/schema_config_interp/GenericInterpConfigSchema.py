from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import envelope_class_query_desc

function_query_ = "function_query"
envelope_class_queries_ = "envelope_class_queries"


class GenericInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    function_query = fields.Nested(
        envelope_class_query_desc.dict_schema,
        required = True,
    )

    envelope_class_queries = fields.List(
        fields.Nested(envelope_class_query_desc.dict_schema),
        required = True,
    )


generic_interp_config_example = {
    function_query_: envelope_class_query_desc.dict_example,
    envelope_class_queries_: [
        envelope_class_query_desc.dict_example,
    ],
}

generic_interp_config_desc = TypeDesc(
    dict_schema = GenericInterpConfigSchema(),
    ref_name = GenericInterpConfigSchema.__name__,
    dict_example = generic_interp_config_example,
    default_file_path = "",
)
