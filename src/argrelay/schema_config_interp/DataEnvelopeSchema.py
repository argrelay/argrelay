from marshmallow import Schema, fields, validates_schema, INCLUDE, post_dump

from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.TypeDesc import TypeDesc
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
Not required field with unique id for `data_envelope`.
If provided, it is given to MongoDB as `mongo_id_` (otherwise, if not provided, MongoDB auto-generates one).
"""

# TODO_45_75_75_65: Merge `instance_data` into `envelop_payload`:
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
    """

    class Meta:
        # All other fields of data envelope becomes its metadata props available for search queries.
        # Note that it does not work for `Schema.dump`, only on `Schema.load`
        # (see `keep_unknown_fields` func below to work around that):
        unknown = INCLUDE
        strict = True

    envelope_id = fields.String(
        required = False,
    )

    """
    Data specific to `envelope_class`.
    Each envelope class may define its own schema for that data.
    For example, `ReservedEnvelopeClass.ClassFunction` defines `FunctionEnvelopeInstanceDataSchema`.
    """
    # TODO_45_75_75_65: Merge `instance_data` into `envelop_payload`:
    instance_data = fields.Dict(
        required = False,
    )

    """
    Arbitrary schemaless data (payload) wrapped by `DataEnvelopeSchema`.
    It is not inspected by `argrelay` layer (unlike, `instance_data`) - instead, it is passed on custom app layer.
    """
    # TODO_45_75_75_65: Merge `instance_data` into `envelop_payload`:
    envelope_payload = fields.Dict(
        required = False,
    )

    @validates_schema
    def validate_known(
        self,
        input_dict: dict,
        **kwargs,
    ):
        if input_dict.get(ReservedArgType.EnvelopeClass.name, None) == ReservedEnvelopeClass.ClassFunction.name:
            function_envelope_instance_data_desc.validate_dict(input_dict[instance_data_])

    @post_dump(pass_original = True)
    def keep_unknown_fields(
        self,
        output_dict: dict,
        orig_dict,
        **kwargs,
    ):
        """
        Dump any unknown fields in `data_envelope` as well.

        *   Because `data_envelope`-s use any (search) metadata fields, they contain arbitrary top-level keys.
        *   Because these top-level keys are arbitrary, they cannot be defined in this schema.
        *   Because they cannot be defined in the schema, they do not survive `Schema.dump`.
        This is a known issue/limitation of `marshmallow` - the `Meta.unknown` field is only used on `Schema.load`
        to allow extra keys in, but `Schema.dump` simply do not serialize them.
        This method works around it.

        See:
        https://github.com/marshmallow-code/marshmallow/issues/1545#issuecomment-947231172
        """
        for field_name in orig_dict:
            if field_name not in output_dict:
                # Do not dump `mongo_id` field because it cannot be serialized subsequently
                # (see `test_data_dump_on_server_with_non_serializable_id`):
                if field_name != mongo_id_:
                    output_dict[field_name] = orig_dict[field_name]
        return output_dict


sample_field_type_A_ = "SomeTypeA"
sample_field_type_B_ = "SomeTypeB"
sample_field_type_C_ = "SomeTypeC"

data_envelope_desc = TypeDesc(
    dict_schema = DataEnvelopeSchema(),
    ref_name = DataEnvelopeSchema.__name__,
    dict_example = {
        envelope_id_: "some_unique_id",
        instance_data_: function_envelope_instance_data_desc.dict_example,
        envelope_payload_: {},
        ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
        sample_field_type_A_: "A_value_1",
        sample_field_type_B_: "B_value_1",
        sample_field_type_C_: "C_value_1",
    },
    default_file_path = "",
)
