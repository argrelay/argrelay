from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import envelope_class_query_desc

invocator_plugin_id_ = "invocator_plugin_id"
envelope_class_queries_ = "envelope_class_queries"


class FunctionEnvelopeInstanceDataSchema(Schema):
    """
    Schema for :class:`DataEnvelopeSchema.instance_data` of :class:`ReservedEnvelopeClass.ClassFunction`
    """

    class Meta:
        unknown = RAISE
        strict = True

    invocator_plugin_id = fields.String(
        required = True,
    )

    envelope_class_queries = fields.List(
        fields.Nested(envelope_class_query_desc.dict_schema),
        required = True,
    )


function_envelope_instance_data_desc = TypeDesc(
    dict_schema = FunctionEnvelopeInstanceDataSchema(),
    ref_name = FunctionEnvelopeInstanceDataSchema.__name__,
    dict_example = {
        invocator_plugin_id_: "NoopInvocator",
        envelope_class_queries_: [
            envelope_class_query_desc.dict_example,
        ],
    },
    default_file_path = "",
)
