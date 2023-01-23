from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_response.EnvelopeContainerSchema import envelope_container_desc

"""
Schema for the result of interpretation taken from :class:`InterpContext`
"""

envelope_containers_ = "envelope_containers"


class InterpResultSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    envelope_containers = fields.List(
        fields.Nested(envelope_container_desc.dict_schema),
        required = True,
    )


interp_result_desc = TypeDesc(
    dict_schema = InterpResultSchema(),
    ref_name = InterpResultSchema.__name__,
    dict_example = {
        envelope_containers_: [
            envelope_container_desc.dict_example,
        ]
    },
    default_file_path = "",
)
