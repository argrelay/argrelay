from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceDelegator import ServiceDelegator
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServiceLoaderConfigSchema import (
    service_loader_config_desc,
    test_data_ids_to_load_,
)
from argrelay.custom_integ.value_constants import (
    goto_host_funct_,
    goto_service_funct_,
    list_host_func_,
    list_service_func_,
)
from argrelay.enum_desc.GlobalArgType import GlobalArgType
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper import eprint
from argrelay.plugin_delegator.NoopDelegator import NoopDelegator
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
)
from argrelay.schema_config_interp.SearchControlSchema import keys_to_types_list_, envelope_class_
from argrelay.test_helper import test_data_

cluster_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassCluster.name,
    keys_to_types_list_: [
        {"code": ServiceArgType.CodeMaturity.name},
        {"stage": ServiceArgType.FlowStage.name},
        {"region": ServiceArgType.GeoRegion.name},
        {"cluster": ServiceArgType.ClusterName.name},
    ],
}

host_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassHost.name,
    keys_to_types_list_: [
        # ClassCluster:
        {"code": ServiceArgType.CodeMaturity.name},
        {"stage": ServiceArgType.FlowStage.name},
        {"region": ServiceArgType.GeoRegion.name},
        {"cluster": ServiceArgType.ClusterName.name},
        # ClassHost:
        {"host": ServiceArgType.HostName.name},
        # ---
        {"ip": ServiceArgType.IpAddress.name},
    ],
}

