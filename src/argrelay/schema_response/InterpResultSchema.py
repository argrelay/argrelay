from copy import deepcopy

from marshmallow import RAISE, fields, pre_dump

from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_response.ArgValuesSchema import ArgValuesSchema, arg_values_desc
from argrelay.schema_response.EnvelopeContainerSchema import envelope_container_desc
from argrelay.schema_response.InterpResult import InterpResult

"""
Schema for the result of interpretation taken from :class:`InterpContext`
"""

all_tokens_ = "all_tokens"
excluded_tokens_ = "excluded_tokens"
consumed_arg_buckets_ = "consumed_arg_buckets"
envelope_containers_ = "envelope_containers"
tan_token_ipos_ = "tan_token_ipos"
tan_token_l_part_ = "tan_token_l_part"


class InterpResultSchema(ArgValuesSchema):
    """
    See also `InterpResult`.
    """

    class Meta:
        unknown = RAISE
        ordered = True

    model_class = InterpResult

    all_tokens = fields.List(
        fields.String(),
        required = True,
    )

    excluded_tokens = fields.List(
        fields.Integer(),
        required = True,
    )

    consumed_arg_buckets = fields.List(
        fields.List(
            fields.Integer(),
        ),
        required = True,
    )

    envelope_containers = fields.List(
        fields.Nested(envelope_container_desc.dict_schema),
        required = True,
    )

    tan_token_ipos = fields.Integer()

    tan_token_l_part = fields.String()

    @pre_dump
    def make_dict(
        self,
        input_object: InterpResult,
        **kwargs,
    ):
        data_dict = super().make_dict(input_object)
        data_dict.update({
            all_tokens_: input_object.all_tokens,
            excluded_tokens_: input_object.excluded_tokens,
            consumed_arg_buckets_: input_object.consumed_arg_buckets,
            envelope_containers_: input_object.envelope_containers,
            tan_token_ipos_: input_object.tan_token_ipos,
            tan_token_l_part_: input_object.tan_token_l_part,
        })
        return data_dict


_interp_result_example = deepcopy(arg_values_desc.dict_example)
_interp_result_example.update({
    all_tokens_: [
        "some_command",
        "unrecognized_token",
        "goto",
        "host",
        "prod",
        SpecialChar.ArgBucketDelimiter.value,
    ],
    excluded_tokens_: [
        5,
    ],
    consumed_arg_buckets_: [
        [
            0,
            2,
            3,
            4,
        ],
        [],
    ],
    envelope_containers_: [
        envelope_container_desc.dict_example,
    ],
    tan_token_ipos_: 1,
    tan_token_l_part_: "unrecognized_",
})

interp_result_desc = TypeDesc(
    dict_schema = InterpResultSchema(),
    ref_name = InterpResultSchema.__name__,
    dict_example = _interp_result_example,
    default_file_path = "",
)
