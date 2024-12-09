from __future__ import annotations

from argrelay.custom_integ.DelegatorServiceBase import DelegatorServiceBase
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control


def get_host_search_control(
) -> dict:
    return populate_search_control(
        ServiceEnvelopeClass.ClassHost.name,
        {
            ReservedPropName.envelope_class.name: ServiceEnvelopeClass.ClassHost.name,
        },
        [
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            {"class": ReservedPropName.envelope_class.name},

            # ClassCluster:
            {"code": ServicePropName.code_maturity.name},
            {"stage": ServicePropName.flow_stage.name},
            {"region": ServicePropName.geo_region.name},
            {"cluster": ServicePropName.cluster_name.name},
            # ClassHost:
            {"host": ServicePropName.host_name.name},
            # ---
            {"status": ServicePropName.live_status.name},
            {"ip": ServicePropName.ip_address.name},
        ],
    )


class DelegatorServiceHostBase(DelegatorServiceBase):
    """
    Provide base functionality for funcs working with `ServiceEnvelopeClass.ClassHost`.
    """