service_search_control = {
    envelope_class_: ServiceEnvelopeClass.ClassService.name,
    keys_to_types_list_: [
        # ClassCluster:
        {"code": ServiceArgType.CodeMaturity.name},
        {"stage": ServiceArgType.FlowStage.name},
        {"region": ServiceArgType.GeoRegion.name},
        {"cluster": ServiceArgType.ClusterName.name},
        # ClassService:
        {"service": ServiceArgType.ServiceName.name},
        # ClassHost:
        {"host": ServiceArgType.HostName.name},
        # ---
        {"status": ServiceArgType.LiveStatus.name},
        {"dc": ServiceArgType.DataCenter.name},
        {"ip": ServiceArgType.IpAddress.name},
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
        plugin_instance_id: str,
        config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            config_dict,
        )
        service_loader_config_desc.validate_dict(config_dict)

    def update_static_data(
        self,
        static_data: StaticData,
    ) -> StaticData:

        static_data = self.load_data_envelopes(static_data)

        return static_data

    # noinspection PyMethodMayBeStatic
    def load_data_envelopes(
        self,
        static_data: StaticData,
    ) -> StaticData:
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
        self.populate_TD_43_24_76_58_single(data_envelopes)

        self.generate_envelope_id(data_envelopes)

        self.generate_help_hints(data_envelopes)

        static_data.data_envelopes.extend(data_envelopes)

        return static_data

    # noinspection PyMethodMayBeStatic
    def generate_envelope_id(
        self,
        data_envelopes: list[dict],
    ):
        for data_envelope in data_envelopes:
            if envelope_id_ not in data_envelope:
                if data_envelope[ReservedArgType.EnvelopeClass.name] == ServiceEnvelopeClass.ClassHost.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServiceArgType.ClusterName.name]
                        + "." +
                        data_envelope[ServiceArgType.HostName.name]
                    )
                if data_envelope[ReservedArgType.EnvelopeClass.name] == ServiceEnvelopeClass.ClassService.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServiceArgType.ClusterName.name]
                        + "." +
                        data_envelope[ServiceArgType.HostName.name]
                        + "." +
                        data_envelope[ServiceArgType.ServiceName.name]
                    )

    @staticmethod
    def generate_help_hints(
        data_envelopes: list[dict],
    ):
        """
        Function demos FS_71_87_33_52 help_hint for `ServiceArgType.IpAddress`.

        It simply generates `data_envelope`-s of `ReservedEnvelopeClass.ClassHelp` for
        values of `ServiceArgType.IpAddress` equal to corresponding `ServiceArgType.HostName`.
        """
        help_hint_envelopes = []
        for data_envelope in data_envelopes:
            if data_envelope[ReservedArgType.EnvelopeClass.name] == ServiceEnvelopeClass.ClassHost.name:
                if ServiceArgType.IpAddress.name in data_envelope:
                    help_hint_envelopes.append({
                        f"{ReservedArgType.EnvelopeClass.name}": f"{ReservedEnvelopeClass.ClassHelp.name}",
                        f"{ReservedArgType.ArgType.name}": f"{ServiceArgType.IpAddress.name}",
                        f"{ReservedArgType.ArgValue.name}": f"{data_envelope[ServiceArgType.IpAddress.name]}",
                        f"{ReservedArgType.HelpHint.name}": f"{data_envelope[ServiceArgType.HostName.name]}",
                    })

        data_envelopes.extend(help_hint_envelopes)

    @staticmethod
    def populate_common_functions(
        data_envelopes: list,
    ):
        data_envelopes.extend([

            ############################################################################################################
            # functions

            # TODO: As of now, `ServiceLoader` is configured first (after `GitRepoLoader`), so it works.
            #       But to be robust against re-ordering, this loader should share function names like
            #       "desc", "list", "goto" to accept `GitRepoEnvelopeClass` in addition to `ServiceEnvelopeClass`.
            {
                envelope_id_: goto_host_funct_,
                instance_data_: {
                    delegator_plugin_instance_id_: ServiceDelegator.__name__,
                    search_control_list_: [
                        host_search_control,
                        access_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Go (log in) to remote host",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: goto_service_funct_,
                instance_data_: {
                    delegator_plugin_instance_id_: ServiceDelegator.__name__,
                    search_control_list_: [
                        service_search_control,
                        access_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Go (log in) to remote host and dir path with specified service",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "goto",
                GlobalArgType.ObjectSelector.name: "service",
            },
            {
                envelope_id_: "desc_host",
                instance_data_: {
                    delegator_plugin_instance_id_: NoopDelegator.__name__,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Describe remote host",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: "desc_service",
                instance_data_: {
                    delegator_plugin_instance_id_: NoopDelegator.__name__,
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "Describe service instance",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "desc",
                GlobalArgType.ObjectSelector.name: "service",
            },
            {
                envelope_id_: list_host_func_,
                instance_data_: {
                    delegator_plugin_instance_id_: ServiceDelegator.__name__,
                    search_control_list_: [
                        host_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "List remote hosts matching search query",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "list",
                GlobalArgType.ObjectSelector.name: "host",
            },
            {
                envelope_id_: list_service_func_,
                instance_data_: {
                    delegator_plugin_instance_id_: ServiceDelegator.__name__,
                    search_control_list_: [
                        service_search_control,
                    ],
                },
                ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
                ReservedArgType.HelpHint.name: "List service instances matching search query",
                GlobalArgType.FunctionCategory.name: "external",
                GlobalArgType.ActionType.name: "list",
                GlobalArgType.ObjectSelector.name: "service",
            },
        ])

    def is_test_data_allowed(
        self,
        test_data_id: str,
    ) -> bool:
        if test_data_id in self.config_dict[test_data_ids_to_load_]:
            return True
        return False

    @staticmethod
    def populate_common_AccessType(data_envelopes: list):

        data_envelopes.extend([

            ############################################################################################################
            # `AccessType`: FS_24_50_40_64

            {
                envelope_payload_: {
                },
                ReservedArgType.EnvelopeClass.name: ServiceArgType.AccessType.name,
                ServiceArgType.AccessType.name: "ro",
            },
            {
                envelope_payload_: {
                },
                ReservedArgType.EnvelopeClass.name: ServiceArgType.AccessType.name,
                ServiceArgType.AccessType.name: "rw",
            },
        ])

    def populate_TD_63_37_05_36_default(
        self,
        data_envelopes: list,
    ):
        """
        Populates TD_63_37_05_36 # demo
        """
        if not self.is_test_data_allowed("TD_63_37_05_36"):
            return

        data_envelopes.extend([

            ############################################################################################################
            # TD_63_37_05_36 # demo: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
            },

            ############################################################################################################
            # TD_63_37_05_36 # demo: hosts

            # dev

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "zxcv-du",
                ServiceArgType.IpAddress.name: "ip.192.168.1.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.11",
                ServiceArgType.HostName.name: "zxcv-dd",
                ServiceArgType.IpAddress.name: "ip.172.16.1.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "poiu-dd",
                ServiceArgType.IpAddress.name: "ip.192.168.1.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
                ServiceArgType.DataCenter.name: "dc.22",
                ServiceArgType.HostName.name: "asdf-du",
                ServiceArgType.IpAddress.name: "ip.172.16.2.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.DataCenter.name: "dc.02",
                ServiceArgType.HostName.name: "xcvb-dd",
                ServiceArgType.IpAddress.name: "ip.192.168.2.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
                ServiceArgType.DataCenter.name: "dc.03",
                ServiceArgType.HostName.name: "qwer-du",
                ServiceArgType.IpAddress.name: "ip.192.168.3.1",
            },

            # qa

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.04",
                ServiceArgType.HostName.name: "hjkl-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.4.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.44",
                ServiceArgType.HostName.name: "poiu-qu",
                ServiceArgType.IpAddress.name: "ip.172.16.4.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-amer-upstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "rtyu-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.6.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-amer-upstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "rt-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.6.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "sdfgh-qd",
                ServiceArgType.IpAddress.name: "ip.192.168.6.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "sdfgb-qd",
                ServiceArgType.IpAddress.name: "ip.192.168.6.4",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.DataCenter.name: "dc.66",
                ServiceArgType.HostName.name: "sdfg-qd",
                ServiceArgType.IpAddress.name: "ip.172.16.6.5",
            },

            # prod

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "qwer-pd-1",
                ServiceArgType.IpAddress.name: "ip.192.168.7.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "qwer-pd-3",
                ServiceArgType.IpAddress.name: "ip.192.168.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.77",
                ServiceArgType.HostName.name: "qwer-pd-2",
                ServiceArgType.IpAddress.name: "ip.172.16.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "wert-pd-1",
                ServiceArgType.IpAddress.name: "ip.192.168.7.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "wert-pd-2",
                ServiceArgType.IpAddress.name: "ip.192.168.7.4",
            },

            ############################################################################################################
            # TD_63_37_05_36 # demo: services

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "zxcv-du",
                ServiceArgType.IpAddress.name: "ip.192.168.1.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "zxcv-du",
                ServiceArgType.IpAddress.name: "ip.192.168.1.1",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "zxcv-du",
                ServiceArgType.IpAddress.name: "ip.192.168.1.1",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.11",
                ServiceArgType.HostName.name: "zxcv-dd",
                ServiceArgType.IpAddress.name: "ip.172.16.1.2",
                ServiceArgType.ServiceName.name: "tt",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.01",
                ServiceArgType.HostName.name: "poiu-dd",
                ServiceArgType.IpAddress.name: "ip.192.168.1.3",
                ServiceArgType.ServiceName.name: "xx",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
                ServiceArgType.DataCenter.name: "dc.22",
                ServiceArgType.HostName.name: "asdf-du",
                ServiceArgType.IpAddress.name: "ip.172.16.2.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-emea-upstream",
                ServiceArgType.DataCenter.name: "dc.22",
                ServiceArgType.HostName.name: "asdf-du",
                ServiceArgType.IpAddress.name: "ip.172.16.2.1",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.DataCenter.name: "dc.02",
                ServiceArgType.HostName.name: "xcvb-dd",
                ServiceArgType.IpAddress.name: "ip.192.168.2.2",
                ServiceArgType.ServiceName.name: "xx",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.DataCenter.name: "dc.02",
                ServiceArgType.HostName.name: "xcvb-dd",
                ServiceArgType.IpAddress.name: "ip.192.168.2.2",
                ServiceArgType.ServiceName.name: "zz",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "dev-amer-upstream",
                ServiceArgType.DataCenter.name: "dc.03",
                ServiceArgType.HostName.name: "qwer-du",
                ServiceArgType.IpAddress.name: "ip.192.168.3.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.04",
                ServiceArgType.HostName.name: "hjkl-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.4.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.04",
                ServiceArgType.HostName.name: "hjkl-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.4.1",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.44",
                ServiceArgType.HostName.name: "poiu-qu",
                ServiceArgType.IpAddress.name: "ip.172.16.4.2",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "qa-amer-upstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "rtyu-qu",
                ServiceArgType.IpAddress.name: "ip.192.168.6.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "sdfgh-qd",
                ServiceArgType.IpAddress.name: "ip.192.168.6.3",
                ServiceArgType.ServiceName.name: "tt1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "qa",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "qa-amer-downstream",
                ServiceArgType.DataCenter.name: "dc.06",
                ServiceArgType.HostName.name: "sdfgb-qd",
                ServiceArgType.IpAddress.name: "ip.192.168.6.4",
                ServiceArgType.ServiceName.name: "xx",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "qwer-pd-1",
                ServiceArgType.IpAddress.name: "ip.192.168.7.1",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "qwer-pd-1",
                ServiceArgType.IpAddress.name: "ip.192.168.7.1",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "qwer-pd-3",
                ServiceArgType.IpAddress.name: "ip.192.168.7.2",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.77",
                ServiceArgType.HostName.name: "qwer-pd-2",
                ServiceArgType.IpAddress.name: "ip.172.16.7.2",
                ServiceArgType.ServiceName.name: "s_a",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.77",
                ServiceArgType.HostName.name: "qwer-pd-2",
                ServiceArgType.IpAddress.name: "ip.172.16.7.2",
                ServiceArgType.ServiceName.name: "s_b",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "upstream",
                ServiceArgType.ClusterName.name: "prod-apac-upstream",
                ServiceArgType.DataCenter.name: "dc.77",
                ServiceArgType.HostName.name: "qwer-pd-2",
                ServiceArgType.IpAddress.name: "ip.172.16.7.2",
                ServiceArgType.ServiceName.name: "s_c",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "wert-pd-1",
                ServiceArgType.IpAddress.name: "ip.192.168.7.3",
                ServiceArgType.ServiceName.name: "tt1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "wert-pd-2",
                ServiceArgType.IpAddress.name: "ip.192.168.7.4",
                ServiceArgType.ServiceName.name: "tt2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.CodeMaturity.name: "prod",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "prod-apac-downstream",
                ServiceArgType.DataCenter.name: "dc.07",
                ServiceArgType.HostName.name: "wert-pd-2",
                ServiceArgType.IpAddress.name: "ip.192.168.7.4",
                ServiceArgType.ServiceName.name: "xx",
            },
        ])

    def populate_TD_76_09_29_31_overlapped(
        self,
        data_envelopes: list,
    ):
        if not self.is_test_data_allowed("TD_76_09_29_31"):
            return

        data_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-amer-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
            },

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                # TD_76_09_29_31 GeoRegion set overlaps with HostName set:
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-amer-downstream",
                # TD_76_09_29_31 HostName set overlaps with GeoRegion set:
                ServiceArgType.HostName.name: "amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "amer",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-amer-downstream",
                # HostName is intentionally mathing another HostName from different GeoRegion (also named alike):
                ServiceArgType.HostName.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                # TD_76_09_29_31 GeoRegion set overlaps with HostName set:
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                # TD_76_09_29_31 HostName set overlaps with GeoRegion set:
                ServiceArgType.HostName.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                # HostName is intentionally mathing another HostName from different GeoRegion (also named alike):
                ServiceArgType.HostName.name: "amer",
            },
        ])

    def populate_TD_38_03_48_51_large_generated(
        self,
        data_envelopes: list,
    ):
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
                        envelope_payload_: {
                        },
                        test_data_: "TD_38_03_48_51",  # large generated
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
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
                            envelope_payload_: {
                            },
                            test_data_: "TD_38_03_48_51",  # large generated
                            ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                            ServiceArgType.CodeMaturity.name: code_maturity,
                            ServiceArgType.GeoRegion.name: geo_region,
                            ServiceArgType.FlowStage.name: flow_stage,
                            ServiceArgType.ClusterName.name: cluster_name,
                            ServiceArgType.HostName.name: host_name,
                        }

                        data_envelopes.append(generated_host)

                        for service_name in ["sn{:02d}".format(snn) for snn in range(0, 10)]:
                            ############################################################################################################
                            # services

                            generated_service = {
                                envelope_payload_: {
                                },
                                test_data_: "TD_38_03_48_51",  # large generated
                                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                                ServiceArgType.CodeMaturity.name: code_maturity,
                                ServiceArgType.GeoRegion.name: geo_region,
                                ServiceArgType.FlowStage.name: flow_stage,
                                ServiceArgType.ClusterName.name: cluster_name,
                                ServiceArgType.HostName.name: host_name,
                                ServiceArgType.ServiceName.name: service_name,
                            }

                            data_envelopes.append(generated_service)

    def populate_TD_43_24_76_58_single(
        self,
        data_envelopes: list,
    ):
        if not self.is_test_data_allowed("TD_43_24_76_58"):
            return

        data_envelopes.extend([

            ############################################################################################################
            # TD_43_24_76_58 # single: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
            },

            ############################################################################################################
            # TD_43_24_76_58 # single: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.HostName.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "apac",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-apac-downstream",
                ServiceArgType.HostName.name: "asdf",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.HostName.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.CodeMaturity.name: "dev",
                ServiceArgType.GeoRegion.name: "emea",
                ServiceArgType.FlowStage.name: "downstream",
                ServiceArgType.ClusterName.name: "dev-emea-downstream",
                ServiceArgType.HostName.name: "asdf",
            },
        ])
