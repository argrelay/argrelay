from __future__ import annotations

from copy import deepcopy

from marshmallow import RAISE, Schema, fields, validates_schema, pre_load

from argrelay.custom_integ.BaseConfigDelegatorConfigSchema import BaseConfigDelegatorConfigSchema, func_configs_
from argrelay.custom_integ.FuncConfigSchema import func_config_desc, func_envelope_
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from argrelay.schema_config_interp.FuncEnvelopeSchema import (
    func_id_some_func_,
)

command_template_ = "command_template"
echo_command_on_stderr_ = "echo_command_on_stderr"


class ConfigOnlyDelegatorConfigSchema(BaseConfigDelegatorConfigSchema):
    """
    Part of FS_49_96_50_77 config_only_delegator implementation.
    """

    class Meta:
        unknown = RAISE
        strict = True

    @pre_load
    def pre_load(
        self,
        input_dict: dict,
        **kwargs
    ) -> dict:
        """
        See `validate_data` why this has to be done:
        """
        for func_config in input_dict[func_configs_].values():
            func_config[func_envelope_][
                envelope_payload_
            ] = config_only_delegator_envelope_payload_desc.dict_from_input_dict(
                func_config[func_envelope_][envelope_payload_]
            )
        return input_dict

    @validates_schema
    def validate_data(
        self,
        input_dict: dict,
        **kwargs,
    ):
        """
        `BaseConfigDelegatorConfigSchema.func_configs` dict contains values with
        `FuncConfigSchema.func_envelope` of `FuncEnvelopeSchema` which allows arbitrary dict in `envelope_payload`.

        `ConfigOnlyDelegatorConfigSchema` expects them to be of `ConfigOnlyDelegatorEnvelopePayloadSchema`.
        """
        for func_config in input_dict[func_configs_].values():
            config_only_delegator_envelope_payload_desc.validate_dict(func_config[func_envelope_][envelope_payload_])


class ConfigOnlyDelegatorEnvelopePayloadSchema(Schema):
    class Meta:
        unknown = RAISE
        strict = True

    command_template = fields.String(
        required = True,
    )

    echo_command_on_stderr = fields.Boolean(
        required = False,
        load_default = False,
    )

    # TODO_54_68_18_12: Support defaults for config-only delegator:
    # Add a schema for this config but likely into _new_ `BaseConfigDelegatorEnvelopePayloadSchema`
    # as it can be used with other configurable plugins even if they do not use
    # `command_template` (as this `ConfigOnlyDelegatorEnvelopePayloadSchema` class does).

    # TODO_74_73_60_93: Support expected envelope count in config-only delegator:
    # Similar to TODO_54_68_18_12 (above), it should be part of _new_ `BaseConfigDelegatorEnvelopePayloadSchema`.


_config_only_func_config_dict_example = deepcopy(func_config_desc.dict_example)
_config_only_func_config_dict_example[func_envelope_][envelope_payload_].update({
    command_template_: "echo",
})

config_only_delegator_envelope_payload_desc = TypeDesc(
    dict_schema = ConfigOnlyDelegatorEnvelopePayloadSchema(),
    ref_name = ConfigOnlyDelegatorEnvelopePayloadSchema.__name__,
    dict_example = _config_only_func_config_dict_example,
    default_file_path = "",
)

config_only_delegator_config_desc = TypeDesc(
    dict_schema = ConfigOnlyDelegatorConfigSchema(),
    ref_name = ConfigOnlyDelegatorConfigSchema.__name__,
    dict_example = {
        func_configs_: {
            func_id_some_func_: config_only_delegator_envelope_payload_desc.dict_example,
        },
    },
    default_file_path = "",
)
