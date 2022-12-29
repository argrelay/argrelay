from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

accept_object_classes_ = "accept_object_classes"


class FunctionObjectDataSchema(Schema):
    """
    Schema for :class:`ReservedObjectClass.ClassFunction` object class
    """

    class Meta:
        unknown = RAISE
        strict = True

    accept_object_classes = fields.List(
        fields.String(),
        required = False,
    )


function_object_data_desc = TypeDesc(
    object_schema = FunctionObjectDataSchema(),
    ref_name = FunctionObjectDataSchema.__name__,
    dict_example = {
        accept_object_classes_: [
            "SomeClassNameA",
            "SomeClassNameB",
        ],
    },
    default_file_path = "",
)
