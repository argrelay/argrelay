from __future__ import annotations

from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper import eprint
from argrelay.plugin_invocator.ErrorInvocator import ErrorInvocator
from argrelay.plugin_invocator.NoopInvocator import NoopInvocator
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_demo.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.relay_demo.ServiceLoaderConfigSchema import (
    service_loader_config_desc,
    test_data_ids_to_load_,
)
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
    envelope_class_,
    instance_data_,
    context_control_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    invocator_plugin_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_
from argrelay.test_helper import test_data_


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

    # TODO: implement generic logic and config when one of the arg makes other/extra required.
    # TODO: implement generic logic and config when one of the arg proposes values for other.


cluster_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
    keys_to_types_list_: [
        {"code": ServiceArgType.CodeMaturity.name},
        {"stage": ServiceArgType.FlowStage.name},
        {"region": ServiceArgType.GeoRegion.name},
    ],
}

host_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassHost.name,
    keys_to_types_list_: [
        {"cluster": ServiceArgType.ClusterName.name},
        {"host": ServiceArgType.HostName.name},
        {"tag": ServiceArgType.ColorTag.name},
    ],
}

service_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassService.name,
    keys_to_types_list_: [
        {"cluster": ServiceArgType.ClusterName.name},
        {"host": ServiceArgType.HostName.name},
        {"service": ServiceArgType.ServiceName.name},
        {"tag": ServiceArgType.ColorTag.name},
    ],
}

access_search_control = {
    envelope_class_: ServiceArgType.AccessType.name,
    keys_to_types_list_: [
        {"access": ServiceArgType.AccessType.name},
    ],
}


