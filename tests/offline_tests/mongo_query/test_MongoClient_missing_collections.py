from __future__ import annotations

from argrelay.custom_integ.ServicePropName import ServicePropName
from offline_tests.mongo_query.MongoClientTestClass import MongoClientTestClass


class ThisTestClass(MongoClientTestClass):

    # noinspection PyMethodMayBeStatic
    def test_querying_non_exising_collection(self):
        """
        This tests assumption that querying non-existing collections does not fail.
        """

        self.show_all_envelopes(self.col_proxy)

        print("query 1:")
        for data_envelope in self.col_proxy.find(
            {
                ServicePropName.access_type.name: "rw",
                ServicePropName.live_status.name: "red",
            }
        ):
            print("data_envelope: ", data_envelope)
