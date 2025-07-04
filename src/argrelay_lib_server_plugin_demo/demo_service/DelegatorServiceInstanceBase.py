from __future__ import annotations

from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_server_plugin_demo.demo_service.DelegatorServiceBase import (
    DelegatorServiceBase,
)
from argrelay_lib_server_plugin_demo.demo_service.ServiceEnvelopeClass import (
    ServiceEnvelopeClass,
)
from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import (
    populate_search_control,
)


def get_service_search_control() -> dict:
    return populate_search_control(
        ServiceEnvelopeClass.class_service.name,
        {
            ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
        },
        [
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            {"class": ReservedPropName.envelope_class.name},
            # class_cluster:
            {"code": ServicePropName.code_maturity.name},
            {"stage": ServicePropName.flow_stage.name},
            {"region": ServicePropName.geo_region.name},
            {"cluster": ServicePropName.cluster_name.name},
            # class_service:
            {"group": ServicePropName.group_label.name},
            {"service": ServicePropName.service_name.name},
            {"mode": ServicePropName.run_mode.name},
            # class_host:
            {"host": ServicePropName.host_name.name},
            # ---
            {"status": ServicePropName.live_status.name},
            {"dc": ServicePropName.data_center.name},
            {"ip": ServicePropName.ip_address.name},
        ],
    )


class DelegatorServiceInstanceBase(DelegatorServiceBase):
    """
    Provide base functionality for funcs working with `ServiceEnvelopeClass.class_service`.
    """
