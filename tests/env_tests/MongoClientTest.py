from unittest import TestCase

from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoClientWrapper import get_mongo_client
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc

object_name_ = "object_name"


class MongoClientTest(TestCase):

    @staticmethod
    def create_collection_proxy(
        col_name: str,
    ):
        # To connect to real mongo server, change this to False:
        # mongo_config_desc.dict_example[use_mongomock_only_] = False

        mongo_config = mongo_config_desc.from_input_dict(mongo_config_desc.dict_example)
        mongo_client = get_mongo_client(mongo_config)
        print("list_database_names: ", mongo_client.list_database_names())
        mongo_db: Database = mongo_client[mongo_config.mongo_server.database_name]
        print("list_collection_names: ", mongo_db.list_collection_names())

        col_proxy: Collection = mongo_db[col_name]
        return col_proxy

    @staticmethod
    def show_all_envelopes(
        col_proxy: Collection,
    ):
        print("show_all_envelopes:")
        for data_envelope in col_proxy.find():
            print("data_envelope: ", data_envelope)

    @staticmethod
    def remove_all_envelopes(
        col_proxy: Collection,
    ):
        col_proxy.delete_many({})
        col_proxy.drop_indexes()

    @staticmethod
    def index_fields(
        col_proxy: Collection,
        known_arg_types: list[str],
    ):
        for index_field in known_arg_types:
            col_proxy.create_index(index_field)
