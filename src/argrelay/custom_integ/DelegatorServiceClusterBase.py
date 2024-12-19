from __future__ import annotations

from argrelay.custom_integ.DelegatorServiceBase import DelegatorServiceBase
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.schema_config_interp.SearchControlSchema import (
    populate_search_control,
)


def get_cluster_search_control(
) -> dict:
    return populate_search_control(
        ServiceEnvelopeClass.class_cluster.name,
        {
            ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
        },
        [
            # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
            {"class": ReservedPropName.envelope_class.name},

            {"code": ServicePropName.code_maturity.name},
            {"stage": ServicePropName.flow_stage.name},
            {"region": ServicePropName.geo_region.name},
            {"cluster": ServicePropName.cluster_name.name},
        ],
    )


class DelegatorServiceClusterBase(DelegatorServiceBase):
    """
    Provide base functionality for funcs working with `ServiceEnvelopeClass.class_cluster`.
    """
