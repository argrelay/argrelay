from marshmallow import Schema, RAISE, fields, post_load, pre_dump

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc

invocator_plugin_entry_ = "invocator_plugin_entry"
function_envelope_ = "function_envelope"
assigned_types_to_values_per_envelope_ = "assigned_types_to_values_per_envelope"
interp_result_ = "interp_result"
extra_data_ = "extra_data"


class InvocationInputSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    invocator_plugin_entry = fields.Nested(
        plugin_entry_desc.dict_schema,
        required = True,
    )

    function_envelope = fields.Nested(
        data_envelope_desc.dict_schema,
        required = True,
    )

    assigned_types_to_values_per_envelope = fields.List(
        fields.Nested(data_envelope_desc.dict_schema),
        required = True,
    )

    interp_result = fields.Nested(
        interp_result_desc.dict_schema,
        required = True
    )

    extra_data = fields.Dict(
        required = False,
    )

    @pre_dump
    def make_dict(self, input_object: InvocationInput, **kwargs):
        if isinstance(input_object, InvocationInput):
            return {
                invocator_plugin_entry_: input_object.invocator_plugin_entry,
                function_envelope_: input_object.function_envelope,
                assigned_types_to_values_per_envelope_: input_object.assigned_types_to_values_per_envelope,
                interp_result_: input_object.interp_result,
                extra_data_: input_object.extra_data,
            }
        else:
            # Assuming it is as dict:
            return input_object
        pass

    @post_load
    def make_object(self, input_dict, **kwargs):
        return InvocationInput(
            invocator_plugin_entry = input_dict[invocator_plugin_entry_],
            function_envelope = input_dict[function_envelope_],
            assigned_types_to_values_per_envelope = input_dict[assigned_types_to_values_per_envelope_],
            interp_result = input_dict[interp_result_],
            extra_data = {},
        )


_invocation_input_example = {
    invocator_plugin_entry_: plugin_entry_desc.dict_example,
    function_envelope_: data_envelope_desc.dict_example,
    assigned_types_to_values_per_envelope_: [
        data_envelope_desc.dict_example,
    ],
    interp_result_: interp_result_desc.dict_example,
    extra_data_: {},
}

invocation_input_desc = TypeDesc(
    dict_schema = InvocationInputSchema(),
    ref_name = InvocationInputSchema.__name__,
    dict_example = _invocation_input_example,
    default_file_path = "",
)
