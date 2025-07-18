from marshmallow import (
    fields,
    RAISE,
    Schema,
)

from argrelay_lib_root.misc_helper_common.TypeDesc import TypeDesc
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import (
    search_control_desc,
)

func_id_ = "func_id"
"""
An id (unique string) used by `DelegatorAbstract` to distinguish one of many functions it can potentially support.
See also `ReservedPropName.func_id`.
"""

delegator_plugin_instance_id_ = "delegator_plugin_instance_id"
search_control_list_ = "search_control_list"


# TODO: TODO_45_75_75_65: Merge `instance_data` into `envelop_payload`:
class FunctionEnvelopeInstanceDataSchema(Schema):
    """
    Schema for :class:`DataEnvelopeSchema.instance_data` of :class:`ReservedEnvelopeClass.class_function`
    """

    class Meta:
        unknown = RAISE
        strict = True

    func_id = fields.String(
        required=True,
    )

    delegator_plugin_instance_id = fields.String(
        required=True,
    )

    search_control_list = fields.List(
        fields.Nested(search_control_desc.dict_schema),
        required=True,
    )


function_envelope_instance_data_desc = TypeDesc(
    dict_schema=FunctionEnvelopeInstanceDataSchema(),
    ref_name=FunctionEnvelopeInstanceDataSchema.__name__,
    dict_example={
        func_id_: "some_function",
        # TODO: Be able to import `DelegatorNoopEmpty` and reference it via `__name__`:
        delegator_plugin_instance_id_: "DelegatorNoopEmpty.default",
        search_control_list_: [
            search_control_desc.dict_example,
        ],
    },
    default_file_path="",
)
