from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServiceLoaderConfigSchema import (
    service_loader_config_desc,
    test_data_ids_to_load_,
)
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.misc_helper_common import eprint
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.EnvelopeCollectionSchema import init_envelop_collections
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
)
from argrelay.test_infra import test_data_


# noinspection PyPep8Naming
class ServiceLoader(AbstractLoader):
    object_multiplier: int = 10
    """
    Used by TD_38_03_48_51 to generate large data set.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

    def load_config(
        self,
        plugin_config_dict: dict,
    ) -> dict:
        return service_loader_config_desc.dict_from_input_dict(plugin_config_dict)

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
        The loader writes samples into `static_data` simply from code (without any data source).
        """

        class_to_collection_map: dict = self.server_config.class_to_collection_map

        class_names = [
            ServiceEnvelopeClass.ClassCluster.name,
            ServiceEnvelopeClass.ClassHost.name,
            ServiceEnvelopeClass.ClassService.name,
            ServiceEnvelopeClass.ClassAccessType.name,
        ]

        init_envelop_collections(
            self.server_config,
            class_names,
            # Same index fields for all collections (can be fine-tuned later):
            lambda collection_name, class_name: [enum_item.name for enum_item in ServiceArgType]
        )

        # Select `data_envelope` lists used by each collection name
        cluster_envelopes = static_data.envelope_collections[
            class_to_collection_map[ServiceEnvelopeClass.ClassCluster.name]
        ].data_envelopes
        host_envelopes = static_data.envelope_collections[
            class_to_collection_map[ServiceEnvelopeClass.ClassHost.name]
        ].data_envelopes
        service_envelopes = static_data.envelope_collections[
            class_to_collection_map[ServiceEnvelopeClass.ClassService.name]
        ].data_envelopes
        access_envelopes = static_data.envelope_collections[
            class_to_collection_map[ServiceEnvelopeClass.ClassAccessType.name]
        ].data_envelopes

        self.populate_common_access_type(access_envelopes)
        self.populate_TD_63_37_05_36_default(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )
        self.populate_TD_76_09_29_31_overlapped(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )
        self.populate_TD_99_99_88_75_mutually_exclusive(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )
        self.populate_TD_38_03_48_51_large_generated(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )
        self.populate_TD_43_24_76_58_single(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )

        self.generate_envelope_id(cluster_envelopes + host_envelopes + service_envelopes)

        self.generate_help_hints(
            class_to_collection_map,
            static_data,
        )

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
                        data_envelope[ServiceArgType.cluster_name.name]
                        + "." +
                        data_envelope[ServiceArgType.host_name.name]
                    )
                if data_envelope[ReservedArgType.EnvelopeClass.name] == ServiceEnvelopeClass.ClassService.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServiceArgType.cluster_name.name]
                        + "." +
                        data_envelope[ServiceArgType.host_name.name]
                        + "." +
                        data_envelope[ServiceArgType.service_name.name]
                        + "." +
                        data_envelope[ServiceArgType.run_mode.name]
                    )

    @staticmethod
    def generate_help_hints(
        class_to_collection_map: dict,
        static_data: StaticData,
    ):
        """
        This demos FS_71_87_33_52 help_hint for `ServiceArgType.ip_address`.

        It simply generates `data_envelope`-s of `ReservedEnvelopeClass.ClassHelp` for
        values of `ServiceArgType.ip_address` equal to corresponding `ServiceArgType.host_name`.
        """

        class_to_collection_map.setdefault(
            ReservedEnvelopeClass.ClassHelp.name,
            ReservedEnvelopeClass.ClassHelp.name,
        )
        help_hint_envelope_collection = static_data.envelope_collections.setdefault(
            class_to_collection_map[ReservedEnvelopeClass.ClassHelp.name],
            EnvelopeCollection(
                index_fields = [],
                data_envelopes = [],
            ),
        )
        help_hint_index_fields = help_hint_envelope_collection.index_fields
        help_hint_envelopes = help_hint_envelope_collection.data_envelopes

        # Init index fields (if they do not exist):
        for help_hint_index_field in [
            ReservedArgType.EnvelopeClass.name,
            ReservedArgType.ArgType.name,
            ReservedArgType.ArgValue.name,
            ReservedArgType.HelpHint.name,
        ]:
            if help_hint_index_field not in help_hint_index_fields:
                help_hint_index_fields.append(help_hint_index_field)

        # Generating
        host_envelopes = static_data.envelope_collections[
            class_to_collection_map[ServiceEnvelopeClass.ClassHost.name]
        ].data_envelopes

        for host_envelope in host_envelopes:
            # This `if`-filter is not necessary until non-host-class-envelopes
            # get stored into the same collection:
            if host_envelope[ReservedArgType.EnvelopeClass.name] == ServiceEnvelopeClass.ClassHost.name:
                if ServiceArgType.ip_address.name in host_envelope:
                    help_hint_envelopes.append({
                        f"{ReservedArgType.EnvelopeClass.name}": f"{ReservedEnvelopeClass.ClassHelp.name}",
                        f"{ReservedArgType.ArgType.name}": f"{ServiceArgType.ip_address.name}",
                        f"{ReservedArgType.ArgValue.name}": f"{host_envelope[ServiceArgType.ip_address.name]}",
                        f"{ReservedArgType.HelpHint.name}": f"{host_envelope[ServiceArgType.host_name.name]}",
                    })

    def is_test_data_allowed(
        self,
        test_data_id: str,
    ) -> bool:
        if test_data_id in self.plugin_config_dict[test_data_ids_to_load_]:
            return True
        return False

    @classmethod
    def populate_common_access_type(
        cls,
        data_envelopes: list,
    ):

        data_envelopes.extend([

            ############################################################################################################
            # `access_type`: FS_24_50_40_64

            {
                envelope_payload_: {
                },
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassAccessType.name,
                ServiceArgType.access_type.name: "ro",
            },
            {
                envelope_payload_: {
                },
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassAccessType.name,
                ServiceArgType.access_type.name: "rw",
            },
        ])

    def populate_TD_63_37_05_36_default(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        """
        Populates TD_63_37_05_36 # demo
        """
        if not self.is_test_data_allowed("TD_63_37_05_36"):
            return

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_63_37_05_36 # demo: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-emea-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
            },
        ])

        host_envelopes.extend([
            ############################################################################################################
            # TD_63_37_05_36 # demo: hosts

            # dev

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-apac-upstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "zxcv-du",
                ServiceArgType.ip_address.name: "ip.192.168.1.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.data_center.name: "dc.11",
                ServiceArgType.host_name.name: "zxcv-dd",
                ServiceArgType.ip_address.name: "ip.172.16.1.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "poiu-dd",
                ServiceArgType.ip_address.name: "ip.192.168.1.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-emea-upstream",
                ServiceArgType.data_center.name: "dc.22",
                ServiceArgType.host_name.name: "asdf-du",
                ServiceArgType.ip_address.name: "ip.172.16.2.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.data_center.name: "dc.02",
                ServiceArgType.host_name.name: "xcvb-dd",
                ServiceArgType.ip_address.name: "ip.192.168.2.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-amer-upstream",
                ServiceArgType.data_center.name: "dc.03",
                ServiceArgType.host_name.name: "qwer-du",
                ServiceArgType.ip_address.name: "ip.192.168.3.1",
            },

            # qa

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
                ServiceArgType.data_center.name: "dc.04",
                ServiceArgType.host_name.name: "hjkl-qu",
                ServiceArgType.ip_address.name: "ip.192.168.4.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
                ServiceArgType.data_center.name: "dc.44",
                ServiceArgType.host_name.name: "poiu-qu",
                ServiceArgType.ip_address.name: "ip.172.16.4.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-amer-upstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "rtyu-qu",
                ServiceArgType.ip_address.name: "ip.192.168.6.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-amer-upstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "rt-qu",
                ServiceArgType.ip_address.name: "ip.192.168.6.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "sdfgh-qd",
                ServiceArgType.ip_address.name: "ip.192.168.6.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "sdfgb-qd",
                ServiceArgType.ip_address.name: "ip.192.168.6.4",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
                ServiceArgType.data_center.name: "dc.66",
                ServiceArgType.host_name.name: "sdfg-qd",
                ServiceArgType.ip_address.name: "ip.172.16.6.5",
            },

            # prod

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "qwer-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "qwer-pd-3",
                ServiceArgType.ip_address.name: "ip.192.168.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.77",
                ServiceArgType.host_name.name: "qwer-pd-2",
                ServiceArgType.ip_address.name: "ip.172.16.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-2",
                ServiceArgType.ip_address.name: "ip.192.168.7.4",
            },
        ])

        service_envelopes.extend([
            ############################################################################################################
            # TD_63_37_05_36 # demo: services

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-apac-upstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "zxcv-du",
                ServiceArgType.ip_address.name: "ip.192.168.1.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-apac-upstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "zxcv-du",
                ServiceArgType.ip_address.name: "ip.192.168.1.1",
                ServiceArgType.service_name.name: "s_b",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-apac-upstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "zxcv-du",
                ServiceArgType.ip_address.name: "ip.192.168.1.1",
                ServiceArgType.service_name.name: "s_c",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.data_center.name: "dc.11",
                ServiceArgType.host_name.name: "zxcv-dd",
                ServiceArgType.ip_address.name: "ip.172.16.1.2",
                ServiceArgType.service_name.name: "tt",
                ServiceArgType.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.data_center.name: "dc.01",
                ServiceArgType.host_name.name: "poiu-dd",
                ServiceArgType.ip_address.name: "ip.192.168.1.3",
                ServiceArgType.service_name.name: "xx",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-emea-upstream",
                ServiceArgType.data_center.name: "dc.22",
                ServiceArgType.host_name.name: "asdf-du",
                ServiceArgType.ip_address.name: "ip.172.16.2.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-emea-upstream",
                ServiceArgType.data_center.name: "dc.22",
                ServiceArgType.host_name.name: "asdf-du",
                ServiceArgType.ip_address.name: "ip.172.16.2.1",
                ServiceArgType.service_name.name: "s_b",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.data_center.name: "dc.02",
                ServiceArgType.host_name.name: "xcvb-dd",
                ServiceArgType.ip_address.name: "ip.192.168.2.2",
                ServiceArgType.service_name.name: "xx",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.data_center.name: "dc.02",
                ServiceArgType.host_name.name: "xcvb-dd",
                ServiceArgType.ip_address.name: "ip.192.168.2.2",
                ServiceArgType.service_name.name: "zz",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "rrr",
                    "hhh",
                    "odd",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "dev-amer-upstream",
                ServiceArgType.data_center.name: "dc.03",
                ServiceArgType.host_name.name: "qwer-du",
                ServiceArgType.ip_address.name: "ip.192.168.3.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
                ServiceArgType.data_center.name: "dc.04",
                ServiceArgType.host_name.name: "hjkl-qu",
                ServiceArgType.ip_address.name: "ip.192.168.4.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
                ServiceArgType.data_center.name: "dc.04",
                ServiceArgType.host_name.name: "hjkl-qu",
                ServiceArgType.ip_address.name: "ip.192.168.4.1",
                ServiceArgType.service_name.name: "s_b",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-apac-upstream",
                ServiceArgType.data_center.name: "dc.44",
                ServiceArgType.host_name.name: "poiu-qu",
                ServiceArgType.ip_address.name: "ip.172.16.4.2",
                ServiceArgType.service_name.name: "s_c",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "qa-amer-upstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "rtyu-qu",
                ServiceArgType.ip_address.name: "ip.192.168.6.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "sdfgh-qd",
                ServiceArgType.ip_address.name: "ip.192.168.6.3",
                ServiceArgType.service_name.name: "tt1",
                ServiceArgType.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-amer-downstream",
                ServiceArgType.data_center.name: "dc.06",
                ServiceArgType.host_name.name: "sdfgb-qd",
                ServiceArgType.ip_address.name: "ip.192.168.6.4",
                ServiceArgType.service_name.name: "xx",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "qwer-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.1",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "qwer-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.1",
                ServiceArgType.service_name.name: "s_b",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "qwer-pd-3",
                ServiceArgType.ip_address.name: "ip.192.168.7.2",
                ServiceArgType.service_name.name: "s_c",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.77",
                ServiceArgType.host_name.name: "qwer-pd-2",
                ServiceArgType.ip_address.name: "ip.172.16.7.2",
                ServiceArgType.service_name.name: "s_a",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.77",
                ServiceArgType.host_name.name: "qwer-pd-2",
                ServiceArgType.ip_address.name: "ip.172.16.7.2",
                ServiceArgType.service_name.name: "s_b",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "bbb",
                    "xxx",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "upstream",
                ServiceArgType.cluster_name.name: "prod-apac-upstream",
                ServiceArgType.data_center.name: "dc.77",
                ServiceArgType.host_name.name: "qwer-pd-2",
                ServiceArgType.ip_address.name: "ip.172.16.7.2",
                ServiceArgType.service_name.name: "s_c",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.3",
                ServiceArgType.service_name.name: "tt1",
                ServiceArgType.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-1",
                ServiceArgType.ip_address.name: "ip.192.168.7.3",
                ServiceArgType.service_name.name: "tt2",
                ServiceArgType.run_mode.name: "passive",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-2",
                ServiceArgType.ip_address.name: "ip.192.168.7.4",
                ServiceArgType.service_name.name: "tt1",
                ServiceArgType.run_mode.name: "passive",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-2",
                ServiceArgType.ip_address.name: "ip.192.168.7.4",
                ServiceArgType.service_name.name: "tt2",
                ServiceArgType.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for list/array field is also possible:
                ServiceArgType.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                ServiceArgType.code_maturity.name: "prod",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "prod-apac-downstream",
                ServiceArgType.data_center.name: "dc.07",
                ServiceArgType.host_name.name: "wert-pd-2",
                ServiceArgType.ip_address.name: "ip.192.168.7.4",
                ServiceArgType.service_name.name: "xx",
                ServiceArgType.run_mode.name: "active",
                ServiceArgType.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
        ])

    def populate_TD_76_09_29_31_overlapped(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        if not self.is_test_data_allowed("TD_76_09_29_31"):
            return

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-amer-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                # TD_76_09_29_31 geo_region set overlaps with host_name set:
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-amer-downstream",
                # TD_76_09_29_31 host_name set overlaps with geo_region set:
                ServiceArgType.host_name.name: "amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-amer-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServiceArgType.host_name.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "amer",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-amer-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServiceArgType.host_name.name: "host-3-amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                # TD_76_09_29_31 geo_region set overlaps with host_name set:
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                # TD_76_09_29_31 host_name set overlaps with geo_region set:
                ServiceArgType.host_name.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServiceArgType.host_name.name: "amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServiceArgType.host_name.name: "host-3-emea",
            },
        ])

    def populate_TD_99_99_88_75_mutually_exclusive(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        if not self.is_test_data_allowed("TD_99_99_88_75"):
            return

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_99_99_88_75 # mutually exclusive: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-amer-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_99_99_88_75 # mutually exclusive: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-apac-downstream",
                ServiceArgType.host_name.name: "host-a-1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "qa",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "qa-apac-downstream",
                ServiceArgType.host_name.name: "host-a-2",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.host_name.name: "host-b-1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.host_name.name: "host-b-2",
            },
        ])

    def populate_TD_38_03_48_51_large_generated(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        """
        TD_38_03_48_51: generate large data set
        """
        if not self.is_test_data_allowed("TD_38_03_48_51"):
            return

        for code_maturity in ["cm" + str(cmn) for cmn in range(0, self.object_multiplier)]:
            for geo_region in ["gr" + str(grn) for grn in range(0, self.object_multiplier)]:
                for flow_stage in ["fs" + str(fsn) for fsn in range(0, self.object_multiplier)]:

                    cluster_name = f"{code_maturity}-{geo_region}-{flow_stage}"

                    eprint(f"loading cluster_name={cluster_name}...")

                    #####################################################################################################
                    # clusters

                    generated_cluster = {
                        envelope_payload_: {
                        },
                        test_data_: "TD_38_03_48_51",  # large generated
                        ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                        ServiceArgType.code_maturity.name: code_maturity,
                        ServiceArgType.geo_region.name: geo_region,
                        ServiceArgType.flow_stage.name: flow_stage,
                        ServiceArgType.cluster_name.name: cluster_name,
                    }

                    cluster_envelopes.append(generated_cluster)

                    for host_name in ["hs" + str(hsn) for hsn in range(0, self.object_multiplier)]:

                        ################################################################################################
                        # hosts

                        generated_host = {
                            envelope_payload_: {
                            },
                            test_data_: "TD_38_03_48_51",  # large generated
                            ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                            ServiceArgType.code_maturity.name: code_maturity,
                            ServiceArgType.geo_region.name: geo_region,
                            ServiceArgType.flow_stage.name: flow_stage,
                            ServiceArgType.cluster_name.name: cluster_name,
                            ServiceArgType.host_name.name: host_name,
                        }

                        host_envelopes.append(generated_host)

                        run_mode = "active"
                        for service_name in ["sn{:02d}".format(snn) for snn in range(0, self.object_multiplier)]:
                            ############################################################################################################
                            # services

                            generated_service = {
                                envelope_payload_: {
                                },
                                test_data_: "TD_38_03_48_51",  # large generated
                                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassService.name,
                                ServiceArgType.code_maturity.name: code_maturity,
                                ServiceArgType.geo_region.name: geo_region,
                                ServiceArgType.flow_stage.name: flow_stage,
                                ServiceArgType.cluster_name.name: cluster_name,
                                ServiceArgType.host_name.name: host_name,
                                ServiceArgType.service_name.name: service_name,
                                ServiceArgType.run_mode.name: run_mode,
                            }

                            # Even (0, 2, ...) => active
                            # Odd (1, 3, ...) => passive
                            if run_mode == "active":
                                run_mode = "passive"
                            else:
                                run_mode = "active"

                            service_envelopes.append(generated_service)

    def populate_TD_43_24_76_58_single(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        if not self.is_test_data_allowed("TD_43_24_76_58"):
            return

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_43_24_76_58 # single: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassCluster.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_43_24_76_58 # single: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.host_name.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "apac",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-apac-downstream",
                ServiceArgType.host_name.name: "asdf",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.host_name.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedArgType.EnvelopeClass.name: ServiceEnvelopeClass.ClassHost.name,
                ServiceArgType.code_maturity.name: "dev",
                ServiceArgType.geo_region.name: "emea",
                ServiceArgType.flow_stage.name: "downstream",
                ServiceArgType.cluster_name.name: "dev-emea-downstream",
                ServiceArgType.host_name.name: "asdf",
            },
        ])
