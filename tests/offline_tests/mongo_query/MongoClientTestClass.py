from __future__ import annotations

from icecream import ic
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay_app_server.mongo_data.MongoClientWrapper import get_mongo_client
from argrelay_schema_config_server.schema_config_server_app.MongoConfigSchema import (
    mongo_config_desc,
)
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass

object_name_ = "object_name"


class MongoClientTestClass(BaseTestClass):
    """
    No `argrelay`: plain mongo test using either `pymongo` (real MongoDB) or `mongomock` (in-mem).
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super(
            MongoClientTestClass,
            self,
        ).__init__(
            *args,
            **kwargs,
        )

        self.col_name = "whatever"
        self.use_mongomock = True

    def setUp(self):
        super().setUp()
        self.col_proxy = self.select_collection_proxy(self.col_name)
        self.remove_all_data(self.col_proxy)

    def tearDown(self):
        super().tearDown()
        self.remove_all_data(self.col_proxy)

    def select_collection_proxy(
        self,
        col_name: str,
    ):
        # To connect to real mongo server, change this to False:
        # mongo_config_desc.dict_example[use_mongomock_] = False

        mongo_config = mongo_config_desc.obj_from_input_dict(
            mongo_config_desc.dict_example
        )

        # Overwrite default config example to use real MongoDB (`pymongo`) or not (`mongomock`):
        mongo_config.use_mongomock = self.use_mongomock

        mongo_client = get_mongo_client(mongo_config)
        ic(mongo_client.list_database_names())
        mongo_db: Database = mongo_client[mongo_config.mongo_server.database_name]
        ic(mongo_db.list_collection_names())

        col_proxy: Collection = mongo_db[col_name]
        return col_proxy

    @staticmethod
    def show_all_envelopes(
        col_proxy: Collection,
    ):
        print(f"show_all_envelopes [{col_proxy.name}]:")
        for data_envelope in col_proxy.find():
            print("data_envelope: ", data_envelope)

    @staticmethod
    def remove_all_data(
        col_proxy: Collection,
    ):
        col_proxy.delete_many({})
        col_proxy.drop_indexes()
        col_proxy.drop()

    @staticmethod
    def index_props(
        col_proxy: Collection,
        index_props: list[str],
    ):
        for index_prop in index_props:
            col_proxy.create_index(index_prop)
