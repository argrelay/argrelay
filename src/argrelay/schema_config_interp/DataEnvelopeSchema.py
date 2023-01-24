from marshmallow import Schema, INCLUDE, fields, validates_schema

from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import function_envelope_instance_data_desc

envelope_id_ = "envelope_id"
envelope_class_ = "envelope_class"
instance_data_ = "instance_data"
envelope_payload_ = "envelope_payload"
context_control_ = "context_control"


class DataEnvelopeSchema(Schema):
    """
    Schema for all :class:`StaticDataSchema.data_envelopes`
    """

    class Meta:
        # All other fields of data envelope becomes its metadata (except those below processing relies on):
        unknown = INCLUDE
        strict = True

    envelope_id = fields.String(
        # TODO: make it required for predictability - isn't it required?
        required = False,
    )
    envelope_class = fields.String(
        required = True,
    )

    """
    Data specific to `envelope_class`.
    Each envelope class may define its own schema for that data.
    For example, `ReservedEnvelopeClass.ClassFunction` defines `FunctionEnvelopeInstanceDataSchema`.
    """
    instance_data = fields.Dict(
        # TODO: make it required for predictability - isn't it required?
        required = False,
    )

    """
    Arbitrary schemaless data (payload) wrapped by `DataEnvelopeSchema`.
    It is not inspected by `argrelay`.
    """
    envelope_payload = fields.Dict(
        # TODO: make it required for predictability - isn't it required?
        required = False,
    )

    """
    List of arg types to be pushed to the next `args_context` to query next `data_envelope`-s.
    """
    context_control = fields.List(
        fields.String(),
        # TODO: make it required for predictability - isn't it required?
        required = False,
    )

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        if input_dict[envelope_class_] == ReservedEnvelopeClass.ClassFunction.name:
            function_envelope_instance_data_desc.validate_dict(input_dict[instance_data_])


data_envelope_desc = TypeDesc(
    dict_schema = DataEnvelopeSchema(),
    ref_name = DataEnvelopeSchema.__name__,
    dict_example = {
        envelope_id_: "some_unique_id",
        envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
        instance_data_: function_envelope_instance_data_desc.dict_example,
        envelope_payload_: {},
        context_control_: [
            "SomeTypeB",
        ],
        "SomeTypeA": "A_value_1",
        "SomeTypeB": "B_value_1",
        "SomeTypeC": "C_value_1",
    },
    default_file_path = "",
)
