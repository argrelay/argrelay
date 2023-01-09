from unittest import TestCase, skip

from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoClientWrapper import get_mongo_client
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from argrelay.schema_config_core_server.StaticDataSchema import types_to_values_, data_envelopes_


class MongoClientTest(TestCase):

    @staticmethod
    def show_all_envelopes(col_proxy: Collection):
        print("show_all_envelopes:")
        for data_envelope in col_proxy.find():
            print("data_envelope: ", data_envelope)

    @staticmethod
    def remove_all_envelopes(col_proxy):
        col_proxy.delete_many({})
