from marshmallow import Schema, INCLUDE, fields, validates_schema

from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FunctionObjectDataSchema import function_object_data_desc

object_id_ = "object_id"
object_class_ = "object_class"
object_data_ = "object_data"


class DataObjectSchema(Schema):
    """
    Schema for all :class:`StaticDataSchema.data_objects`
    """

    class Meta:
        # All other fields of data object becomes its metadata (except those below processing relies on):
        unknown = INCLUDE
        strict = True

    object_id = fields.String(
        required = False,
    )
    object_class = fields.String(
        required = True,
    )

    """
    Arbitrary data (payload) wrapped by `DataObjectSchema`.

    Each object class may define its own schema for that data.
    For example, `ReservedObjectClass.ClassFunction` defines `FunctionObjectDataSchema`.
    """
    object_data = fields.Dict(
        # TODO: make it required (and ensure it is sent in tests):
        required = False,
    )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        if input_dict[object_class_] == ReservedObjectClass.ClassFunction.name:
            function_object_data_desc.object_schema.validate(input_dict[object_class_])


data_object_desc = TypeDesc(
    object_schema = DataObjectSchema(),
    ref_name = DataObjectSchema.__name__,
    dict_example = {
        object_id_: "some_unique_id",
        object_class_: ReservedObjectClass.ClassFunction.name,
        object_data_: function_object_data_desc.dict_example,
        "SomeTypeA": "A_value_1",
        "SomeTypeB": "B_value_1",
        "SomeTypeC": "C_value_1",
    },
    default_file_path = "",
)
