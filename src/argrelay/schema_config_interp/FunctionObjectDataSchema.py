from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

invocator_plugin_id_ = "invocator_plugin_id"
accept_object_classes_ = "accept_object_classes"


# TODO: rename: object -> object_wrapper/object_meta (level stored and understood by argrelay), object_data -> object_payload (pass-through layer understood by plugins).
class FunctionObjectDataSchema(Schema):
    """
    Schema for :class:`DataObjectSchema.object_data` of :class:`ReservedObjectClass.ClassFunction`
    """

    class Meta:
        unknown = RAISE
        strict = True

    invocator_plugin_id = fields.String(
        required = True,
    )

    accept_object_classes = fields.List(
        fields.String(),
        required = False,
    )


function_object_data_desc = TypeDesc(
    object_schema = FunctionObjectDataSchema(),
    ref_name = FunctionObjectDataSchema.__name__,
    dict_example = {
        invocator_plugin_id_: "NoopInvocator",
        accept_object_classes_: [
            "SomeClassNameA",
            "SomeClassNameB",
        ],
    },
    default_file_path = "",
)
