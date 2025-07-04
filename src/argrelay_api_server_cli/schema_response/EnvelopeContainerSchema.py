from marshmallow import (
    fields,
    RAISE,
)

from argrelay_api_server_cli.schema_response.AssignedValueSchema import (
    assigned_value_desc,
)
from argrelay_app_server.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay_lib_root.misc_helper_common.ObjectSchema import ObjectSchema
from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    data_envelope_desc,
)
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import (
    search_control_desc,
)

"""
Schema for :class:`EnvelopeContainer`
"""

search_control_ = "search_control"
data_envelopes_ = "data_envelopes"
found_count_ = "found_count"
used_token_bucket_ = "used_token_bucket"
assigned_prop_name_to_prop_value_ = "assigned_prop_name_to_prop_value"
remaining_prop_name_to_prop_value_ = "remaining_prop_name_to_prop_value"
filled_prop_values_hidden_by_defaults_ = "filled_prop_values_hidden_by_defaults"


class EnvelopeContainerSchema(ObjectSchema):
    class Meta:
        unknown = RAISE
        ordered = True

    model_class = EnvelopeContainer

    search_control = fields.Nested(
        search_control_desc.dict_schema,
        required=True,
    )

    data_envelopes = fields.List(
        fields.Nested(data_envelope_desc.dict_schema),
        required=True,
    )

    found_count = fields.Integer(
        required=True,
    )

    used_token_bucket = fields.Integer(
        required=True,
        allow_none=True,
    )

    assigned_prop_name_to_prop_value = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(assigned_value_desc.dict_schema),
        required=True,
    )

    remaining_prop_name_to_prop_value = fields.Dict(
        keys=fields.String(),
        values=fields.List(
            fields.String(),
        ),
        required=True,
    )

    filled_prop_values_hidden_by_defaults = fields.Dict(
        keys=fields.String(),
        values=fields.List(
            fields.String(),
        ),
        required=True,
    )


envelope_container_desc = TypeDesc(
    dict_schema=EnvelopeContainerSchema(),
    ref_name=EnvelopeContainerSchema.__name__,
    dict_example={
        search_control_: search_control_desc.dict_example,
        data_envelopes_: [
            data_envelope_desc.dict_example,
        ],
        found_count_: 1,
        used_token_bucket_: 0,
        assigned_prop_name_to_prop_value_: {
            "SomeTypeA": assigned_value_desc.dict_example,
        },
        remaining_prop_name_to_prop_value_: {
            "SomeTypeB": [
                "B_value_1",
                "B_value_7",
            ],
            "SomeTypeC": [
                "C_value_3",
                "C_value_9",
            ],
        },
        filled_prop_values_hidden_by_defaults_: {},
    },
    default_file_path="",
)
