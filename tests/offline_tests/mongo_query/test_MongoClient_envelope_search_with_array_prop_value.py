from __future__ import annotations

from icecream import ic
from pymongo.collection import Collection

from argrelay_lib_server_plugin_demo.demo_service.ServicePropName import ServicePropName
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from offline_tests.mongo_query.MongoClientTestClass import (
    MongoClientTestClass,
    object_name_,
)


class ThisTestClass(MongoClientTestClass):

    # noinspection PyMethodMayBeStatic
    def test_live_envelope_searched_by_multiple_prop_name_prop_value_pairs(self):
        """
        Example with data searched by multiple { prop_name: prop_value } pairs
        where some fields contain array of values.
        See: FS_06_99_43_60 array `prop_value`
        """

        # Fields which will be indexed:
        index_props = [
            ServicePropName.access_type.name,
            ServicePropName.live_status.name,
            ServicePropName.code_maturity.name,
        ]

        envelope_001 = {
            envelope_payload_: {
                object_name_: "envelope_001",
            },
            ServicePropName.access_type.name: "ro",
        }

        envelope_002 = {
            envelope_payload_: {
                object_name_: "envelope_002",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: [
                "red",
                "blue",
            ],
        }

        envelope_003 = {
            envelope_payload_: {
                object_name_: "envelope_003",
            },
            ServicePropName.access_type.name: "rw",
            # NOTE: some of the envelopes have scalar value for the same field which has arrays in other envelopes:
            ServicePropName.live_status.name: "blue",
        }

        envelope_004 = {
            envelope_payload_: {
                object_name_: "envelope_004",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: [
                "red",
                "yellow",
            ],
            ServicePropName.code_maturity.name: "prod",
        }

        envelope_005 = {
            envelope_payload_: {
                object_name_: "envelope_005",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: [
                "blue",
                "green",
            ],
            ServicePropName.code_maturity.name: "prod",
        }

        envelope_006 = {
            envelope_payload_: {
                object_name_: "envelope_006",
            },
            ServicePropName.access_type.name: "rw",
            # NOTE: some of the envelopes have scalar value for the same field which has arrays in other envelopes:
            ServicePropName.live_status.name: "green",
            ServicePropName.code_maturity.name: "prod",
        }

        envelope_007 = {
            envelope_payload_: {
                object_name_: "envelope_007",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: [
                "red",
                "green",
                "blue",
                "yellow",
            ],
            ServicePropName.code_maturity.name: "prod",
        }

        self.col_proxy.insert_many([
            envelope_001,
            envelope_002,
            envelope_003,
            envelope_004,
            envelope_005,
            envelope_006,
            envelope_007,
        ])

        self.index_props(self.col_proxy, index_props)

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: "red",
            }),
            [
                "envelope_002",
                "envelope_004",
                "envelope_007",
            ],
        )

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: "yellow",
            }),
            [
                "envelope_004",
                "envelope_007",
            ],
        )

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: "blue",
            }),
            [
                "envelope_002",
                "envelope_003",
                "envelope_005",
                "envelope_007",
            ],
        )

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: "green",
            }),
            [
                "envelope_005",
                "envelope_006",
                "envelope_007",
            ],
        )

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: [
                    "green",
                    "blue",
                ]
            }),
            # NOTE: query with array of values does not work:
            [
            ],
        )

        self.find_and_assert(
            self.col_proxy,
            ic({
                ServicePropName.live_status.name: [
                    "green",
                    "blue",
                ]
            }),
            # NOTE: query with array of values does not work:
            [
            ],
        )

        self.remove_all_data(self.col_proxy)

    def find_and_assert(
        self,
        col_proxy: Collection,
        query_dict: dict,
        expected_object_names: list[str],
    ):
        data_envelopes = list(col_proxy.find(query_dict))
        for data_envelope in data_envelopes:
            ic(data_envelope)
        self.assertTrue(len(data_envelopes) == len(expected_object_names))
        actual_object_names = self.extract_object_names(data_envelopes)
        for expected_object_name in expected_object_names:
            self.assertTrue(expected_object_name in actual_object_names)

    @staticmethod
    def extract_object_names(
        data_envelopes: list[dict],
    ):
        return [data_envelope[envelope_payload_][object_name_] for data_envelope in data_envelopes]
