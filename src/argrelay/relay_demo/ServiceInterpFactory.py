from argrelay.data_schema.GenericInterpConfigSchema import GenericInterpConfigSchema
from argrelay.data_schema.GenericInterpConfigSchema import (
    function_query_,
    object_class_queries_,
)
from argrelay.data_schema.ObjectClassQuerySchema import object_class_, keys_to_types_list_
from argrelay.interp_plugin.AbstractInterpFactory import AbstractInterpFactory
from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceInterp import ServiceInterp
from argrelay.relay_demo.ServiceObjectClass import ServiceObjectClass
from argrelay.runtime_context.InterpContext import InterpContext


class ServiceInterpConfigSchema(GenericInterpConfigSchema):
    pass


service_interp_config_example = {
    function_query_: {
        object_class_: ReservedObjectClass.ClassFunction.name,
        keys_to_types_list_: [
            {
                "action": ServiceArgType.ActionType.name,
            },
            {
                "object": ServiceArgType.ObjectSelector.name,
            },
        ],
    },
    object_class_queries_: [
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

service_interp_config_desc = TypeDesc(
    object_schema = ServiceInterpConfigSchema(),
    ref_name = ServiceInterpConfigSchema.__name__,
    dict_example = service_interp_config_example,
    default_file_path = "",
)


class ServiceInterpFactory(AbstractInterpFactory):

    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        service_interp_config_desc.object_schema.validate(config_dict)

    def create_interp(self, interp_ctx: InterpContext) -> ServiceInterp:
        return ServiceInterp(interp_ctx, self.config_dict)