# noinspection PyPep8Naming
class ServiceLoader(AbstractLoader):

    def __init__(
        self,
        config_dict: dict,
    ):
        super().__init__(config_dict)
        service_loader_config_desc.validate_dict(config_dict)

    def update_static_data(self, static_data: StaticData) -> StaticData:

        static_data = self.load_data_envelopes(static_data)

        return static_data

    # noinspection PyMethodMayBeStatic
    def load_data_envelopes(self, static_data: StaticData) -> StaticData:
        """
        The loader writes samples into `static_data[data_envelopes_]` simply from code (without any data source).
        """

        # Init type keys (if they do not exist):
        for type_name in [enum_item.name for enum_item in ServiceArgType]:
            if type_name not in static_data.known_arg_types:
                static_data.known_arg_types.append(type_name)

        # TODO: This loader overwrites existing object list (it has to patch it instead).
        #       This is fine for now because `ServiceLoader` is used first in config.
        data_envelopes = []

        self.populate_common_functions(data_envelopes)
        self.populate_common_AccessType(data_envelopes)
        self.populate_TD_63_37_05_36_default(data_envelopes)
        self.populate_TD_76_09_29_31_overlapped(data_envelopes)
        self.populate_TD_38_03_48_51_large_generated(data_envelopes)

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

    @staticmethod
    def populate_common_functions(data_envelopes: list):
        data_envelopes.extend([

            ############################################################################################################
            # functions

            # TODO: As of now, `ServiceLoader` is configured first (after `GitRepoLoader`), so it works.
            #       But to be robust against re-ordering, this loader should share function names like
            #       "desc", "list", "goto" to accept `GitRepoEnvelopeClass` in addition to `ServiceEnvelopeClass`.
            {
                envelope_id_: "goto_host",
                envelope_class_: ReservedEnvelopeClass.ClassFunction.name,
                instance_data_: {
                    invocator_plugin_id_: ErrorInvocator.__name__,
                    search_control_list_: [
                        cluster_search_control,
                        host_search_control,
                        access_search_control,
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
                    search_control_list_: [
                        cluster_search_control,
                        service_search_control,
                        access_search_control,
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
                    search_control_list_: [
                        cluster_search_control,
                        host_search_control,
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
                    search_control_list_: [
                        cluster_search_control,
                        service_search_control,
                    ],
                },
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "service",
            },
            # TODO: Finalize (and test):
            #       Can there be functions accepting different envelopes classes
            #       (not like goto_host and goto_service specific for each)?
            #       When "list" `search_control_list_` including both host and servie
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
                    search_control_list_: [
                        host_search_control,
                        service_search_control,
                    ],
                },
                GlobalArgType.ActionType.name: "list",
            },
        ])

    def is_test_data_allowed(self, test_data_id: str) -> bool:
        if test_data_id in self.config_dict[test_data_ids_to_load_]:
            return True
        return False

    @staticmethod
    def populate_common_AccessType(data_envelopes: list):

        data_envelopes.extend([

            ############################################################################################################
            # `AccessType`: FS_24_50_40_64

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
        ])

    def populate_TD_63_37_05_36_default(self, data_envelopes: list):
        """
        Populates TD_63_37_05_36 # default
        """
        if not self.is_test_data_allowed("TD_63_37_05_36"):
            return

        data_envelopes.extend([

            ############################################################################################################
            # TD_63_37_05_36 # default: clusters

            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
            },

            ############################################################################################################
            # TD_63_37_05_36 # default: hosts

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
                ServiceArgType.HostName.name: "qwer",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
                ServiceArgType.HostName.name: "asdf-du",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.HostName.name: "zxcv-du",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.HostName.name: "xcvb-dd",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.HostName.name: "poiu-qu",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.HostName.name: "sdfg-qd",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.HostName.name: "wert-pd-1",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.HostName.name: "wert-pd-2",
            },

            ############################################################################################################
            # TD_63_37_05_36 # default: services

            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.HostName.name: "zxcv-du",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
                ServiceArgType.HostName.name: "asdf-du",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
                ServiceArgType.HostName.name: "qwer-du",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.HostName.name: "xcvb-dd",
                ServiceArgType.ServiceName.name: "xx",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.HostName.name: "poiu-qu",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.HostName.name: "wert-pd-1",
                ServiceArgType.ServiceName.name: "tt1",
            },
            {
                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # default
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.HostName.name: "wert-pd-2",
                ServiceArgType.ServiceName.name: "tt2",
            },
        ])

    def populate_TD_76_09_29_31_overlapped(self, data_envelopes: list):
        if not self.is_test_data_allowed("TD_76_09_29_31"):
            return

        data_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: clusters

            {
                envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                envelope_payload_: {
                },
                # TODO: repeated info: FS_83_48_41_30:
                context_control_: [
                    ServiceArgType.ClusterName.name,
                ],
                # TODO: Fix test_data: TD_76_09_29_31 # overlapped:
                #       there is no overlap after introduction of ClusterName.
                test_data_: "TD_76_09_29_31",  # overlapped
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer.us",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-amer.us-downstream",
            },

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: hosts

            {
                envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                envelope_payload_: {
                },
                # TODO: Fix test_data: TD_76_09_29_31: # overlapped:
                #       there is no overlap after introduction of ClusterName.
                test_data_: "TD_76_09_29_31",  # overlapped
                ServiceArgType.ClusterName.name: "dev-amer.us-downstream",
                ServiceArgType.HostName.name: "amer.us",
            },
        ])

    def populate_TD_38_03_48_51_large_generated(self, data_envelopes: list):
        """
        TD_38_03_48_51: generate large data set
        """
        if not self.is_test_data_allowed("TD_38_03_48_51"):
            return

        for code_maturity in ["cm" + str(cmn) for cmn in range(0, 10)]:
            for geo_region in ["gr" + str(grn) for grn in range(0, 10)]:
                for flow_stage in ["fs" + str(fsn) for fsn in range(0, 10)]:

                    cluster_name = f"{code_maturity}-{geo_region}-{flow_stage}"

                    eprint(f"loading cluster_name={cluster_name}...")

                    #####################################################################################################
                    # clusters

                    generated_cluster = {
                        envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
                        envelope_payload_: {
                        },
                        # TODO: repeated info: FS_83_48_41_30:
                        context_control_: [
                            ServiceArgType.ClusterName.name,
                        ],
                        test_data_: "TD_38_03_48_51",  # large generated
                        ServiceArgType.CodeMaturity.name: code_maturity,
                        ServiceArgType.GeoRegion.name: geo_region,
                        ServiceArgType.FlowStage.name: flow_stage,
                        ServiceArgType.ClusterName.name: cluster_name,
                    }

                    data_envelopes.append(generated_cluster)

                    for host_name in ["hs" + str(hsn) for hsn in range(0, 10)]:

                        ################################################################################################
                        # hosts

                        generated_host = {
                            envelope_class_: ServiceEnvelopeClass.ClassHost.name,
                            envelope_payload_: {
                            },
                            test_data_: "TD_38_03_48_51",  # large generated
                            ServiceArgType.ClusterName.name: cluster_name,
                            ServiceArgType.HostName.name: host_name,
                        }

                        data_envelopes.append(generated_host)

                        for service_name in ["sn{:02d}".format(snn) for snn in range(0, 10)]:
                            ############################################################################################################
                            # services

                            generated_service = {
                                envelope_class_: ServiceEnvelopeClass.ClassService.name,
                                envelope_payload_: {
                                },
                                test_data_: "TD_38_03_48_51",  # large generated
                                ServiceArgType.ClusterName.name: cluster_name,
                                ServiceArgType.HostName.name: host_name,
                                ServiceArgType.ServiceName.name: service_name,
                            }

                            data_envelopes.append(generated_service)
