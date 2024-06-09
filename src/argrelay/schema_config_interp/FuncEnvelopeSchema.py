from marshmallow import fields, validates_schema, INCLUDE

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    DataEnvelopeSchema,
    envelope_id_,
    instance_data_,
    envelope_payload_,
    sample_field_type_A_,
    sample_field_type_B_,
    sample_field_type_C_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import function_envelope_instance_data_desc


class FuncEnvelopeSchema(DataEnvelopeSchema):
    class Meta:
        # Same as in base `DataEnvelopeSchema` - all unknown fields used as search props:
        unknown = INCLUDE
        strict = True

    envelope_payload = fields.Dict(
        required = False,
    )

    @validates_schema
    def validate_known(
        self,
        input_dict: dict,
        **kwargs,
    ):
        assert input_dict.get(ReservedPropName.envelope_class.name, None) == ReservedEnvelopeClass.ClassFunction.name
        function_envelope_instance_data_desc.validate_dict(input_dict[instance_data_])


func_id_some_func_ = "func_id_some_func"

func_envelope_desc = TypeDesc(
    dict_schema = DataEnvelopeSchema(),
    ref_name = DataEnvelopeSchema.__name__,
    dict_example = {
        # TODO: Do we need to duplicate `envelope_id_` and `ReservedPropName.func_id.name`?
        envelope_id_: func_id_some_func_,
        instance_data_: function_envelope_instance_data_desc.dict_example,
        envelope_payload_: {},
        sample_field_type_A_: "A_value_1",
        sample_field_type_B_: "B_value_1",
        sample_field_type_C_: "C_value_1",
        ReservedPropName.envelope_class.name: ReservedEnvelopeClass.ClassFunction.name,
        ReservedPropName.help_hint.name: f"Some help hint",
        ReservedPropName.func_state.name: FuncState.demo.name,
        ReservedPropName.func_id.name: func_id_some_func_,
    },
    default_file_path = "",
)
