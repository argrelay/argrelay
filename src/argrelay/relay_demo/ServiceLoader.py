from __future__ import annotations

from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.NoopInvocator import NoopInvocator
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
    envelope_class_,
    instance_data_,
    context_control_,
)
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import keys_to_types_list_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    invocator_plugin_id_,
    envelope_class_queries_,
)


def _todo(self):
    # TODO: this should be generic config for (ServiceArgType, value) -> assignment of implicit args in completion mode.
    #       It is actually, when one of the envelope is singled-out.
    #       "default vs implicit":
    #       But setting it as implicit args means situation of searching objects contained by it.
    #       Another situation is to continue searching envelopes outside of it - implicit args should not be used.
    # host_name_to_args: dict[str, dict[ServiceArgType, str]]
    self.host_name_to_args = {
        "qwer": {
            ServiceArgType.CodeMaturity: "dev",
            ServiceArgType.FlowStage: "upstream",
            ServiceArgType.GeoRegion: "amer",
        }
    }

    # TODO: add generic config for (ServiceArgType, value) -> assignment of implicit args in invocation mode.

    # TODO: implement generic logic and config when one of the arg makes other required.
    # TODO: implement generic logic and config when one of the arg proposes values for other.


class ServiceLoader(AbstractLoader):

    def update_static_data(self, static_data: StaticData) -> StaticData:

        static_data = self.load_data_envelopes(static_data)

        return static_data

    # noinspection PyMethodMayBeStatic
    def load_data_envelopes(self, static_data: StaticData) -> StaticData:
        """
        The loader writes samples into `static_data["data_envelopes"]` simply from code (without any data source).
        """

        # Init type keys (if they do not exist):
        for type_name in [enum_item.name for enum_item in ServiceArgType]:
            if type_name not in static_data.known_types:
                static_data.known_types.append(type_name)

        # TODO: Consider `search_control` - see FD-2023-01-17--4:
        cluster_query = {
            envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
            keys_to_types_list_: [
                {"code": ServiceArgType.CodeMaturity.name},
                {"stage": ServiceArgType.FlowStage.name},
                {"region": ServiceArgType.GeoRegion.name},
            ],
        }

        host_query = {
            envelope_class_: ServiceEnvelopeClass.ClassHost.name,
            keys_to_types_list_: [
                {"cluster": ServiceArgType.ClusterName.name},
                {"host": ServiceArgType.HostName.name},
                {"tag": ServiceArgType.ColorTag.name},
            ],
        }

        service_query = {
            envelope_class_: ServiceEnvelopeClass.ClassService.name,
            keys_to_types_list_: [
                {"cluster": ServiceArgType.ClusterName.name},
                {"host": ServiceArgType.HostName.name},
                {"service": ServiceArgType.ServiceName.name},
                {"tag": ServiceArgType.ColorTag.name},
            ],
        }

        access_query = {
            envelope_class_: ServiceArgType.AccessType.name,
            keys_to_types_list_: [
                {"access": ServiceArgType.AccessType.name},
            ],
        }

        # TODO: This loader overwrites existing object list (it has to patch it instead).
        #       This is fine for now because `ServiceLoader` is used first in config.
        data_envelopes = [

            ############################################################################################################
            # functions

            # TODO: As of now, `ServiceLoader` is configured first (after `GitRepoLoader`), so it works.
            #       But to be robust against re-ordering, this loader should shared function names like
            #       "desc", "list", "goto" to accept `GitRepoEnvelopeClass` in addition to `ServiceEnvelopeClass`.
            {
                envelope_id_: "goto_host",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: ErrorInvocator.__name__,
                    envelope_class_queries_: [
                        cluster_query,
                        host_query,
                        access_query,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: "goto_service",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: ErrorInvocator.__name__,
                    envelope_class_queries_: [
                        cluster_query,
                        service_query,
                        access_query,
                    ],
                },
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "service",
            },
            {
                envelope_id_: "desc_host",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: NoopInvocator.__name__,
                    envelope_class_queries_: [
                        cluster_query,
                        host_query,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: "desc_service",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: NoopInvocator.__name__,
                    envelope_class_queries_: [
                        cluster_query,
                        service_query,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "service",
            },
            # TODO: Finalize (and test):
            #       Can there be functions accepting different envelopes classes
            #       (not like goto_host and goto_service specific for each)?
            #       When "list" `envelope_class_queries_` including both host and servie
            #       (ServiceEnvelopeClass.ClassService.name and ServiceEnvelopeClass.ClassHost.name),
            #       will it accept 2 (ALL) via AND or 1 (ANY) via OR?
            #       Is such distinction required?
            #       DECISION: Always always find ALL per function via AND.
            #       TODO: The function below should be split into `list_service` and `list_host`.
            # TODO: How to specify `list_service` which will list all services matching criteria (instead of trying to find one)?
            {
                envelope_id_: "list",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: NoopInvocator.__name__,
                    envelope_class_queries_: [
                        host_query,
                        service_query,
                    ],
                },
                GlobalArgType.ActionType.name: "list",
            },

            ############################################################################################################
            # clusters

            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.ClusterName.name: "dev-upstream-amer",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.ClusterName.name: "dev-upstream-emea",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.ClusterName.name: "dev-upstream-apac",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.ClusterName.name: "prod-downstream-apac",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.ClusterName.name: "qa-downstream-amer",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.ClusterName.name: "dev-downstream-emea",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                    # TODO: Fix test_data: TD-2023-01-07--1: there is no overlap after introduction of ClusterName.
                    "test_data": "TD-2023-01-07--1",
                },
                # TODO: repeated info: FD-2023-01-19--3:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.GeoRegion.name: "amer.us",
                ServiceArgType.ClusterName.name: "dev-downstream-amer.us",
            },

            ############################################################################################################
            # hosts

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-amer",
                ServiceArgType.HostName.name: "qwer",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-emea",
                ServiceArgType.HostName.name: "asdf",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-apac",
                ServiceArgType.HostName.name: "zxcv",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "prod-downstream-apac",
                ServiceArgType.HostName.name: "wert",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "qa-downstream-amer",
                ServiceArgType.HostName.name: "sdfg",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-downstream-emea",
                ServiceArgType.HostName.name: "xcvb",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                    # TODO: Fix test_data: TD-2023-01-07--1: there is no overlap after introduction of ClusterName.
                    "test_data": "TD-2023-01-07--1",
                },
                ServiceArgType.ClusterName.name: "dev-downstream-amer.us",
                ServiceArgType.HostName.name: "amer.us",
            },

            ############################################################################################################
            # services

            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-amer",
                ServiceArgType.HostName.name: "qwer",
                ServiceArgType.ServiceName.name: "service_a",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-emea",
                ServiceArgType.HostName.name: "asdf",
                ServiceArgType.ServiceName.name: "service_b",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "dev-upstream-apac",
                ServiceArgType.HostName.name: "zxcv",
                ServiceArgType.ServiceName.name: "service_c",
            },

            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                ServiceArgType.ClusterName.name: "qa-upstream-apac",
                ServiceArgType.HostName.name: "poiu",
                ServiceArgType.ServiceName.name: "service_c",
            },

            ############################################################################################################
            # `AccessType`: FD-2023-01-19--1

            {
                envelope_class_: ServiceArgType.AccessType.name,
                envelope_payload_: {
                },
                ServiceArgType.AccessType.name: "ro",
            },
            {
                envelope_class_: ServiceArgType.AccessType.name,
                envelope_payload_: {
                },
                ServiceArgType.AccessType.name: "rw",
            },
        ]

        self.generate_envelope_id(data_envelopes)

        static_data.data_envelopes.extend(data_envelopes)

        return static_data

    # noinspection PyMethodMayBeStatic
    def generate_envelope_id(self, data_envelopes: list):
        for data_envelope in data_envelopes:
            if envelope_id_ not in data_envelope:
                if envelope_class_ == ServiceEnvelopeClass.ClassHost.name:
                    data_envelope[envelope_id_] = data_envelope[ServiceArgType.HostName.name]
                if envelope_class_ == ServiceEnvelopeClass.ClassService.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServiceArgType.HostName.name]
                        + "." +
                        data_envelope[ServiceArgType.ServiceName.name]
                    )
