from __future__ import annotations

from argrelay.custom_integ.ServiceArgType import ServiceArgType
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_payload_
from offline_tests.mongo_query.MongoClientTestClass import MongoClientTestClass, object_name_


class ThisTestClass(MongoClientTestClass):

    # noinspection PyMethodMayBeStatic
    def test_live_envelope_searched_by_multiple_typed_key_value_pairs(self):
        """
        Example with data searched by multiple { type: value } pairs = typical search feature `argrelay` relies on.
        """

        # Fields which will be indexed:
        index_fields = [
            ServiceArgType.access_type.name,
            ServiceArgType.live_status.name,
            ServiceArgType.code_maturity.name,
        ]

        envelope_001 = {
            envelope_payload_: {
                object_name_: "envelope_001",
            },
            ServiceArgType.access_type.name: "ro",
        }

        envelope_002 = {
            envelope_payload_: {
                object_name_: "envelope_002",
            },
            ServiceArgType.access_type.name: "rw",
            ServiceArgType.live_status.name: "red",
        }

        envelope_003 = {
            envelope_payload_: {
                object_name_: "envelope_003",
            },
            ServiceArgType.access_type.name: "rw",
            ServiceArgType.live_status.name: "blue",
        }

        envelope_004 = {
            envelope_payload_: {
                object_name_: "envelope_004",
            },
            ServiceArgType.access_type.name: "rw",
            ServiceArgType.live_status.name: "red",
            ServiceArgType.code_maturity.name: "prod",
        }

        self.col_proxy.insert_many([
            envelope_001,
            envelope_002,
            envelope_003,
            envelope_004,
        ])

        self.index_fields(self.col_proxy, index_fields)

        print("query 1:")
        for data_envelope in self.col_proxy.find(
            {
                ServiceArgType.access_type.name: "rw",
                ServiceArgType.live_status.name: "red",
            }
        ):
            print("data_envelope: ", data_envelope)

        self.remove_all_data(self.col_proxy)
