from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoClientWrapper import get_mongo_client
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from env_tests.MongoClientTest import MongoClientTest


class ThisTestCase(MongoClientTest):

    def test_list_all_envelopes(self):
        """
        Does not test anything, just lists envelopes in current database collection:
        """

        mongo_config = mongo_config_desc.from_input_dict(mongo_config_desc.dict_example)
        mongo_client = get_mongo_client(mongo_config)
        print("list_database_names: ", mongo_client.list_database_names())

        mongo_db: Database = mongo_client[mongo_config.database_name]
        print("list_collection_names: ", mongo_db.list_collection_names())

        col_name = data_envelopes_
        col_proxy: Collection = mongo_db[col_name]

        self.show_all_envelopes(col_proxy)
