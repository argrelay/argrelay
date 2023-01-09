from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc

invocator_plugin_id_ = "invocator_plugin_id"
accept_envelope_classes_ = "accept_envelope_classes"


class FunctionEnvelopePayloadSchema(Schema):
    """
    Schema for :class:`DataEnvelopeSchema.envelope_payload` of :class:`ReservedEnvelopeClass.ClassFunction`
    """

    class Meta:
        unknown = RAISE
        strict = True

    invocator_plugin_id = fields.String(
        required = True,
    )

    accept_envelope_classes = fields.List(
        fields.String(),
        required = False,
    )


function_envelope_payload_desc = TypeDesc(
    dict_schema = FunctionEnvelopePayloadSchema(),
    ref_name = FunctionEnvelopePayloadSchema.__name__,
    dict_example = {
        invocator_plugin_id_: "NoopInvocator",
        accept_envelope_classes_: [
            "SomeClassNameA",
            "SomeClassNameB",
        ],
    },
    default_file_path = "",
)
