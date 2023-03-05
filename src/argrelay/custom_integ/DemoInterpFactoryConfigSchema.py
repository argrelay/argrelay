from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.schema_config_interp.FuncArgsInterpConfigSchema import (
    FuncArgsInterpConfigSchema,
    function_search_control_,
    function_init_control_,
)
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_
from argrelay.schema_config_interp.SearchControlSchema import envelope_class_, keys_to_types_list_


class DemoInterpFactoryConfigSchema(FuncArgsInterpConfigSchema):
    pass


demo_interp_factory_config_example = {
    function_search_control_: {
        envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
        keys_to_types_list_: [
            {
                "category": GlobalArgType.FunctionCategory.name,
            },
            {
                "action": GlobalArgType.ActionType.name,
            },
            {
                "object": GlobalArgType.ObjectSelector.name,
            },
        ],
    },
    function_init_control_: {
        init_types_to_values_: {
            GlobalArgType.FunctionCategory.name: "internal",
            GlobalArgType.ActionType.name: "intercept",
            GlobalArgType.ObjectSelector.name: "func",
        },
    },
}

demo_interp_factory_config_desc = TypeDesc(
    dict_schema = DemoInterpFactoryConfigSchema(),
    ref_name = DemoInterpFactoryConfigSchema.__name__,
    dict_example = demo_interp_factory_config_example,
    default_file_path = "",
)
