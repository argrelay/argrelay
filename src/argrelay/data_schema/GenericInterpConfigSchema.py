from marshmallow import Schema, RAISE, fields

from argrelay.data_schema.ObjectClassQuerySchema import object_class_query_desc
from argrelay.misc_helper.TypeDesc import TypeDesc

function_query_ = "function_query"
object_class_queries_ = "object_class_queries"


class GenericInterpConfigSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    function_query = fields.Nested(
        object_class_query_desc.object_schema,
        required = True,
    )

    object_class_queries = fields.List(
        fields.Nested(object_class_query_desc.object_schema),
        required = True,
    )


generic_interp_config_example = {
    function_query_: object_class_query_desc.dict_example,
    object_class_queries_: [
        object_class_query_desc.dict_example,
    ],
}

generic_interp_config_desc = TypeDesc(
    object_schema = GenericInterpConfigSchema(),
    ref_name = GenericInterpConfigSchema.__name__,
    dict_example = generic_interp_config_example,
    default_file_path = "",
)
