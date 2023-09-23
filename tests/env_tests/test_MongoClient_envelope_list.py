from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from env_tests.MongoClientTest import MongoClientTest


class ThisTestCase(MongoClientTest):

    def test_list_all_envelopes(self):
        """
        Does not test anything, just lists envelopes in current database collection.
        """

        col_proxy = self.create_collection_proxy(data_envelopes_)

        self.show_all_envelopes(col_proxy)
