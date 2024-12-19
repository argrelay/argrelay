from __future__ import annotations

from argrelay.custom_integ.ServiceEnvelopeClass import ServiceEnvelopeClass
from argrelay.custom_integ.ServiceLoaderConfigSchema import (
    service_loader_config_desc,
    test_data_ids_to_load_,
)
from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common import eprint
from argrelay.plugin_loader.AbstractLoader import AbstractLoader
from argrelay.relay_server.QueryEngine import QueryEngine
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.IndexModel import IndexModel
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
    envelope_id_,
)
from argrelay.test_infra import test_data_


class ServiceLoader(AbstractLoader):
    object_multiplier: int = 10
    """
    Used by TD_38_03_48_51 to generate large data set.
    """

    # Quick flag to load (or not) `ServiceEnvelopeClass.class_cluster` (currently not used by anything).
    # Alternatively, a dummy function with `search_list` using it will make validation pass:
    load_class_cluster: bool = False

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

    def list_index_models(
        self,
    ) -> list[IndexModel]:

        return [
            IndexModel(
                collection_name = ServiceEnvelopeClass.class_cluster.name,
                index_props = (
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    [ReservedPropName.envelope_class.name] +
                    # TODO: TODO_89_50_17_63: fine-tune list of `index_prop`-s:
                    [e.name for e in ServicePropName]
                )
            ),
            IndexModel(
                collection_name = ServiceEnvelopeClass.class_host.name,
                index_props = (
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    [ReservedPropName.envelope_class.name] +
                    # TODO: TODO_89_50_17_63: fine-tune list of `index_prop`-s:
                    [e.name for e in ServicePropName]
                )
            ),
            IndexModel(
                collection_name = ServiceEnvelopeClass.class_service.name,
                index_props = (
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    [ReservedPropName.envelope_class.name] +
                    # TODO: TODO_89_50_17_63: fine-tune list of `index_prop`-s:
                    [e.name for e in ServicePropName]
                )
            ),
            IndexModel(
                collection_name = ServiceEnvelopeClass.class_access_type.name,
                index_props = [
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    ReservedPropName.envelope_class.name,
                    ServicePropName.access_type.name,
                ],
            ),
            IndexModel(
                collection_name = ReservedEnvelopeClass.class_help.name,
                index_props = [
                    # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                    ReservedPropName.envelope_class.name,
                    ReservedPropName.prop_name.name,
                    ReservedPropName.prop_value.name,
                    # `ReservedPropName.help_hint` is not indexed (not used in `search_control`) - instead,
                    # it is a search result:
                    # ReservedPropName.help_hint.name,
                ],
            ),
        ]

    def load_envelope_collections(
        self,
        query_engine: QueryEngine,
    ) -> list[EnvelopeCollection]:
        """
        The loader returns `data_envelope`-s populated by code (without any data source).
        """

        envelope_collections: dict[str, EnvelopeCollection] = {}

        cluster_envelopes = envelope_collections.setdefault(
            ServiceEnvelopeClass.class_cluster.name,
            EnvelopeCollection(
                collection_name = ServiceEnvelopeClass.class_cluster.name,
                data_envelopes = [],
            ),
        ).data_envelopes

        host_envelopes = envelope_collections.setdefault(
            ServiceEnvelopeClass.class_host.name,
            EnvelopeCollection(
                collection_name = ServiceEnvelopeClass.class_host.name,
                data_envelopes = [],
            ),
        ).data_envelopes

        service_envelopes = envelope_collections.setdefault(
            ServiceEnvelopeClass.class_service.name,
            EnvelopeCollection(
                collection_name = ServiceEnvelopeClass.class_service.name,
                data_envelopes = [],
            ),
        ).data_envelopes

        access_envelopes = envelope_collections.setdefault(
            ServiceEnvelopeClass.class_access_type.name,
            EnvelopeCollection(
                collection_name = ServiceEnvelopeClass.class_access_type.name,
                data_envelopes = [],
            ),
        ).data_envelopes

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
        self.populate_TD_39_25_11_76_missing_props(
            cluster_envelopes,
            host_envelopes,
            service_envelopes,
        )

        self.generate_envelope_id(cluster_envelopes + host_envelopes + service_envelopes)

        self.generate_help_hints(
            envelope_collections,
        )

        return envelope_collections.values()

    # noinspection PyMethodMayBeStatic
    def generate_envelope_id(
        self,
        data_envelopes: list[dict],
    ):
        for data_envelope in data_envelopes:
            if envelope_id_ not in data_envelope:
                if data_envelope[ReservedPropName.envelope_class.name] == ServiceEnvelopeClass.class_host.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServicePropName.cluster_name.name]
                        + "." +
                        data_envelope[ServicePropName.host_name.name]
                    )
                if data_envelope[ReservedPropName.envelope_class.name] == ServiceEnvelopeClass.class_service.name:
                    data_envelope[envelope_id_] = (
                        data_envelope[ServicePropName.cluster_name.name]
                        + "." +
                        data_envelope[ServicePropName.host_name.name]
                        + "." +
                        data_envelope[ServicePropName.service_name.name]
                        + "." +
                        data_envelope[ServicePropName.run_mode.name]
                    )

    @staticmethod
    def generate_help_hints(
        envelope_collections: dict[str, EnvelopeCollection],
    ) -> list[dict]:
        """
        This demos FS_71_87_33_52 help_hint for `ServicePropName.ip_address`.

        It simply generates `data_envelope`-s of `ReservedEnvelopeClass.class_help` for
        values of `ServicePropName.ip_address` equal to corresponding `ServicePropName.host_name`.
        """

        help_hint_envelopes = envelope_collections.setdefault(
            ReservedEnvelopeClass.class_help.name,
            EnvelopeCollection(
                collection_name = ReservedEnvelopeClass.class_help.name,
                data_envelopes = [],
            ),
        ).data_envelopes

        host_envelopes = envelope_collections[ServiceEnvelopeClass.class_host.name].data_envelopes

        # Generating `help_hint` data:
        for host_envelope in host_envelopes:
            # This `if`-filter is not necessary until non-host-class-envelopes
            # get stored into the same collection:
            if host_envelope[ReservedPropName.envelope_class.name] == ServiceEnvelopeClass.class_host.name:
                if ServicePropName.ip_address.name in host_envelope:
                    help_hint_envelopes.append({
                        f"{ReservedPropName.envelope_class.name}": f"{ReservedEnvelopeClass.class_help.name}",
                        f"{ReservedPropName.prop_name.name}": f"{ServicePropName.ip_address.name}",
                        f"{ReservedPropName.prop_value.name}": f"{host_envelope[ServicePropName.ip_address.name]}",
                        f"{ReservedPropName.help_hint.name}": f"{host_envelope[ServicePropName.host_name.name]}",
                    })

        return help_hint_envelopes

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
            # `access_type`

            {
                envelope_payload_: {
                },
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_access_type.name,
                ServicePropName.access_type.name: "ro",
            },
            {
                envelope_payload_: {
                },
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_access_type.name,
                ServicePropName.access_type.name: "rw",
            },
        ])

    def switch_loading_class_cluster(self, cluster_envelopes):
        if not self.load_class_cluster:
            # Substitute given collection by idle instance to avoid loading:
            cluster_envelopes = []
        return cluster_envelopes

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

        cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_63_37_05_36 # demo: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-emea-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-emea-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-amer-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
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
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-apac-upstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "zxcv-du",
                ServicePropName.ip_address.name: "ip.192.168.1.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.data_center.name: "dc.11",
                ServicePropName.host_name.name: "zxcv-dd",
                ServicePropName.ip_address.name: "ip.172.16.1.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "poiu-dd",
                ServicePropName.ip_address.name: "ip.192.168.1.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-emea-upstream",
                ServicePropName.data_center.name: "dc.22",
                ServicePropName.host_name.name: "asdf-du",
                ServicePropName.ip_address.name: "ip.172.16.2.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.data_center.name: "dc.02",
                ServicePropName.host_name.name: "xcvb-dd",
                ServicePropName.ip_address.name: "ip.192.168.2.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-amer-upstream",
                ServicePropName.data_center.name: "dc.03",
                ServicePropName.host_name.name: "qwer-du",
                ServicePropName.ip_address.name: "ip.192.168.3.1",
            },

            # qa

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
                ServicePropName.data_center.name: "dc.04",
                ServicePropName.host_name.name: "hjkl-qu",
                ServicePropName.ip_address.name: "ip.192.168.4.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
                ServicePropName.data_center.name: "dc.44",
                ServicePropName.host_name.name: "poiu-qu",
                ServicePropName.ip_address.name: "ip.172.16.4.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-amer-upstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "rtyu-qu",
                ServicePropName.ip_address.name: "ip.192.168.6.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-amer-upstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "rt-qu",
                ServicePropName.ip_address.name: "ip.192.168.6.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "sdfgh-qd",
                ServicePropName.ip_address.name: "ip.192.168.6.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "sdfgb-qd",
                ServicePropName.ip_address.name: "ip.192.168.6.4",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
                ServicePropName.data_center.name: "dc.66",
                ServicePropName.host_name.name: "sdfg-qd",
                ServicePropName.ip_address.name: "ip.172.16.6.5",
            },

            # prod

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "qwer-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "qwer-pd-3",
                ServicePropName.ip_address.name: "ip.192.168.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.77",
                ServicePropName.host_name.name: "qwer-pd-2",
                ServicePropName.ip_address.name: "ip.172.16.7.2",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.3",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-2",
                ServicePropName.ip_address.name: "ip.192.168.7.4",
            },
        ])

        service_envelopes.extend([
            ############################################################################################################
            # TD_63_37_05_36 # demo: services

            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-apac-upstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "zxcv-du",
                ServicePropName.ip_address.name: "ip.192.168.1.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-apac-upstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "zxcv-du",
                ServicePropName.ip_address.name: "ip.192.168.1.1",
                ServicePropName.service_name.name: "s_b",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-apac-upstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "zxcv-du",
                ServicePropName.ip_address.name: "ip.192.168.1.1",
                ServicePropName.service_name.name: "s_c",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.data_center.name: "dc.11",
                ServicePropName.host_name.name: "zxcv-dd",
                ServicePropName.ip_address.name: "ip.172.16.1.2",
                ServicePropName.service_name.name: "tt",
                ServicePropName.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.data_center.name: "dc.01",
                ServicePropName.host_name.name: "poiu-dd",
                ServicePropName.ip_address.name: "ip.192.168.1.3",
                ServicePropName.service_name.name: "xx",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-emea-upstream",
                ServicePropName.data_center.name: "dc.22",
                ServicePropName.host_name.name: "asdf-du",
                ServicePropName.ip_address.name: "ip.172.16.2.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-emea-upstream",
                ServicePropName.data_center.name: "dc.22",
                ServicePropName.host_name.name: "asdf-du",
                ServicePropName.ip_address.name: "ip.172.16.2.1",
                ServicePropName.service_name.name: "s_b",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.data_center.name: "dc.02",
                ServicePropName.host_name.name: "xcvb-dd",
                ServicePropName.ip_address.name: "ip.192.168.2.2",
                ServicePropName.service_name.name: "xx",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.data_center.name: "dc.02",
                ServicePropName.host_name.name: "xcvb-dd",
                ServicePropName.ip_address.name: "ip.192.168.2.2",
                ServicePropName.service_name.name: "zz",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "rrr",
                    "hhh",
                    "odd",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "dev-amer-upstream",
                ServicePropName.data_center.name: "dc.03",
                ServicePropName.host_name.name: "qwer-du",
                ServicePropName.ip_address.name: "ip.192.168.3.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
                ServicePropName.data_center.name: "dc.04",
                ServicePropName.host_name.name: "hjkl-qu",
                ServicePropName.ip_address.name: "ip.192.168.4.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
                ServicePropName.data_center.name: "dc.04",
                ServicePropName.host_name.name: "hjkl-qu",
                ServicePropName.ip_address.name: "ip.192.168.4.1",
                ServicePropName.service_name.name: "s_b",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-apac-upstream",
                ServicePropName.data_center.name: "dc.44",
                ServicePropName.host_name.name: "poiu-qu",
                ServicePropName.ip_address.name: "ip.172.16.4.2",
                ServicePropName.service_name.name: "s_c",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "qa-amer-upstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "rtyu-qu",
                ServicePropName.ip_address.name: "ip.192.168.6.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "sdfgh-qd",
                ServicePropName.ip_address.name: "ip.192.168.6.3",
                ServicePropName.service_name.name: "tt1",
                ServicePropName.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-amer-downstream",
                ServicePropName.data_center.name: "dc.06",
                ServicePropName.host_name.name: "sdfgb-qd",
                ServicePropName.ip_address.name: "ip.192.168.6.4",
                ServicePropName.service_name.name: "xx",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "rrr",
                    "hhh",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "qwer-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.1",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "qwer-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.1",
                ServicePropName.service_name.name: "s_b",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "bbb",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "qwer-pd-3",
                ServicePropName.ip_address.name: "ip.192.168.7.2",
                ServicePropName.service_name.name: "s_c",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.77",
                ServicePropName.host_name.name: "qwer-pd-2",
                ServicePropName.ip_address.name: "ip.172.16.7.2",
                ServicePropName.service_name.name: "s_a",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "aaa",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.77",
                ServicePropName.host_name.name: "qwer-pd-2",
                ServicePropName.ip_address.name: "ip.172.16.7.2",
                ServicePropName.service_name.name: "s_b",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "bbb",
                    "xxx",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "upstream",
                ServicePropName.cluster_name.name: "prod-apac-upstream",
                ServicePropName.data_center.name: "dc.77",
                ServicePropName.host_name.name: "qwer-pd-2",
                ServicePropName.ip_address.name: "ip.172.16.7.2",
                ServicePropName.service_name.name: "s_c",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
                    "ccc",
                    "sss",
                ],
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.3",
                ServicePropName.service_name.name: "tt1",
                ServicePropName.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-1",
                ServicePropName.ip_address.name: "ip.192.168.7.3",
                ServicePropName.service_name.name: "tt2",
                ServicePropName.run_mode.name: "passive",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-2",
                ServicePropName.ip_address.name: "ip.192.168.7.4",
                ServicePropName.service_name.name: "tt1",
                ServicePropName.run_mode.name: "passive",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-2",
                ServicePropName.ip_address.name: "ip.192.168.7.4",
                ServicePropName.service_name.name: "tt2",
                ServicePropName.run_mode.name: "active",
                # FS_06_99_43_60 providing scalar value for array `prop_name` is also possible:
                ServicePropName.group_label.name: "rrr",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_63_37_05_36",  # demo
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                ServicePropName.code_maturity.name: "prod",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "prod-apac-downstream",
                ServicePropName.data_center.name: "dc.07",
                ServicePropName.host_name.name: "wert-pd-2",
                ServicePropName.ip_address.name: "ip.192.168.7.4",
                ServicePropName.service_name.name: "xx",
                ServicePropName.run_mode.name: "active",
                ServicePropName.group_label.name: [
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

        cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-amer-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_76_09_29_31 # overlapped: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                # TD_76_09_29_31 geo_region set overlaps with host_name set:
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-amer-downstream",
                # TD_76_09_29_31 host_name set overlaps with geo_region set:
                ServicePropName.host_name.name: "amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-amer-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServicePropName.host_name.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "amer",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-amer-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServicePropName.host_name.name: "host-3-amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                # TD_76_09_29_31 geo_region set overlaps with host_name set:
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                # TD_76_09_29_31 host_name set overlaps with geo_region set:
                ServicePropName.host_name.name: "emea",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServicePropName.host_name.name: "amer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_76_09_29_31",  # overlapped
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                # host_name is intentionally matching another host_name from different geo_region (also named alike):
                ServicePropName.host_name.name: "host-3-emea",
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

        cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_99_99_88_75 # mutually exclusive: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-amer-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_99_99_88_75 # mutually exclusive: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-apac-downstream",
                ServicePropName.host_name.name: "host-a-1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "qa",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "qa-apac-downstream",
                ServicePropName.host_name.name: "host-a-2",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "host-b-1",
            },
            {
                envelope_payload_: {
                },
                test_data_: "TD_99_99_88_75",  # mutually exclusive
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "host-b-2",
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

                    cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

                    generated_cluster = {
                        envelope_payload_: {
                        },
                        test_data_: "TD_38_03_48_51",  # large generated
                        ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                        ServicePropName.code_maturity.name: code_maturity,
                        ServicePropName.geo_region.name: geo_region,
                        ServicePropName.flow_stage.name: flow_stage,
                        ServicePropName.cluster_name.name: cluster_name,
                    }

                    cluster_envelopes.append(generated_cluster)

                    for host_name in ["hs" + str(hsn) for hsn in range(0, self.object_multiplier)]:

                        ################################################################################################
                        # hosts

                        generated_host = {
                            envelope_payload_: {
                            },
                            test_data_: "TD_38_03_48_51",  # large generated
                            ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                            ServicePropName.code_maturity.name: code_maturity,
                            ServicePropName.geo_region.name: geo_region,
                            ServicePropName.flow_stage.name: flow_stage,
                            ServicePropName.cluster_name.name: cluster_name,
                            ServicePropName.host_name.name: host_name,
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
                                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_service.name,
                                ServicePropName.code_maturity.name: code_maturity,
                                ServicePropName.geo_region.name: geo_region,
                                ServicePropName.flow_stage.name: flow_stage,
                                ServicePropName.cluster_name.name: cluster_name,
                                ServicePropName.host_name.name: host_name,
                                ServicePropName.service_name.name: service_name,
                                ServicePropName.run_mode.name: run_mode,
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

        cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_43_24_76_58 # single: clusters

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
            },
        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_43_24_76_58 # single: hosts

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.host_name.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.host_name.name: "asdf",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "qwer",
            },

            {
                envelope_payload_: {
                },
                test_data_: "TD_43_24_76_58",  # single
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "asdf",
            },
        ])

    def populate_TD_39_25_11_76_missing_props(
        self,
        cluster_envelopes: list[dict],
        host_envelopes: list[dict],
        service_envelopes: list[dict],
    ):
        if not self.is_test_data_allowed("TD_39_25_11_76"):
            return

        cluster_envelopes = self.switch_loading_class_cluster(cluster_envelopes)

        cluster_envelopes.extend([

            ############################################################################################################
            # TD_39_25_11_76 # missing props: clusters

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
            },

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_cluster.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
            },

        ])

        host_envelopes.extend([

            ############################################################################################################
            # TD_39_25_11_76 # missing props: hosts

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.host_name.name: "qwer",
                ServicePropName.live_status.name: "green",
            },

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.host_name.name: "asdf",
                ServicePropName.live_status.name: "yellow",
            },

            {
                # missing `ServicePropName.live_status`:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "apac",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-apac-downstream",
                ServicePropName.host_name.name: "zxcv",
                # NOTE: `ServicePropName.live_status` for this `data_envelope` is missing only in `apac` (not in `emea`).
                # ServicePropName.live_status.name: "red",
            },

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "qwer",
                ServicePropName.live_status.name: "green",
            },

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "asdf",
                ServicePropName.live_status.name: "yellow",
            },

            {
                # nothing missing:
                envelope_payload_: {
                },
                test_data_: "TD_39_25_11_76",  # missing props
                ReservedPropName.envelope_class.name: ServiceEnvelopeClass.class_host.name,
                ServicePropName.code_maturity.name: "dev",
                ServicePropName.geo_region.name: "emea",
                ServicePropName.flow_stage.name: "downstream",
                ServicePropName.cluster_name.name: "dev-emea-downstream",
                ServicePropName.host_name.name: "zxcv",
                ServicePropName.live_status.name: "red",
            },
        ])
