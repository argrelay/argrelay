from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FuncArgsInterpConfigSchema import (
    FuncArgsInterpConfigSchema,
    function_search_control_,
)
from argrelay.schema_config_interp.SearchControlSchema import envelope_class_, keys_to_types_list_


class DemoInterpConfigSchema(FuncArgsInterpConfigSchema):
    pass


demo_interp_config_example = {
    function_search_control_: {
        envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
        keys_to_types_list_: [
            {
                "action": GlobalArgType.ActionType.name,
            },
            {
                "object": GlobalArgType.ObjectSelector.name,
            },
        ],
    },
}

demo_interp_config_desc = TypeDesc(
    dict_schema = DemoInterpConfigSchema(),
    ref_name = DemoInterpConfigSchema.__name__,
    dict_example = demo_interp_config_example,
    default_file_path = "",
)
