from marshmallow import Schema, INCLUDE, fields, validates_schema

from argrelay.meta_data.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FunctionEnvelopePayloadSchema import function_envelope_payload_desc

envelope_id_ = "envelope_id"
envelope_class_ = "envelope_class"
envelope_payload_ = "envelope_payload"


class DataEnvelopeSchema(Schema):
    """
    Schema for all :class:`StaticDataSchema.data_envelopes`
    """

    class Meta:
        # All other fields of data envelope becomes its metadata (except those below processing relies on):
        unknown = INCLUDE
        strict = True

    envelope_id = fields.String(
        required = False,
    )
    envelope_class = fields.String(
        required = True,
    )

    """
    Arbitrary data (payload) wrapped by `DataEnvelopeSchema`.

    Each envelope class may define its own schema for that data.
    For example, `ReservedEnvelopeClass.ClassFunction` defines `FunctionEnvelopePayloadSchema`.
    """
    envelope_payload = fields.Dict(
        # TODO: make it required (and ensure it is sent in tests):
        required = False,
    )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        if input_dict[envelope_class_] == ReservedEnvelopeClass.ClassFunction.name:
            function_envelope_payload_desc.dict_schema.validate(input_dict[envelope_class_])


data_envelope_desc = TypeDesc(
    dict_schema = DataEnvelopeSchema(),
    ref_name = DataEnvelopeSchema.__name__,
    dict_example = {
        envelope_id_: "some_unique_id",
        envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
        envelope_payload_: function_envelope_payload_desc.dict_example,
        "SomeTypeA": "A_value_1",
        "SomeTypeB": "B_value_1",
        "SomeTypeC": "C_value_1",
    },
    default_file_path = "",
)
