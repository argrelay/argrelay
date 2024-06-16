from __future__ import annotations

from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from offline_tests.mongo_query.MongoClientTestClass import MongoClientTestClass, object_name_


class ThisTestClass(MongoClientTestClass):

    # noinspection PyMethodMayBeStatic
    def test_live_envelope_searched_by_multiple_typed_key_value_pairs(self):
        """
        Example with data searched by multiple { type: value } pairs = typical search feature `argrelay` relies on.
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
            ServicePropName.live_status.name: "red",
        }

        envelope_003 = {
            envelope_payload_: {
                object_name_: "envelope_003",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: "blue",
        }

        envelope_004 = {
            envelope_payload_: {
                object_name_: "envelope_004",
            },
            ServicePropName.access_type.name: "rw",
            ServicePropName.live_status.name: "red",
            ServicePropName.code_maturity.name: "prod",
        }

        self.col_proxy.insert_many([
            envelope_001,
            envelope_002,
            envelope_003,
            envelope_004,
        ])

        self.index_props(self.col_proxy, index_props)

        print("query 1:")
        for data_envelope in self.col_proxy.find(
            {
                ServicePropName.access_type.name: "rw",
                ServicePropName.live_status.name: "red",
            }
        ):
            print("data_envelope: ", data_envelope)

        self.remove_all_data(self.col_proxy)
