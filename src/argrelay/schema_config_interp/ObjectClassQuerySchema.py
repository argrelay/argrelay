from marshmallow import Schema, RAISE, fields, validates_schema, ValidationError

from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.misc_helper.TypeDesc import TypeDesc

object_class_ = "object_class"
keys_to_types_list_ = "keys_to_types_list"


class ObjectClassQuerySchema(Schema):
    """
    Schema for all :class:`plugin_config.object_class_queries`
    """

    class Meta:
        unknown = RAISE
        strict = True

    object_class = fields.String()

    # List of keys to use for named args during interpretation and arg types to use in queries:
    keys_to_types_list = fields.List(
        fields.Dict(
            keys = fields.String(),
            values = fields.String(),
            required = True,
        ),
    ),

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        for key_to_type_entry in input_dict[keys_to_types_list_]:
            # ensure there is only one key per dict:
            if len(key_to_type_entry.keys()) != 1:
                raise ValidationError("only one key per dict is allowed")


object_class_query_desc = TypeDesc(
    object_schema = ObjectClassQuerySchema(),
    ref_name = ObjectClassQuerySchema.__name__,
    dict_example = {
        object_class_: ReservedObjectClass.ClassFunction.name,
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
