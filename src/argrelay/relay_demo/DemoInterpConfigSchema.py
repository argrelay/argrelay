from argrelay.meta_data.GlobalArgType import GlobalArgType
from argrelay.meta_data.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import envelope_class_, keys_to_types_list_
from argrelay.schema_config_interp.GenericInterpConfigSchema import (
    GenericInterpConfigSchema,
    function_query_,
    envelope_class_queries_,
)


class DemoInterpConfigSchema(GenericInterpConfigSchema):
    pass


demo_interp_config_example = {
    function_query_: {
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
    envelope_class_queries_: [
        {
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
        {
            envelope_class_: ServiceEnvelopeClass.ClassService.name,
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
    dict_schema = DemoInterpConfigSchema(),
    ref_name = DemoInterpConfigSchema.__name__,
    dict_example = demo_interp_config_example,
    default_file_path = "",
)
