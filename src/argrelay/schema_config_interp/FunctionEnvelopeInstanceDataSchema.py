from marshmallow import Schema, RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc

func_id_ = "func_id"
"""
An id (unique string) used by `AbstractDelegator` to distinguish one of many functions it can potentially support.
See also `ReservedArgType.FuncId`.
"""

delegator_plugin_instance_id_ = "delegator_plugin_instance_id"
search_control_list_ = "search_control_list"


class FunctionEnvelopeInstanceDataSchema(Schema):
    """
    Schema for :class:`DataEnvelopeSchema.instance_data` of :class:`ReservedEnvelopeClass.ClassFunction`
    """

    class Meta:
        unknown = RAISE
        strict = True

    func_id = fields.String(
        required = True,
    )

    delegator_plugin_instance_id = fields.String(
        required = True,
    )

    search_control_list = fields.List(
        fields.Nested(search_control_desc.dict_schema),
        required = True,
    )


function_envelope_instance_data_desc = TypeDesc(
    dict_schema = FunctionEnvelopeInstanceDataSchema(),
    ref_name = FunctionEnvelopeInstanceDataSchema.__name__,
    dict_example = {
        func_id_: "some_function",
        delegator_plugin_instance_id_: "NoopDelegator",
        search_control_list_: [
            search_control_desc.dict_example,
        ],
    },
    default_file_path = "",
)
