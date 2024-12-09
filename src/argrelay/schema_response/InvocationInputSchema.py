from copy import deepcopy

from marshmallow import RAISE, fields

from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_delegator.SchemaCustomDataDelegatorError import error_delegator_custom_data_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.InterpResultSchema import (
    InterpResultSchema,
    interp_result_desc,
)
from argrelay.schema_response.InvocationInput import InvocationInput

call_ctx_ = "call_ctx"
delegator_plugin_entry_ = "delegator_plugin_entry"
custom_plugin_data_ = "custom_plugin_data"


class InvocationInputSchema(InterpResultSchema):
    class Meta:
        unknown = RAISE
        ordered = True

    model_class = InvocationInput

    call_ctx = fields.Nested(
        call_context_desc.dict_schema,
        required = True,
    )

    delegator_plugin_entry = fields.Nested(
        plugin_entry_desc.dict_schema,
        required = True,
    )

    custom_plugin_data = fields.Dict(
        required = False,
    )


_call_ctx_example = deepcopy(call_context_desc.dict_example)
_invocation_input_example = deepcopy(interp_result_desc.dict_example)
_invocation_input_example.update({
    call_ctx_: _call_ctx_example,
    delegator_plugin_entry_: plugin_entry_desc.dict_example,
    custom_plugin_data_: error_delegator_custom_data_desc.dict_example,
})

invocation_input_desc = TypeDesc(
    dict_schema = InvocationInputSchema(),
    ref_name = InvocationInputSchema.__name__,
    dict_example = _invocation_input_example,
    default_file_path = "",
)
