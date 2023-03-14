from marshmallow import Schema, RAISE, fields, post_load, pre_dump

from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.plugin_delegator.ErrorDelegatorCustomDataSchema import error_delegator_custom_data_desc
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.schema_config_interp.DataEnvelopeSchema import data_envelope_desc, mongo_id_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_entry_desc
from argrelay.schema_response.FilteredDict import FilteredDict

all_tokens_ = "all_tokens"
consumed_tokens_ = "consumed_tokens"
delegator_plugin_entry_ = "delegator_plugin_entry"
data_envelopes_ = "data_envelopes"
custom_plugin_data_ = "custom_plugin_data"


class InvocationInputSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    all_tokens = fields.List(
        fields.String(),
        required = True,
    )

    consumed_tokens = fields.List(
        fields.Integer(),
        required = True,
    )

    delegator_plugin_entry = fields.Nested(
        plugin_entry_desc.dict_schema,
        required = True,
    )

    data_envelopes = fields.List(
        FilteredDict(
            filtered_keys = [mongo_id_],
            # Some `data_envelope`-s may not be found by search -
            # instead of redirecting invocation to something like `ErrorDelegator` on server side,
            # send `None` items to decide how to handle that on client side.
            allow_none = True,
        ),
        required = True,
    )

    custom_plugin_data = fields.Dict(
        required = False,
    )

    @pre_dump
    def make_dict(self, input_object: InvocationInput, **kwargs):
        if isinstance(input_object, InvocationInput):
            return {
                all_tokens_: input_object.all_tokens,
                consumed_tokens_: input_object.consumed_tokens,
                delegator_plugin_entry_: input_object.delegator_plugin_entry,
                data_envelopes_: input_object.data_envelopes,
                custom_plugin_data_: input_object.custom_plugin_data,
            }
        else:
            # Assuming it is as dict:
            return input_object
        pass

    @post_load
    def make_object(self, input_dict, **kwargs):
        return InvocationInput(
            all_tokens = input_dict[all_tokens_],
            consumed_tokens = input_dict[consumed_tokens_],
            delegator_plugin_entry = input_dict[delegator_plugin_entry_],
            data_envelopes = input_dict[data_envelopes_],
            custom_plugin_data = input_dict[custom_plugin_data_],
        )


_invocation_input_example = {
    all_tokens_: [
        "some_command",
        "unrecognized_token",
        "goto",
        "host",
        "prod",
    ],
    consumed_tokens_: [
        0,
        2,
        3,
        4,
    ],
    delegator_plugin_entry_: plugin_entry_desc.dict_example,
    data_envelopes_: [
        data_envelope_desc.dict_example,
    ],
    custom_plugin_data_: error_delegator_custom_data_desc.dict_example,
}

invocation_input_desc = TypeDesc(
    dict_schema = InvocationInputSchema(),
    ref_name = InvocationInputSchema.__name__,
    dict_example = _invocation_input_example,
    default_file_path = "",
)
