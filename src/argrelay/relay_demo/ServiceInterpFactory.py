from argrelay.api_ext.relay_server.AbstractInterpFactory import AbstractInterpFactory
from argrelay.misc_helper.TypeDesc import TypeDesc
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceInterp import ServiceInterp
from argrelay.relay_server.call_context import CommandContext
from argrelay.relay_server.line_interp.GenericInterpFactory import GenericInterpConfigSchema


class ServiceInterpConfigSchema(GenericInterpConfigSchema):
    pass


service_interp_config_example = {
    "keys_to_types": {
        "action": ServiceArgType.ActionType.name,
        "code": ServiceArgType.CodeMaturity.name,
        "stage": ServiceArgType.FlowStage.name,
        "region": ServiceArgType.GeoRegion.name,
        "host": ServiceArgType.HostName.name,
        "service": ServiceArgType.ServiceName.name,
        "access": ServiceArgType.AccessType.name,
        "tag": ServiceArgType.ColorTag.name,
    },
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

    def create_interp(self, command_context: CommandContext) -> ServiceInterp:
        return ServiceInterp(command_context, self.config_dict)
