from argrelay.data_schema.GenericInterpConfigSchema import (
    GenericInterpConfigSchema,
    function_query_,
    object_class_queries_,
)
from argrelay.data_schema.ObjectClassQuerySchema import object_class_, keys_to_types_list_
from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceObjectClass import ServiceObjectClass


class DemoInterpConfigSchema(GenericInterpConfigSchema):
    pass


demo_interp_config_example = {
    function_query_: {
        object_class_: ReservedObjectClass.ClassFunction.name,
        keys_to_types_list_: [
            {
                "action": GlobalArgType.ActionType.name,
            },
            {
                "object": GlobalArgType.ObjectSelector.name,
            },
        ],
    },
    object_class_queries_: [
        {
            object_class_: ReservedObjectClass.ClassFunction.name,
            keys_to_types_list_: [
                {
                    "action": GlobalArgType.ActionType.name,
                },
                {
                    "object": GlobalArgType.ObjectSelector.name,
                },
            ],
        },
        {
            object_class_: ServiceObjectClass.ClassService.name,
            keys_to_types_list_: [
                {
                    "code": ServiceArgType.CodeMaturity.name,
                },
                {
                    "stage": ServiceArgType.FlowStage.name,
                },
                {
                    "region": ServiceArgType.GeoRegion.name,
                },
                {
                    "host": ServiceArgType.HostName.name,
                },
                {
                    "service": ServiceArgType.ServiceName.name,
                },
                {
                    "access": ServiceArgType.AccessType.name,
                },
                {
                    "tag": ServiceArgType.ColorTag.name,
                },
            ],
        },
    ],
}

demo_interp_config_desc = TypeDesc(
    object_schema = DemoInterpConfigSchema(),
    ref_name = DemoInterpConfigSchema.__name__,
    dict_example = demo_interp_config_example,
    default_file_path = "",
)
