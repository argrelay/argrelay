from marshmallow import Schema, RAISE, fields, post_load, pre_dump

from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.DataObjectSchema import data_object_desc
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_response.InterpResultSchema import interp_result_desc

invocator_plugin_entry_ = "invocator_plugin_entry"
function_object_ = "function_object"
assigned_types_to_values_per_object_ = "assigned_types_to_values_per_object"
interp_result_ = "interp_result"
extra_data_ = "extra_data"


class InvocationInputSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    invocator_plugin_entry = fields.Nested(
        plugin_entry_desc.object_schema,
        required = True,
    )

    # TODO: make it clear that it is function object wrapper/meta, not function object payload:
    function_object = fields.Nested(
        data_object_desc.object_schema,
        required = True,
    )

    assigned_types_to_values_per_object = fields.List(
        fields.Nested(data_object_desc.object_schema),
        required = True,
    )

    interp_result = fields.Nested(
        interp_result_desc.object_schema,
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
                function_object_: input_object.function_object,
                assigned_types_to_values_per_object_: input_object.assigned_types_to_values_per_object,
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
            function_object = input_dict[function_object_],
            assigned_types_to_values_per_object = input_dict[assigned_types_to_values_per_object_],
            interp_result = input_dict[interp_result_],
            extra_data = {},
        )


_invocation_input_example = {
    invocator_plugin_entry_: plugin_entry_desc.dict_example,
    function_object_: data_object_desc.dict_example,
    assigned_types_to_values_per_object_: [
        data_object_desc.dict_example,
    ],
    interp_result_: interp_result_desc.dict_example,
    extra_data_: {},
}

invocation_input_desc = TypeDesc(
    object_schema = InvocationInputSchema(),
    ref_name = InvocationInputSchema.__name__,
    dict_example = _invocation_input_example,
    default_file_path = "",
)
