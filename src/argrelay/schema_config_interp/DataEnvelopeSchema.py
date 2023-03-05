from marshmallow import Schema, fields, validates_schema, INCLUDE

from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import function_envelope_instance_data_desc

mongo_id_ = "_id"
"""
Field used by Mongo DB to uniquely identify every object inside a collection.
If not provided, it is auto-generated as `bson.objectid.ObjectId`.
Note that it is not serializable by `Schema.dump` and must be excluded.
for `argrelay`, if unique id is required, `envelope_id_` must be used (which is copied to `_id` on load).
"""

envelope_id_ = "envelope_id"
"""
Not required (yet) field within `envelope_metadata` with unique id for `data_envelope`.
If provided, it is given to MongoDB as `id_` (otherwise, if not provided, MongoDB auto-generates one).
"""

instance_data_ = "instance_data"
"""
Data specific to `envelope_class`.
Unlike `envelope_payload` `argrelay` does not inspect, `instance_data` can be inspected
(if not inspected by `argrelay`, but by its plugins) and this data has schema implied or defined somewhere.
"""

envelope_payload_ = "envelope_payload"
"""
Data `argrelay` does not inspect.
"""


class DataEnvelopeSchema(Schema):
    """
    Schema for all :class:`StaticDataSchema.data_envelopes`

    Note that this schema definition (unlike many others) is not used to `Schema.dump` `dict` instances
    because `data_envelope`-s contain arbitrary top-level keys used as (search) metadata.
    Because these top-level keys are arbitrary, they cannot be defined in this schema.
    Because they cannot be defined in the schema, they do not survive `Schema.dump`.
    This is a known issue/limitation of `marshmallow` - the `Meta.unknown` field is only used on `Schema.load`
    to allow extra keys in, but `Schema.dump` simply do not serialize them.
    See these fields (which should otherwise use `DataEnvelopeSchema`):
    *   `InvocationInputSchema.data_envelopes`
    *   `EnvelopeContainerSchema.data_envelope`
    *   `StaticDataSchema.data_envelopes`
    """

    class Meta:
        # All other fields of data envelope becomes its metadata available for search queries.
        # Note that it does not work for `Schema.dump`:
        unknown = INCLUDE
        strict = True

    envelope_id = fields.String(
        # TODO: make it required for predictability - isn't it required?
        required = False,
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

    @validates_schema
    def validate_known(self, input_dict, **kwargs):
        if input_dict[ReservedArgType.EnvelopeClass.name] == ReservedEnvelopeClass.ClassFunction.name:
            function_envelope_instance_data_desc.validate_dict(input_dict[instance_data_])


data_envelope_desc = TypeDesc(
    dict_schema = DataEnvelopeSchema(),
    ref_name = DataEnvelopeSchema.__name__,
    dict_example = {
        envelope_id_: "some_unique_id",
        instance_data_: function_envelope_instance_data_desc.dict_example,
        envelope_payload_: {},
        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
        "SomeTypeA": "A_value_1",
        "SomeTypeB": "B_value_1",
        "SomeTypeC": "C_value_1",
    },
    default_file_path = "",
)
